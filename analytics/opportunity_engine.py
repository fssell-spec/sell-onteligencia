"""
Motor de oportunidades comerciais — Etapa 9.

Calcula score 0-100 por município e gera registros em commercial_opportunities
com artistas recomendados baseados em padrão histórico e proximidade geográfica.
"""
import math
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.accreditation_notice import AccreditationNotice
from app.models.artist import Artist
from app.models.commercial_opportunity import CommercialOpportunity
from app.models.enums import ContractType, OpportunityStatus, OpportunityType
from app.models.municipal_event import MunicipalEvent
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact
from app.models.public_contract import PublicContract


# Pesos do score (somam 100)
W_HISTORICO_CONTRATOS = 15   # qtd de contratos de show
W_HISTORICO_VALOR     = 20   # valor total gasto em shows
W_CONTATOS            =  8   # prefeito/secretários mapeados
W_RECORRENCIA         = 15   # eventos recorrentes identificados
W_JANELA              = 30   # urgência: evento previsto próximo
W_ANIVERSARIO         =  5   # proximidade do aniversário da cidade
W_POPULACAO           =  2   # tamanho do município
W_CREDENCIAMENTO      =  5   # edital de credenciamento ativo no PNCP


def _log_score(value: float, mid: float) -> float:
    """Score 0-1 em escala log. mid = valor que resulta em 0.5."""
    if value <= 0:
        return 0.0
    return min(math.log1p(value) / math.log1p(mid * 2), 1.0)


def _months_until(month: int, today: date) -> int:
    """Meses até a próxima ocorrência daquele mês."""
    if month == today.month:
        return 0
    diff = (month - today.month) % 12
    return diff


def score_historico_contratos(n: int) -> float:
    """0-1 baseado na quantidade de contratos de show."""
    if n == 0:
        return 0.0
    if n >= 10:
        return 1.0
    return n / 10.0


def score_historico_valor(total: float) -> float:
    """0-1 em escala log. R$500k = ~0.75."""
    return _log_score(total, 500_000)


def score_contatos(roles: set[str]) -> float:
    """0-1 baseado nos cargos mapeados."""
    pts = 0
    if "prefeito" in roles:
        pts += 40
    if "secretario_cultura" in roles:
        pts += 35
    if "secretario_turismo" in roles:
        pts += 25
    return pts / 100.0


def score_recorrencia(events: list[MunicipalEvent]) -> float:
    """0-1 baseado em quantidade e diversidade de eventos."""
    if not events:
        return 0.0
    recorrentes = sum(1 for e in events if e.recurrence_pattern == "anual")
    diversidade = len({e.event_type for e in events})
    base = min(recorrentes / 3.0, 1.0) * 0.7
    div = min(diversidade / 4.0, 1.0) * 0.3
    return base + div


def score_janela(events: list[MunicipalEvent], today: date) -> float:
    """0-1 baseado na urgência: quanto mais próximo o evento, maior o score."""
    if not events:
        return 0.0
    months = [e.usual_month for e in events if e.usual_month]
    if not months:
        return 0.0
    min_months = min(_months_until(m, today) for m in months)
    if min_months == 0:
        return 1.0
    if min_months <= 2:
        return 0.9
    if min_months <= 4:
        return 0.7
    if min_months <= 6:
        return 0.5
    return 0.2


def score_aniversario(aniversario_mes: int | None, today: date) -> float:
    """0-1 baseado na proximidade do aniversário da cidade.
    Janela ideal de abordagem: 3 a 6 meses antes.
    """
    if not aniversario_mes:
        return 0.0
    meses = _months_until(aniversario_mes, today)
    if meses == 0:
        return 0.3   # já passou este mês — score baixo
    if meses <= 2:
        return 0.7   # muito próximo — urgência alta
    if meses <= 4:
        return 1.0   # janela ideal de abordagem
    if meses <= 6:
        return 0.8   # ainda em tempo
    return 0.2       # longe demais por ora


def score_populacao(pop: int) -> float:
    """0-1 em escala log. 100k hab = ~0.75."""
    return _log_score(pop, 100_000)


def score_credenciamento(n_active: int) -> float:
    """0-1 baseado em editais de credenciamento ativos no PNCP."""
    if n_active == 0:
        return 0.0
    if n_active == 1:
        return 0.7
    if n_active == 2:
        return 0.85
    return 1.0


def build_opportunity_score(
    n_contratos: int,
    total_valor: float,
    roles: set[str],
    events: list[MunicipalEvent],
    population: int,
    today: date,
    aniversario_mes: int | None = None,
    n_credenciamentos: int = 0,
) -> dict:
    sc_hist_n = score_historico_contratos(n_contratos)
    sc_hist_v = score_historico_valor(total_valor)
    sc_cont   = score_contatos(roles)
    sc_rec    = score_recorrencia(events)
    sc_jan    = score_janela(events, today)
    sc_aniv   = score_aniversario(aniversario_mes, today)
    sc_pop    = score_populacao(population)
    sc_cred   = score_credenciamento(n_credenciamentos)

    final = (
        sc_hist_n * W_HISTORICO_CONTRATOS
        + sc_hist_v * W_HISTORICO_VALOR
        + sc_cont   * W_CONTATOS
        + sc_rec    * W_RECORRENCIA
        + sc_jan    * W_JANELA
        + sc_aniv   * W_ANIVERSARIO
        + sc_pop    * W_POPULACAO
        + sc_cred   * W_CREDENCIAMENTO
    )

    return {
        "urgency_score":           round(max(sc_jan, sc_aniv, sc_cred * 0.9), 3),
        "fit_score":               round((sc_hist_n + sc_hist_v) / 2, 3),
        "margin_potential_score":  round(sc_rec, 3),
        "aniversario_score":       round(sc_aniv, 3),
        "credenciamento_score":    round(sc_cred, 3),
        "final_opportunity_score": round(final, 1),
    }


def _next_action_text(
    roles: set[str],
    n_contratos: int,
    events: list[MunicipalEvent],
    today: date,
    n_credenciamentos: int = 0,
) -> str:
    if n_credenciamentos > 0:
        return "CREDENCIAMENTO ATIVO — entrar no edital imediatamente no PNCP."
    if n_contratos == 0:
        return "Pesquisar histórico no portal de transparência e PNCP antes de abordar."
    months = [e.usual_month for e in events if e.usual_month]
    if months:
        min_months = min(_months_until(m, today) for m in months)
        if min_months <= 2:
            return "JANELA ATIVA — abordar esta semana. Evento previsto em até 2 meses."
        if min_months <= 4:
            return "Abordar em até 2 semanas. Evento previsto em até 4 meses."
    if "secretario_cultura" in roles or "secretario_turismo" in roles:
        return "Contatar secretário para validar calendário do segundo semestre."
    if "prefeito" in roles:
        return "Contatar prefeito via gabinete para mapear agenda de eventos."
    return "Mapear decisor (sec. cultura/turismo) antes de abordar."


def recommend_artists(
    db: Session,
    municipality: Municipality,
    contracts: list[PublicContract],
    all_contracts_by_muni: dict[int, list[PublicContract]],
) -> list[dict]:
    if not contracts:
        return []

    # Padrão histórico: estilo dominante e faixa de cachê
    style_counts: dict[str, int] = defaultdict(int)
    values = [float(c.contract_value) for c in contracts if c.contract_value]
    avg_value = sum(values) / len(values) if values else 0

    for c in contracts:
        artist = db.query(Artist).filter(Artist.id == c.artist_id).first()
        if artist and artist.main_style:
            style_counts[artist.main_style] += 1

    dominant_style = max(style_counts, key=style_counts.get) if style_counts else None

    # Faixa de cachê compatível com o valor médio histórico
    if avg_value < 50_000:
        compatible_tiers = ["micro", "pequeno"]
    elif avg_value < 200_000:
        compatible_tiers = ["pequeno", "medio"]
    elif avg_value < 500_000:
        compatible_tiers = ["medio", "grande"]
    else:
        compatible_tiers = ["grande"]

    # Municípios vizinhos (mesma mesorregião)
    neighbor_muni_ids = {
        c.municipality_id
        for c_list in all_contracts_by_muni.values()
        for c in c_list
        if c.municipality_id != municipality.id
    }

    # Artistas que já atuaram na região (mesma mesorregião)
    artists_in_region: set[int] = set()
    for c_list in all_contracts_by_muni.values():
        for c in c_list:
            if c.artist_id:
                artists_in_region.add(c.artist_id)

    # Buscar artistas compatíveis
    query = db.query(Artist).filter(Artist.fee_tier.in_(compatible_tiers))
    if dominant_style:
        query = query.filter(Artist.main_style == dominant_style)

    candidates = query.limit(50).all()

    results = []
    for a in candidates:
        score = 0
        if a.id in artists_in_region:
            score += 3  # já atuou na região
        if a.fee_tier in compatible_tiers[:1]:
            score += 2  # melhor match de cachê
        if dominant_style and a.main_style == dominant_style:
            score += 2

        results.append({
            "id": a.id,
            "nome": a.name,
            "estilo": a.main_style,
            "cache_tier": a.fee_tier,
            "popularidade": a.popularity_level,
            "origem_estado": a.origin_state,
            "regiao_score": score,
            "ja_atuou_regiao": a.id in artists_in_region,
        })

    results.sort(key=lambda x: x["regiao_score"], reverse=True)
    return results[:5]


def run(db: Session) -> int:
    today = date.today()

    db.query(CommercialOpportunity).delete()
    db.flush()

    municipalities = db.query(Municipality).filter(Municipality.state == "MS").all()

    # Pré-carregar dados em memória para performance
    all_contracts = db.query(PublicContract).all()
    contracts_by_muni: dict[int, list[PublicContract]] = defaultdict(list)
    show_contracts_by_muni: dict[int, list[PublicContract]] = defaultdict(list)
    for c in all_contracts:
        if c.municipality_id:
            if (c.extracted_json or {}).get("source_type") == "estadual":
                continue
            contracts_by_muni[c.municipality_id].append(c)
            if c.contract_type == ContractType.show_artistico:
                show_contracts_by_muni[c.municipality_id].append(c)

    contacts_by_muni: dict[int, list[PublicContact]] = defaultdict(list)
    for ct in db.query(PublicContact).all():
        contacts_by_muni[ct.municipality_id].append(ct)

    # Credenciamentos ativos por município
    credenciamentos_by_muni: dict[int, int] = defaultdict(int)
    for an in db.query(AccreditationNotice).filter(AccreditationNotice.is_active == True).all():
        credenciamentos_by_muni[an.municipality_id] += 1

    events_by_muni: dict[int, list[MunicipalEvent]] = defaultdict(list)
    for ev in db.query(MunicipalEvent).all():
        events_by_muni[ev.municipality_id].append(ev)

    # Contratos por mesorregião para recomendação de artistas
    muni_mesorregiao: dict[int, str] = {m.id: (m.mesorregiao or "") for m in municipalities}
    show_contracts_by_meso: dict[str, list[PublicContract]] = defaultdict(list)
    for muni_id, c_list in show_contracts_by_muni.items():
        meso = muni_mesorregiao.get(muni_id, "")
        show_contracts_by_meso[meso].extend(c_list)

    created = 0
    for muni in municipalities:
        shows = show_contracts_by_muni[muni.id]
        roles = {ct.role for ct in contacts_by_muni[muni.id]}
        events = events_by_muni[muni.id]
        n_cred = credenciamentos_by_muni[muni.id]

        n_contratos = len(shows)
        total_valor = sum(float(c.contract_value) for c in shows if c.contract_value)

        scores = build_opportunity_score(
            n_contratos=n_contratos,
            total_valor=total_valor,
            roles=roles,
            events=events,
            population=muni.population or 0,
            today=today,
            aniversario_mes=muni.aniversario_mes,
            n_credenciamentos=n_cred,
        )

        next_action = _next_action_text(roles, n_contratos, events, today, n_cred)

        # Artistas recomendados
        meso_contracts = show_contracts_by_meso.get(muni.mesorregiao or "", [])
        recommended = recommend_artists(db, muni, shows, {muni.id: shows})

        # Data estimada do próximo evento
        est_date = None
        months = [e.usual_month for e in events if e.usual_month]
        if months:
            closest_month = min(months, key=lambda m: _months_until(m, today))
            months_ahead = _months_until(closest_month, today)
            est_date = date(
                today.year if today.month + months_ahead <= 12 else today.year + 1,
                ((today.month - 1 + months_ahead) % 12) + 1,
                1,
            )

        # Budget estimado: média dos contratos ou 0
        est_budget = round(total_valor / n_contratos, 2) if n_contratos > 0 else None

        opp = CommercialOpportunity(
            municipality_id=muni.id,
            event_id=events[0].id if events else None,
            opportunity_type=OpportunityType.venda_show,
            estimated_budget=est_budget,
            estimated_event_date=est_date,
            urgency_score=scores["urgency_score"],
            fit_score=scores["fit_score"],
            margin_potential_score=scores["margin_potential_score"],
            final_opportunity_score=scores["final_opportunity_score"],
            recommended_artists_json={
                "artistas": recommended,
                "padrao_estilo": max(
                    ({} if not shows else
                     defaultdict(int, {
                         (db.query(Artist).filter(Artist.id == c.artist_id).first() or Artist()).main_style or "outro": 1
                         for c in shows if c.artist_id
                     })),
                    key=lambda x: x if isinstance(x, int) else 0,
                    default="nao_identificado",
                ) if shows else "nao_identificado",
                "valor_medio_historico": round(total_valor / n_contratos, 0) if n_contratos else 0,
                "n_shows_historico": n_contratos,
                "n_credenciamentos_ativos": n_cred,
            },
            suggested_next_action=next_action,
            status=OpportunityStatus.novo,
        )
        db.add(opp)
        created += 1

    db.commit()
    return created
