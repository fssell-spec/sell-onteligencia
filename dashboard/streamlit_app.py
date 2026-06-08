import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact
from app.models.diario_oficial_hit import DiarioOficialHit

# Coordenadas aproximadas dos 79 municípios do MS (lat, lon)
COORDS: dict[str, tuple[float, float]] = {
    "5000203": (-20.45, -52.87),  # Água Clara
    "5000252": (-18.32, -53.71),  # Alcinópolis
    "5000609": (-23.11, -55.22),  # Amambai
    "5000708": (-20.48, -55.81),  # Anastácio
    "5000807": (-22.17, -52.72),  # Anaurilândia
    "5000856": (-22.15, -53.75),  # Angélica
    "5000906": (-22.19, -55.94),  # Antônio João
    "5001004": (-20.09, -51.09),  # Aparecida do Taboado
    "5001102": (-20.47, -55.79),  # Aquidauana
    "5001243": (-22.94, -55.64),  # Aral Moreira
    "5001508": (-19.92, -54.36),  # Bandeirantes
    "5001904": (-21.72, -52.42),  # Bataguassu
    "5002001": (-22.30, -53.27),  # Batayporã
    "5002100": (-22.11, -56.52),  # Bela Vista
    "5002159": (-20.54, -56.71),  # Bodoquena
    "5002209": (-21.13, -56.48),  # Bonito
    "5002308": (-21.26, -52.03),  # Brasilândia
    "5002407": (-22.63, -54.82),  # Caarapó
    "5002605": (-19.53, -54.05),  # Camapuã
    "5002704": (-20.47, -54.62),  # Campo Grande
    "5002803": (-22.01, -57.02),  # Caracol
    "5002902": (-19.12, -51.73),  # Cassilândia
    "5002951": (-18.79, -52.63),  # Chapadão do Sul
    "5003007": (-20.11, -54.83),  # Corguinho
    "5003056": (-23.27, -55.52),  # Coronel Sapucaia
    "5003108": (-19.01, -57.65),  # Corumbá
    "5003157": (-18.54, -53.13),  # Costa Rica
    "5003207": (-18.51, -54.76),  # Coxim
    "5003256": (-22.28, -54.17),  # Deodápolis
    "5003306": (-20.69, -55.30),  # Dois Irmãos do Buriti
    "5003454": (-22.04, -54.61),  # Douradina
    "5003504": (-22.22, -54.81),  # Dourados
    "5003702": (-23.78, -54.28),  # Eldorado
    "5003751": (-22.46, -54.54),  # Fátima do Sul
    "5003801": (-19.37, -53.64),  # Figueirão
    "5003900": (-22.41, -54.23),  # Glória de Dourados
    "5004007": (-21.46, -56.11),  # Guia Lopes da Laguna
    "5004106": (-23.67, -54.56),  # Iguatemi
    "5004304": (-19.73, -51.93),  # Inocência
    "5004403": (-22.09, -54.79),  # Itaporã
    "5004502": (-23.47, -54.19),  # Itaquiraí
    "5004601": (-22.31, -53.82),  # Ivinhema
    "5004700": (-23.88, -54.41),  # Japorã
    "5004809": (-20.15, -54.41),  # Jaraguari
    "5004908": (-21.48, -56.13),  # Jardim
    "5005004": (-22.48, -53.98),  # Jateí
    "5005103": (-22.86, -54.61),  # Juti
    "5005202": (-19.01, -57.60),  # Ladário
    "5005251": (-22.53, -55.18),  # Laguna Carapã
    "5005400": (-21.61, -55.17),  # Maracaju
    "5005459": (-20.24, -56.38),  # Miranda
    "5005507": (-23.94, -54.28),  # Mundo Novo
    "5005681": (-23.06, -54.19),  # Naviraí
    "5005707": (-21.14, -55.83),  # Nioaque
    "5005806": (-21.74, -54.36),  # Nova Alvorada do Sul
    "5005905": (-21.90, -53.34),  # Nova Andradina
    "5006002": (-22.67, -53.86),  # Novo Horizonte do Sul
    "5006200": (-18.93, -51.19),  # Paranaíba
    "5006259": (-23.89, -55.43),  # Paranhos
    "5006309": (-18.10, -54.55),  # Pedro Gomes
    "5006358": (-22.54, -55.73),  # Ponta Porã
    "5006408": (-21.70, -57.88),  # Porto Murtinho
    "5006606": (-20.44, -53.76),  # Ribas do Rio Pardo
    "5006903": (-21.80, -54.54),  # Rio Brilhante
    "5007000": (-19.45, -55.13),  # Rio Negro
    "5007109": (-18.92, -54.83),  # Rio Verde de Mato Grosso
    "5007208": (-19.97, -54.89),  # Rochedo
    "5007307": (-21.30, -52.82),  # Santa Rita do Pardo
    "5007406": (-19.39, -54.56),  # São Gabriel do Oeste
    "5007695": (-20.37, -51.42),  # Selvíria
    "5007802": (-23.97, -55.04),  # Sete Quedas
    "5007901": (-20.93, -54.97),  # Sidrolândia
    "5007952": (-17.57, -54.75),  # Sonora
    "5008008": (-23.76, -55.01),  # Sul Brasil
    "5008107": (-23.63, -55.01),  # Tacuru
    "5008206": (-22.50, -53.35),  # Taquarussu
    "5007958": (-20.44, -54.86),  # Terenos
    "5008305": (-20.79, -51.68),  # Três Lagoas
    "5008404": (-22.41, -54.44),  # Vicentina
}

CARGO_LABELS = {
    "prefeito": "Prefeito",
    "secretario_cultura": "Secretário de Cultura",
    "secretario_turismo": "Secretário de Turismo",
}

PORTE_ORDER = ["Capital", "Grande (100k–1M)", "Médio (20k–100k)", "Pequeno (<20k)"]
MESO_CORES = {
    "Centro-Norte de Mato Grosso do Sul": "#4e79a7",
    "Centro-Sul de Mato Grosso do Sul":   "#f28e2b",
    "Leste de Mato Grosso do Sul":        "#e15759",
    "Pantanais Sul-Mato-Grossenses":      "#76b7b2",
    "Sudeste de Mato Grosso do Sul":      "#59a14f",
    "Sudoeste de Mato Grosso do Sul":     "#edc948",
}


def classifica_porte(pop: int) -> str:
    if pop >= 500_000:
        return "Capital"
    if pop >= 100_000:
        return "Grande (100k–1M)"
    if pop >= 20_000:
        return "Médio (20k–100k)"
    return "Pequeno (<20k)"


@st.cache_data(ttl=300)
def load_municipios() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(Municipality).order_by(Municipality.name).all()
        records = []
        for m in rows:
            lat, lon = COORDS.get(m.ibge_code, (None, None))
            records.append(
                {
                    "nome": m.name,
                    "ibge_code": m.ibge_code,
                    "populacao": m.population or 0,
                    "area_km2": m.area_km2 or 0.0,
                    "mesorregiao": m.mesorregiao or "",
                    "microrregiao": m.microrregiao or "",
                    "lat": lat,
                    "lon": lon,
                    "aniversario_mes": m.aniversario_mes,
                    "aniversario_dia": m.aniversario_dia,
                }
            )
        df = pd.DataFrame(records)
        df["porte"] = df["populacao"].apply(classifica_porte)
        df["densidade"] = (df["populacao"] / df["area_km2"]).round(1)
        return df
    finally:
        db.close()


TIPO_LABELS = {
    "show_artistico": "Show Artístico",
    "rodeio_completo": "Rodeio Completo",
    "estrutura_evento": "Estrutura",
    "som_luz": "Som/Luz",
    "seguranca": "Segurança",
    "gerador": "Gerador",
    "arquibancada": "Arquibancada",
    "arena": "Arena",
    "producao": "Produção",
    "banheiro_quimico": "Banheiro Químico",
    "portaria": "Portaria",
    "alimentacao": "Alimentação",
    "limpeza": "Limpeza",
    "outro": "Outro",
}


@st.cache_data(ttl=300)
def load_contracts_db() -> pd.DataFrame:
    from app.models.public_contract import PublicContract
    db = SessionLocal()
    try:
        rows = (
            db.query(PublicContract, Municipality)
            .outerjoin(Municipality, PublicContract.municipality_id == Municipality.id)
            .order_by(PublicContract.publication_date.desc())
            .all()
        )
        records = []
        for c, m in rows:
            llm = (c.extracted_json or {}).get("llm_extracted", {})
            records.append({
                "municipio": m.name if m else "—",
                "mesorregiao": m.mesorregiao if m else "",
                "tipo": c.contract_type.value if c.contract_type else "",
                "modalidade": c.procurement_modality.value if c.procurement_modality else "",
                "fornecedor": c.supplier_name or "",
                "valor": float(c.contract_value) if c.contract_value else 0.0,
                "evento_nome": llm.get("event_name") or "",
                "data_pub": c.publication_date,
                "data_evento": c.event_date,
                "objeto": (c.object_description or "")[:120],
                "source_url": c.source_url or "",
            })
        df = pd.DataFrame(records)
        if not df.empty:
            df["ano"] = pd.to_datetime(df["data_pub"], errors="coerce").dt.year.fillna(0).astype(int)
        return df
    finally:
        db.close()


FEE_TIER_LABELS = {
    "micro":    "Micro (<50k)",
    "pequeno":  "Pequeno (50k–200k)",
    "medio":    "Médio (200k–500k)",
    "grande":   "Grande (>500k)",
}
FEE_TIER_ORDER = ["micro", "pequeno", "medio", "grande"]

STYLE_LABELS = {
    "sertanejo":    "Sertanejo",
    "forro":        "Forró",
    "gospel":       "Gospel",
    "samba_pagode": "Samba/Pagode",
    "outro":        "Outro",
}

POP_LABELS = {
    "local":        "Local",
    "estadual":     "Estadual",
    "nacional":     "Nacional",
    "nacional_top": "Nacional Top",
}

SUPPLIER_CAT_LABELS = {
    "arena":           "Arena",
    "arquibancada":    "Arquibancada/Palco",
    "banheiro_quimico":"Banheiro Químico",
    "seguranca":       "Segurança",
    "brigadista":      "Brigadista",
    "som":             "Som",
    "luz":             "Luz",
    "led":             "LED",
    "gerador":         "Gerador",
    "portaria":        "Portaria",
    "alimentacao":     "Alimentação",
    "limpeza":         "Limpeza",
    "producao":        "Produção",
    "outro":           "Outro",
}

EVENT_SIZE_LABELS = {
    "pequeno": "Pequeno (ate 2.000 pax)",
    "medio":   "Medio (2.000-8.000 pax)",
    "grande":  "Grande (8.000-20.000 pax)",
    "mega":    "Mega (20.000+ pax)",
}


@st.cache_data(ttl=120)
def load_artists() -> pd.DataFrame:
    from sqlalchemy import text
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                a.id,
                a.name,
                a.main_style,
                a.sub_style,
                a.fee_tier,
                a.popularity_level,
                a.origin_city,
                a.origin_state,
                a.booking_office,
                COUNT(aca.id)                               AS n_aparicoes,
                COALESCE(SUM(aca.cache_value), 0)           AS valor_total,
                MAX(aca.cache_value)                        AS cache_max,
                COUNT(DISTINCT aca.municipality_id)         AS n_municipios,
                STRING_AGG(DISTINCT m.name, ', '
                           ORDER BY m.name)                 AS municipios,
                MAX(COALESCE(aca.event_date,
                             aca.publication_date::date))    AS ultima_atividade
            FROM artists a
            LEFT JOIN artist_contract_appearances aca ON aca.artist_id = a.id
            LEFT JOIN municipalities m ON aca.municipality_id = m.id
            GROUP BY a.id, a.name, a.main_style, a.sub_style, a.fee_tier,
                     a.popularity_level, a.origin_city, a.origin_state, a.booking_office
            ORDER BY n_aparicoes DESC, a.name
        """)).fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "nome":             r[1],
            "estilo":           r[2] or "",
            "sub_estilo":       r[3] or "",
            "cache":            r[4] or "",
            "popularidade":     r[5] or "",
            "origem_cidade":    r[6] or "",
            "origem_estado":    r[7] or "",
            "escritorio":       r[8] or "",
            "contratos":        int(r[9]),
            "valor_total":      float(r[10]),
            "cache_max":        float(r[11]) if r[11] else 0.0,
            "n_municipios":     int(r[12]),
            "municipios":       r[13] or "",
            "ultima_atividade": r[14],
        } for r in rows])
    finally:
        db.close()


@st.cache_data(ttl=300)
def load_artist_contracts_detail() -> pd.DataFrame:
    """Aparições de artistas em contratos (PNCP) e diários oficiais (DOE/DIOGRANDE)."""
    from sqlalchemy import text
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                a.name                                          AS artista,
                a.main_style                                    AS estilo,
                a.fee_tier                                      AS tier,
                COALESCE(m.name, '(sem município)')             AS municipio,
                COALESCE(m.mesorregiao, '')                     AS mesorregiao,
                aca.source,
                aca.cache_value,
                aca.event_date,
                aca.publication_date,
                aca.raw_artist_name,
                aca.match_confidence,
                CASE
                    WHEN aca.source = 'pncp' THEN pc.object_description
                    ELSE doh.highlight
                END                                             AS descricao
            FROM artist_contract_appearances aca
            JOIN artists a ON aca.artist_id = a.id
            LEFT JOIN municipalities m ON aca.municipality_id = m.id
            LEFT JOIN public_contracts pc
                ON aca.source = 'pncp' AND aca.source_ref_id = pc.id
            LEFT JOIN diario_oficial_hits doh
                ON aca.source IN ('doe', 'diogrande') AND aca.source_ref_id = doh.id
            ORDER BY COALESCE(aca.event_date, aca.publication_date::date) DESC NULLS LAST,
                     aca.cache_value DESC NULLS LAST
        """)).fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "artista":       r[0],
            "estilo":        r[1] or "",
            "tier":          r[2] or "",
            "municipio":     r[3],
            "mesorregiao":   r[4],
            "fonte":         r[5],
            "cache_real":    float(r[6]) if r[6] else None,
            "data_show":     r[7],
            "data_contrato": r[8],
            "nome_raw":      r[9] or "",
            "confianca":     float(r[10]) if r[10] else 1.0,
            "descricao":     str(r[11])[:120] if r[11] else "",
        } for r in rows])
    finally:
        db.close()


@st.cache_data(ttl=300)
def load_doe_artist_activity() -> pd.DataFrame:
    """Artistas mais citados no DOE/MS e DIOGRANDE — sinal de contratação ativa."""
    from sqlalchemy import text
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                artista_detectado,
                COUNT(*)                     AS hits,
                COUNT(DISTINCT arquivo)      AS edicoes,
                MAX(data_publicacao)         AS ultimo,
                COUNT(DISTINCT municipio_id) AS n_municipios
            FROM diario_oficial_hits
            WHERE artista_detectado IS NOT NULL
              AND artista_detectado NOT ILIKE '%show%'
              AND artista_detectado NOT ILIKE '%apresentacao%'
              AND artista_detectado NOT ILIKE '%artis%'
              AND artista_detectado NOT ILIKE '%projeto%'
              AND artista_detectado NOT ILIKE '%acoes%'
              AND artista_detectado NOT ILIKE '%contrat%'
              AND LENGTH(artista_detectado) > 5
            GROUP BY artista_detectado
            ORDER BY hits DESC
            LIMIT 60
        """)).fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "artista":      r[0],
            "hits_doe":     int(r[1]),
            "edicoes":      int(r[2]),
            "ultimo":       r[3],
            "n_municipios": int(r[4]),
        } for r in rows])
    finally:
        db.close()


@st.cache_data(ttl=120)
def load_suppliers() -> pd.DataFrame:
    from app.models.supplier import Supplier
    from app.models.supplier_price import SupplierPrice
    db = SessionLocal()
    try:
        suppliers = db.query(Supplier).order_by(Supplier.category, Supplier.name).all()
        records = []
        for s in suppliers:
            avg_prices = [float(p.avg_price) for p in s.prices if p.avg_price]
            records.append({
                "nome": s.name,
                "categoria": s.category.value if s.category else "",
                "cidade": s.city or "",
                "estado": s.state or "",
                "regiao": s.service_region or "",
                "contato": s.contact_name or "",
                "telefone": s.phone or "",
                "email": s.email or "",
                "notas": s.notes or "",
                "n_precos": len(s.prices),
                "preco_min_avg": min(avg_prices) if avg_prices else 0.0,
                "preco_max_avg": max(avg_prices) if avg_prices else 0.0,
            })
        return pd.DataFrame(records)
    finally:
        db.close()


@st.cache_data(ttl=300)
def load_rodeo_templates() -> pd.DataFrame:
    from app.models.rodeo_budget_template import RodeoBudgetTemplate
    db = SessionLocal()
    try:
        templates = db.query(RodeoBudgetTemplate).order_by(
            RodeoBudgetTemplate.expected_audience
        ).all()
        records = []
        for t in templates:
            items = t.required_items_json or {}
            totais = items.get("_totais", {})
            meta = items.get("_meta", {})
            records.append({
                "nome": t.name,
                "porte": t.event_size,
                "publico": t.expected_audience or 0,
                "dias": t.duration_days or 0,
                "total_min": totais.get("min", 0),
                "total_avg": totais.get("avg", 0),
                "total_max": totais.get("max", 0),
                "descricao": meta.get("descricao", ""),
                "itens_json": items,
            })
        return pd.DataFrame(records)
    finally:
        db.close()


@st.cache_data(ttl=60)
def load_contacts() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = (
            db.query(PublicContact, Municipality)
            .join(Municipality, PublicContact.municipality_id == Municipality.id)
            .filter(Municipality.state == "MS")
            .order_by(Municipality.population.desc(), PublicContact.role)
            .all()
        )
        records = []
        for c, m in rows:
            records.append({
                "municipio": m.name,
                "mesorregiao": m.mesorregiao or "",
                "populacao": m.population or 0,
                "nome": c.name or "",
                "cargo": c.role or "",
                "partido": c.party or "",
                "telefone": c.phone or "",
                "email": c.email or "",
                "instagram": c.instagram_url or "",
                "facebook": c.facebook_url or "",
                "confidence": c.confidence_score or 0.0,
            })
        return pd.DataFrame(records)
    finally:
        db.close()


# ── Layout ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SELL INTELIGÊNCIA",
    page_icon="🎪",
    layout="wide",
)

st.title("🎪 SELL INTELIGÊNCIA")
st.caption("Sistema de Inteligência Comercial — Mato Grosso do Sul")

df = load_municipios()

if df.empty:
    st.error("Banco de dados vazio. Execute `python scripts/seed_municipios.py` e recarregue.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")

    mesorregioes_disponiveis = sorted(df["mesorregiao"].unique())
    sel_meso = st.multiselect(
        "Mesorregião",
        mesorregioes_disponiveis,
        default=mesorregioes_disponiveis,
    )

    portes_disponiveis = [p for p in PORTE_ORDER if p in df["porte"].values]
    sel_porte = st.multiselect(
        "Porte",
        portes_disponiveis,
        default=portes_disponiveis,
    )

    pop_min, pop_max = int(df["populacao"].min()), int(df["populacao"].max())
    sel_pop = st.slider(
        "População (hab.)",
        pop_min,
        pop_max,
        (pop_min, pop_max),
        step=1000,
        format="%d",
    )

    st.caption(f"Total no banco: {len(df)} municípios")

# ── Filtro aplicado ───────────────────────────────────────────────────────────

filtrado = df[
    df["mesorregiao"].isin(sel_meso)
    & df["porte"].isin(sel_porte)
    & df["populacao"].between(sel_pop[0], sel_pop[1])
].copy()

# ── KPIs ──────────────────────────────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)

pop_total = filtrado["populacao"].sum()
maior = filtrado.nlargest(1, "populacao")

with k1:
    st.metric("Municípios", len(filtrado))
with k2:
    st.metric("População Total", f"{pop_total:,.0f}".replace(",", "."))
with k3:
    st.metric("Mesorregiões", filtrado["mesorregiao"].nunique())
with k4:
    st.metric("Maior Município", maior["nome"].values[0] if len(maior) else "—")
with k5:
    area_total = filtrado["area_km2"].sum()
    st.metric("Área Total (km²)", f"{area_total:,.0f}".replace(",", "."))

st.divider()

# ── Abas ──────────────────────────────────────────────────────────────────────

tab_mapa, tab_graficos, tab_tabela, tab_contatos, tab_contratos, tab_artistas, tab_fornecedores, tab_opp, tab_rel = st.tabs(
    ["Mapa", "Distribuição", "Municípios", "Contatos", "Contratos", "Artistas", "Fornecedores", "Oportunidades", "Relatórios"]
)

# ── TAB 1: MAPA ───────────────────────────────────────────────────────────────

with tab_mapa:
    mapa_df = filtrado.dropna(subset=["lat", "lon"]).copy()
    mapa_df["pop_fmt"] = mapa_df["populacao"].apply(lambda x: f"{x:,}".replace(",", "."))

    if mapa_df.empty:
        st.info("Nenhum município no filtro atual.")
    else:
        fig_mapa = px.scatter_mapbox(
            mapa_df,
            lat="lat",
            lon="lon",
            size="populacao",
            size_max=40,
            color="mesorregiao",
            color_discrete_map=MESO_CORES,
            hover_name="nome",
            hover_data={
                "lat": False,
                "lon": False,
                "populacao": False,
                "pop_fmt": True,
                "mesorregiao": True,
                "microrregiao": True,
                "area_km2": True,
                "porte": True,
            },
            labels={
                "pop_fmt": "População",
                "mesorregiao": "Mesorregião",
                "microrregiao": "Microrregião",
                "area_km2": "Área (km²)",
                "porte": "Porte",
            },
            mapbox_style="open-street-map",
            zoom=5.5,
            center={"lat": -20.5, "lon": -54.5},
            height=580,
            title=f"79 Municípios do MS — {len(mapa_df)} exibidos",
        )
        fig_mapa.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            legend_title_text="Mesorregião",
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

# ── TAB 2: DISTRIBUIÇÃO ───────────────────────────────────────────────────────

with tab_graficos:
    col_a, col_b = st.columns(2)

    with col_a:
        meso_pop = (
            filtrado.groupby("mesorregiao")["populacao"]
            .sum()
            .reset_index()
            .sort_values("populacao")
        )
        meso_pop["pop_fmt"] = meso_pop["populacao"].apply(
            lambda x: f"{x:,}".replace(",", ".")
        )
        fig_meso = px.bar(
            meso_pop,
            x="populacao",
            y="mesorregiao",
            orientation="h",
            color="mesorregiao",
            color_discrete_map=MESO_CORES,
            text="pop_fmt",
            title="População por Mesorregião",
            labels={"populacao": "População", "mesorregiao": ""},
            height=380,
        )
        fig_meso.update_traces(textposition="outside")
        fig_meso.update_layout(showlegend=False, margin={"t": 50})
        st.plotly_chart(fig_meso, use_container_width=True)

    with col_b:
        meso_count = (
            filtrado.groupby("mesorregiao")
            .size()
            .reset_index(name="total")
            .sort_values("total")
        )
        fig_count = px.bar(
            meso_count,
            x="total",
            y="mesorregiao",
            orientation="h",
            color="mesorregiao",
            color_discrete_map=MESO_CORES,
            text="total",
            title="Quantidade de Municípios por Mesorregião",
            labels={"total": "Municípios", "mesorregiao": ""},
            height=380,
        )
        fig_count.update_traces(textposition="outside")
        fig_count.update_layout(showlegend=False, margin={"t": 50})
        st.plotly_chart(fig_count, use_container_width=True)

    st.subheader("Top 15 Municípios por População")
    top15 = filtrado.nlargest(15, "populacao").sort_values("populacao")
    top15["pop_fmt"] = top15["populacao"].apply(lambda x: f"{x:,}".replace(",", "."))
    fig_top = px.bar(
        top15,
        x="populacao",
        y="nome",
        orientation="h",
        color="mesorregiao",
        color_discrete_map=MESO_CORES,
        text="pop_fmt",
        labels={"populacao": "População", "nome": "", "mesorregiao": "Mesorregião"},
        height=480,
    )
    fig_top.update_traces(textposition="outside")
    fig_top.update_layout(margin={"t": 20})
    st.plotly_chart(fig_top, use_container_width=True)

# ── TAB 3: TABELA ─────────────────────────────────────────────────────────────

with tab_tabela:
    busca = st.text_input("Buscar município", placeholder="Digite o nome...")

    exibir = filtrado.copy()
    if busca:
        exibir = exibir[exibir["nome"].str.contains(busca, case=False, na=False)]

    _MESES = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
    }

    def _fmt_aniv(row) -> str:
        mes, dia = row.get("aniversario_mes"), row.get("aniversario_dia")
        if mes and dia:
            return f"{int(dia):02d}/{_MESES[int(mes)]}"
        return ""

    exibir2 = exibir.copy()
    exibir2["aniversario"] = exibir2.apply(_fmt_aniv, axis=1)

    exibir_fmt = exibir2[
        ["nome", "ibge_code", "populacao", "area_km2", "densidade", "mesorregiao", "microrregiao", "porte", "aniversario"]
    ].rename(
        columns={
            "nome": "Município",
            "ibge_code": "Cód. IBGE",
            "populacao": "População",
            "area_km2": "Área (km²)",
            "densidade": "Dens. (hab/km²)",
            "mesorregiao": "Mesorregião",
            "microrregiao": "Microrregião",
            "porte": "Porte",
            "aniversario": "Aniversário",
        }
    )

    st.caption(f"{len(exibir_fmt)} municípios exibidos — clique em uma linha para ver artistas e contratos")
    _exibir_fmt_r = exibir_fmt.reset_index(drop=True)
    _muni_sel_ev = st.dataframe(
        _exibir_fmt_r,
        use_container_width=True,
        height=520,
        on_select="rerun",
        selection_mode="single-row",
        key="muni_table_sel",
        column_config={
            "População": st.column_config.NumberColumn(format="%d"),
            "Área (km²)": st.column_config.NumberColumn(format="%.0f"),
            "Dens. (hab/km²)": st.column_config.NumberColumn(format="%.1f"),
        },
    )

    if _muni_sel_ev.selection.rows:
        _m_idx = _muni_sel_ev.selection.rows[0]
        _m_nome = _exibir_fmt_r.iloc[_m_idx]["Município"]
        _df_muni_detail = load_artist_contracts_detail()
        _det_muni = _df_muni_detail[_df_muni_detail["municipio"] == _m_nome].copy()
        with st.container(border=True):
            st.markdown(f"#### {_m_nome} — Artistas e Contratos")
            if _det_muni.empty:
                st.info("Nenhuma aparição de artista registrada para este município.")
            else:
                _FONTE_LM = {"pncp": "PNCP", "doe": "DOE/MS", "diogrande": "DIOGRANDE"}
                _det_muni["Fonte"] = _det_muni["fonte"].map(_FONTE_LM).fillna(_det_muni["fonte"])
                _mc1, _mc2, _mc3 = st.columns(3)
                _mc1.metric("Aparições", len(_det_muni))
                _mc2.metric("Artistas únicos", _det_muni["artista"].nunique())
                _com_val_m = _det_muni["cache_real"].notna()
                _mc3.metric(
                    "Valor total",
                    f"R$ {_det_muni.loc[_com_val_m, 'cache_real'].sum():,.0f}".replace(",", ".")
                    if _com_val_m.any() else "—",
                )
                st.dataframe(
                    _det_muni[["artista", "Fonte", "cache_real", "data_show", "data_contrato", "descricao"]].rename(columns={
                        "artista": "Artista",
                        "cache_real": "Cachê (R$)",
                        "data_show": "Data Show",
                        "data_contrato": "Data Publ.",
                        "descricao": "Trecho",
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=280,
                    column_config={"Cachê (R$)": st.column_config.NumberColumn(format="R$ %.0f")},
                )

    csv = exibir_fmt.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "Exportar CSV",
        data=csv,
        file_name="municipios_ms.csv",
        mime="text/csv",
    )

# ── TAB 4: CONTATOS ───────────────────────────────────────────────────────────

with tab_contatos:
    df_c = load_contacts()

    if df_c.empty:
        st.info("Nenhum contato cadastrado ainda.")
        st.stop()

    # KPIs de cobertura
    total_mun = 80
    kc1, kc2, kc3, kc4 = st.columns(4)
    cargo_counts = df_c.groupby("cargo")["municipio"].nunique()

    with kc1:
        n = cargo_counts.get("prefeito", 0)
        st.metric("Prefeitos", f"{n}/{total_mun}")
    with kc2:
        n = cargo_counts.get("secretario_cultura", 0)
        st.metric("Sec. Cultura", f"{n}/{total_mun}")
    with kc3:
        n = cargo_counts.get("secretario_turismo", 0)
        st.metric("Sec. Turismo", f"{n}/{total_mun}")
    with kc4:
        com_email = (df_c["email"] != "").sum()
        com_ig = (df_c["instagram"] != "").sum()
        st.metric("Com e-mail / Instagram", f"{com_email} / {com_ig}")

    st.divider()

    # Filtros da aba
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        cargo_opts = ["Todos"] + list(CARGO_LABELS.keys())
        cargo_sel = st.selectbox(
            "Cargo",
            cargo_opts,
            format_func=lambda x: CARGO_LABELS.get(x, x),
        )
    with fc2:
        meso_opts = ["Todas"] + sorted(df_c["mesorregiao"].unique().tolist())
        meso_sel = st.selectbox("Mesorregião", meso_opts, key="meso_contatos")
    with fc3:
        busca_c = st.text_input("Buscar por nome ou município", placeholder="Digite...", key="busca_contatos")

    # Aplicar filtros
    exibir_c = df_c.copy()
    if cargo_sel != "Todos":
        exibir_c = exibir_c[exibir_c["cargo"] == cargo_sel]
    if meso_sel != "Todas":
        exibir_c = exibir_c[exibir_c["mesorregiao"] == meso_sel]
    if busca_c:
        mask = (
            exibir_c["nome"].str.contains(busca_c, case=False, na=False)
            | exibir_c["municipio"].str.contains(busca_c, case=False, na=False)
        )
        exibir_c = exibir_c[mask]

    exibir_c = exibir_c.copy()
    exibir_c["cargo_label"] = exibir_c["cargo"].map(CARGO_LABELS).fillna(exibir_c["cargo"])

    show_c = exibir_c[
        ["municipio", "cargo_label", "nome", "partido", "telefone", "email", "instagram", "facebook", "confidence"]
    ].rename(
        columns={
            "municipio": "Município",
            "cargo_label": "Cargo",
            "nome": "Nome",
            "partido": "Partido",
            "telefone": "Telefone",
            "email": "E-mail",
            "instagram": "Instagram",
            "facebook": "Facebook",
            "confidence": "Conf.",
        }
    )

    st.caption(f"{len(show_c)} contatos exibidos")
    st.dataframe(
        show_c,
        use_container_width=True,
        height=560,
        column_config={
            "Conf.": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Instagram": st.column_config.LinkColumn(display_text="ver"),
            "Facebook": st.column_config.LinkColumn(display_text="ver"),
        },
    )

    csv_c = show_c.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "Exportar CSV",
        data=csv_c,
        file_name="contatos_ms.csv",
        mime="text/csv",
        key="export_contatos",
    )

# ── TAB 5: CONTRATOS ──────────────────────────────────────────────────────────

with tab_contratos:
    df_k = load_contracts_db()

    if df_k.empty:
        st.info("Nenhum contrato no banco. Execute os crawlers PNCP.")
        st.stop()

    # KPIs
    kk1, kk2, kk3, kk4 = st.columns(4)
    with kk1:
        st.metric("Contratos", f"{len(df_k):,}".replace(",", "."))
    with kk2:
        valor_total = df_k["valor"].sum()
        st.metric("Valor Total", f"R$ {valor_total:,.0f}".replace(",", "."))
    with kk3:
        shows = (df_k["tipo"] == "show_artistico").sum()
        st.metric("Shows Artísticos", shows)
    with kk4:
        muns_c = df_k[df_k["municipio"] != "—"]["municipio"].nunique()
        st.metric("Municípios", muns_c)

    with st.expander("O que significa cada modalidade?"):
        st.markdown(
            """
| Modalidade | O que é | Relevância para shows |
|---|---|---|
| **Inexigibilidade** | Contratação direta sem licitação — usada quando só existe um fornecedor possível (ex: artista exclusivo). | Alta — a maioria dos shows é contratada assim |
| **Dispensa** | Contratação direta por valor baixo ou urgência, sem licitação formal. | Média — shows menores ou emergências |
| **Pregão** | Licitação competitiva onde vence o menor preço. | Baixa — raro para shows, mais comum para estrutura/som |
| **Concorrência** | Licitação pública ampla para contratos de alto valor. | Baixa — projetos grandes de infraestrutura |
| **Credenciamento** | Cadastro de fornecedores previamente habilitados para contratações futuras. | Baixa — mais para serviços contínuos |
| **Outro / Desconhecido** | Modalidade não identificada no texto do contrato. | — |
"""
        )

    st.divider()

    # Filtros
    fk1, fk2, fk3 = st.columns([2, 2, 3])
    with fk1:
        tipos_disp = ["Todos"] + sorted(df_k["tipo"].unique().tolist())
        tipo_sel = st.selectbox("Tipo", tipos_disp, format_func=lambda x: TIPO_LABELS.get(x, x))
    with fk2:
        anos_disp = sorted([a for a in df_k["ano"].unique() if a > 2000], reverse=True)
        ano_opts = ["Todos"] + [str(a) for a in anos_disp]
        ano_sel = st.selectbox("Ano", ano_opts)
    with fk3:
        busca_k = st.text_input("Buscar município ou fornecedor", placeholder="...", key="busca_contratos")

    # Aplicar filtros
    exibir_k = df_k.copy()
    if tipo_sel != "Todos":
        exibir_k = exibir_k[exibir_k["tipo"] == tipo_sel]
    if ano_sel != "Todos":
        exibir_k = exibir_k[exibir_k["ano"] == int(ano_sel)]
    if busca_k:
        mask = (
            exibir_k["municipio"].str.contains(busca_k, case=False, na=False)
            | exibir_k["fornecedor"].str.contains(busca_k, case=False, na=False)
        )
        exibir_k = exibir_k[mask]

    # Gráfico: top 15 municípios por valor
    top_mun_k = (
        exibir_k[exibir_k["municipio"] != "—"]
        .groupby("municipio")["valor"]
        .sum()
        .nlargest(15)
        .reset_index()
        .sort_values("valor")
    )
    top_mun_k["valor_fmt"] = top_mun_k["valor"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    if not top_mun_k.empty:
        fig_k = px.bar(
            top_mun_k,
            x="valor",
            y="municipio",
            orientation="h",
            text="valor_fmt",
            title="Top 15 municípios por valor licitado",
            labels={"valor": "Valor (R$)", "municipio": ""},
            height=420,
        )
        fig_k.update_traces(textposition="outside", marker_color="#4e79a7")
        fig_k.update_layout(margin={"t": 50, "r": 130})
        st.plotly_chart(fig_k, use_container_width=True)

    # Tabela
    exibir_k["tipo_label"] = exibir_k["tipo"].map(TIPO_LABELS).fillna(exibir_k["tipo"])
    show_k = (
        exibir_k[["municipio", "tipo_label", "evento_nome", "fornecedor", "valor", "modalidade", "data_pub", "data_evento", "objeto"]]
        .rename(columns={
            "municipio": "Município",
            "tipo_label": "Tipo",
            "evento_nome": "Evento",
            "fornecedor": "Fornecedor",
            "valor": "Valor (R$)",
            "modalidade": "Modalidade",
            "data_pub": "Publicação",
            "data_evento": "Data Evento",
            "objeto": "Objeto",
        })
        .sort_values("Valor (R$)", ascending=False)
    )

    st.caption(f"{len(show_k)} contratos exibidos — clique em uma linha para ver artista e município")
    _show_k_r = show_k.reset_index(drop=True)
    _contract_sel_ev = st.dataframe(
        _show_k_r,
        use_container_width=True,
        height=480,
        on_select="rerun",
        selection_mode="single-row",
        key="contract_table_sel",
        column_config={
            "Valor (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            "Publicação": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Data Evento": st.column_config.DateColumn(format="DD/MM/YYYY"),
        },
    )

    if _contract_sel_ev.selection.rows:
        _c_idx = _contract_sel_ev.selection.rows[0]
        _c_row = _show_k_r.iloc[_c_idx]
        _c_muni = _c_row["Município"]
        _df_contract_detail = load_artist_contracts_detail()
        _det_cont = _df_contract_detail[_df_contract_detail["municipio"] == _c_muni].copy() if _c_muni != "—" else pd.DataFrame()
        _muni_info = df[df["nome"] == _c_muni]
        with st.container(border=True):
            _cdc1, _cdc2 = st.columns([3, 1])
            with _cdc1:
                _tipo_str = str(_c_row.get("Tipo", "")).strip()
                _forn_str = str(_c_row.get("Fornecedor", "")).strip()
                st.markdown(f"#### {_c_muni} — {_tipo_str}")
                if not _muni_info.empty:
                    _mi = _muni_info.iloc[0]
                    st.caption(f"{_mi['mesorregiao']} | {_mi['populacao']:,} hab. | {_mi['porte']}".replace(",", "."))
                if _forn_str:
                    st.write(f"**Fornecedor:** {_forn_str}")
            with _cdc2:
                _val = _c_row.get("Valor (R$)", 0)
                if _val and _val > 0:
                    st.metric("Valor", f"R$ {_val:,.0f}".replace(",", "."))
            if _det_cont.empty:
                st.info("Nenhum artista identificado em contratos deste município." if _c_muni != "—" else "Contrato sem município vinculado.")
            else:
                st.markdown("**Artistas com aparições neste município:**")
                _FONTE_LC = {"pncp": "PNCP", "doe": "DOE/MS", "diogrande": "DIOGRANDE"}
                _det_cont["Fonte"] = _det_cont["fonte"].map(_FONTE_LC).fillna(_det_cont["fonte"])
                st.dataframe(
                    _det_cont[["artista", "Fonte", "cache_real", "data_show", "data_contrato", "descricao"]].rename(columns={
                        "artista": "Artista",
                        "cache_real": "Cachê (R$)",
                        "data_show": "Data Show",
                        "data_contrato": "Data Publ.",
                        "descricao": "Trecho",
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=250,
                    column_config={"Cachê (R$)": st.column_config.NumberColumn(format="R$ %.0f")},
                )

    csv_k = show_k.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "Exportar CSV",
        data=csv_k,
        file_name="contratos_ms.csv",
        mime="text/csv",
        key="export_contratos",
    )

# ── TAB 6: ARTISTAS ───────────────────────────────────────────────────────────

with tab_artistas:
    df_a = load_artists()

    if df_a.empty:
        st.info("Nenhum artista cadastrado. Execute `python scripts/seed_artistas.py`.")
        st.stop()

    # KPIs
    ka1, ka2, ka3, ka4 = st.columns(4)
    with ka1:
        st.metric("Artistas", len(df_a))
    with ka2:
        com_aparicao = (df_a["contratos"] > 0).sum()
        st.metric("Com aparições (PNCP+DOE)", com_aparicao)
    with ka3:
        estilos = df_a[df_a["estilo"] != ""]["estilo"].nunique()
        st.metric("Estilos", estilos)
    with ka4:
        valor_total_a = df_a["valor_total"].sum()
        st.metric("Valor total (cachês reais)", f"R$ {valor_total_a:,.0f}".replace(",", "."))

    st.divider()

    # Filtros
    fa1, fa2, fa3 = st.columns([2, 2, 3])
    with fa1:
        estilos_disp = ["Todos"] + sorted(df_a[df_a["estilo"] != ""]["estilo"].unique())
        estilo_sel = st.selectbox(
            "Estilo",
            estilos_disp,
            format_func=lambda x: STYLE_LABELS.get(x, x),
            key="estilo_artistas",
        )
    with fa2:
        tiers_disp = ["Todos"] + [t for t in FEE_TIER_ORDER if t in df_a["cache"].values]
        tier_sel = st.selectbox(
            "Faixa de Cachê",
            tiers_disp,
            format_func=lambda x: FEE_TIER_LABELS.get(x, x),
            key="tier_artistas",
        )
    with fa3:
        busca_a = st.text_input("Buscar artista", placeholder="Nome...", key="busca_artistas")

    exibir_a = df_a.copy()
    if estilo_sel != "Todos":
        exibir_a = exibir_a[exibir_a["estilo"] == estilo_sel]
    if tier_sel != "Todos":
        exibir_a = exibir_a[exibir_a["cache"] == tier_sel]
    if busca_a:
        exibir_a = exibir_a[exibir_a["nome"].str.contains(busca_a, case=False, na=False)]

    # Gráfico: artistas por estilo
    if not exibir_a.empty:
        por_estilo = (
            exibir_a[exibir_a["estilo"] != ""]
            .groupby("estilo")
            .size()
            .reset_index(name="total")
            .sort_values("total", ascending=True)
        )
        por_estilo["estilo_label"] = por_estilo["estilo"].map(STYLE_LABELS).fillna(por_estilo["estilo"])
        if not por_estilo.empty:
            fig_a = px.bar(
                por_estilo,
                x="total",
                y="estilo_label",
                orientation="h",
                text="total",
                title="Artistas por Estilo",
                labels={"total": "Qtde", "estilo_label": ""},
                height=280,
            )
            fig_a.update_traces(textposition="outside", marker_color="#59a14f")
            fig_a.update_layout(margin={"t": 40, "r": 60})
            st.plotly_chart(fig_a, use_container_width=True)

    # Tabela
    exibir_a["estilo_label"] = exibir_a["estilo"].map(STYLE_LABELS).fillna(exibir_a["estilo"])
    exibir_a["cache_label"] = exibir_a["cache"].map(FEE_TIER_LABELS).fillna(exibir_a["cache"])
    exibir_a["pop_label"] = exibir_a["popularidade"].map(POP_LABELS).fillna(exibir_a["popularidade"])

    show_a = exibir_a[[
        "nome", "estilo_label", "sub_estilo", "cache_label", "pop_label",
        "origem_estado", "contratos", "valor_total", "n_municipios", "municipios",
    ]].rename(columns={
        "nome": "Artista",
        "estilo_label": "Estilo",
        "sub_estilo": "Sub-estilo",
        "cache_label": "Cachê",
        "pop_label": "Popularidade",
        "origem_estado": "UF",
        "contratos": "Aparições",
        "valor_total": "Valor (R$)",
        "n_municipios": "Municípios (#)",
        "municipios": "Municípios",
    }).sort_values(["Aparições", "Valor (R$)"], ascending=False)

    st.caption(f"{len(show_a)} artistas exibidos — clique em uma linha para ver contratos e municípios")
    _show_a_r = show_a.reset_index(drop=True)
    _artist_sel_ev = st.dataframe(
        _show_a_r,
        use_container_width=True,
        height=520,
        on_select="rerun",
        selection_mode="single-row",
        key="artist_table_sel",
        column_config={
            "Valor (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            "Aparições": st.column_config.NumberColumn(format="%d"),
            "Municípios (#)": st.column_config.NumberColumn(format="%d"),
        },
    )

    if _artist_sel_ev.selection.rows:
        _a_idx = _artist_sel_ev.selection.rows[0]
        _a_nome = _show_a_r.iloc[_a_idx]["Artista"]
        _df_artist_detail = load_artist_contracts_detail()
        _det_art = _df_artist_detail[_df_artist_detail["artista"] == _a_nome].copy()
        with st.container(border=True):
            _a_info = exibir_a[exibir_a["nome"] == _a_nome]
            if not _a_info.empty:
                _ai = _a_info.iloc[0]
                st.markdown(f"#### {_a_nome}")
                st.caption(
                    f"{STYLE_LABELS.get(_ai['estilo'], _ai['estilo'])} | "
                    f"{FEE_TIER_LABELS.get(_ai['cache'], _ai['cache'])} | "
                    f"{POP_LABELS.get(_ai['popularidade'], _ai['popularidade'])} | "
                    f"Origem: {_ai['origem_estado'] or '—'}"
                )
            else:
                st.markdown(f"#### {_a_nome}")
            if _det_art.empty:
                st.info("Sem aparições registradas.")
            else:
                _FONTE_LA = {"pncp": "PNCP", "doe": "DOE/MS", "diogrande": "DIOGRANDE"}
                _det_art["Fonte"] = _det_art["fonte"].map(_FONTE_LA).fillna(_det_art["fonte"])
                _com_val_a = _det_art["cache_real"].notna()
                _aac1, _aac2, _aac3 = st.columns(3)
                _aac1.metric("Aparições", len(_det_art))
                _aac2.metric("Municípios", _det_art["municipio"].nunique())
                _aac3.metric(
                    "Valor total",
                    f"R$ {_det_art.loc[_com_val_a, 'cache_real'].sum():,.0f}".replace(",", ".")
                    if _com_val_a.any() else "—",
                )
                st.dataframe(
                    _det_art[["Fonte", "municipio", "cache_real", "data_show", "data_contrato", "descricao"]].rename(columns={
                        "municipio": "Município",
                        "cache_real": "Cachê (R$)",
                        "data_show": "Data Show",
                        "data_contrato": "Data Publ.",
                        "descricao": "Trecho",
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=300,
                    column_config={"Cachê (R$)": st.column_config.NumberColumn(format="R$ %.0f")},
                )

    csv_a = show_a.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "Exportar CSV",
        data=csv_a,
        file_name="artistas_ms.csv",
        mime="text/csv",
        key="export_artistas",
    )

    st.divider()

    # ── Histórico unificado (PNCP + DOE) ────────────────────────────────────────
    st.subheader("Histórico Unificado de Contratos e Citações (PNCP + DOE)")
    st.caption(
        "Contratos do PNCP e citações nos Diários Oficiais com artista identificado. "
        "Valores reais de cachê quando disponíveis — use para calibrar propostas."
    )
    df_art_hist = load_artist_contracts_detail()
    if df_art_hist.empty:
        st.info("Nenhum contrato com artista e município identificados ainda.")
    else:
        fah1, fah2 = st.columns(2)
        with fah1:
            artistas_hist_opts = ["Todos"] + sorted(df_art_hist["artista"].unique().tolist())
            artista_hist_sel = st.selectbox("Artista", artistas_hist_opts, key="artista_hist_sel")
        with fah2:
            muni_hist_opts = ["Todos"] + sorted(df_art_hist["municipio"].unique().tolist())
            muni_hist_sel = st.selectbox("Município", muni_hist_opts, key="muni_hist_sel")

        df_hist_show = df_art_hist.copy()
        if artista_hist_sel != "Todos":
            df_hist_show = df_hist_show[df_hist_show["artista"] == artista_hist_sel]
        if muni_hist_sel != "Todos":
            df_hist_show = df_hist_show[df_hist_show["municipio"] == muni_hist_sel]

        com_valor = df_hist_show["cache_real"].notna()
        kh1, kh2, kh3, kh4 = st.columns(4)
        kh1.metric("Total aparições", len(df_hist_show))
        kh2.metric("Com valor registrado", com_valor.sum())
        kh3.metric(
            "Cachê médio",
            f"R$ {df_hist_show.loc[com_valor, 'cache_real'].mean():,.0f}".replace(",", ".")
            if com_valor.any() else "—",
        )
        kh4.metric(
            "Cachê máximo",
            f"R$ {df_hist_show['cache_real'].max():,.0f}".replace(",", ".")
            if com_valor.any() else "—",
        )

        FONTE_LABELS = {"pncp": "PNCP", "doe": "DOE/MS", "diogrande": "DIOGRANDE"}
        df_hist_show = df_hist_show.copy()
        df_hist_show["fonte_label"] = df_hist_show["fonte"].map(FONTE_LABELS).fillna(df_hist_show["fonte"])

        st.dataframe(
            df_hist_show[[
                "artista", "fonte_label", "municipio", "mesorregiao",
                "cache_real", "data_show", "data_contrato", "descricao",
            ]].rename(columns={
                "artista":      "Artista",
                "fonte_label":  "Fonte",
                "municipio":    "Município",
                "mesorregiao":  "Mesorregião",
                "cache_real":   "Cachê (R$)",
                "data_show":    "Data Show",
                "data_contrato":"Data Publ.",
                "descricao":    "Trecho",
            }),
            use_container_width=True,
            height=420,
            column_config={
                "Cachê (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
            },
        )

    st.divider()

    # ── Artistas mais ativos no DOE/MS ──────────────────────────────────────────
    st.subheader("Artistas Mais Ativos no DOE/MS e DIOGRANDE")
    st.caption(
        "Artistas mencionados em editais e contratos publicados nos diários oficiais — "
        "sinal de que estão sendo contratados ativamente por prefeituras. "
        "\"Novo lead\" = artista ativo mas ainda não no nosso catálogo."
    )
    df_doe_art = load_doe_artist_activity()
    if df_doe_art.empty:
        st.info("Nenhum dado de DOE disponível.")
    else:
        cat_names_lower = set(df_a["nome"].str.lower().str.strip())
        def _check_catalogo(nome: str) -> str:
            n = nome.lower().strip()
            if n in cat_names_lower:
                return "No catálogo"
            for c in cat_names_lower:
                if (len(c) > 4 and c in n) or (len(n) > 4 and n in c):
                    return "No catálogo"
            return "Novo lead"

        df_doe_art["catalogo"] = df_doe_art["artista"].apply(_check_catalogo)

        novos_leads = (df_doe_art["catalogo"] == "Novo lead").sum()
        kd1, kd2, kd3 = st.columns(3)
        kd1.metric("Artistas únicos no DOE", len(df_doe_art))
        kd2.metric("No catálogo", (df_doe_art["catalogo"] == "No catálogo").sum())
        kd3.metric("Novos leads", novos_leads)

        st.dataframe(
            df_doe_art[[
                "artista", "hits_doe", "edicoes", "ultimo", "n_municipios", "catalogo",
            ]].rename(columns={
                "artista": "Artista",
                "hits_doe": "Menções DOE",
                "edicoes": "Edições",
                "ultimo": "Última citação",
                "n_municipios": "Municípios",
                "catalogo": "Catálogo",
            }),
            use_container_width=True,
            height=420,
        )

# ── TAB 7: FORNECEDORES ───────────────────────────────────────────────────────

with tab_fornecedores:
    df_f = load_suppliers()
    df_tmpl = load_rodeo_templates()

    if df_f.empty:
        st.info("Nenhum fornecedor cadastrado. Execute `python scripts/seed_fornecedores.py`.")
    else:
        # KPIs
        kf1, kf2, kf3, kf4 = st.columns(4)
        with kf1:
            st.metric("Fornecedores", len(df_f))
        with kf2:
            cats = df_f["categoria"].nunique()
            st.metric("Categorias", cats)
        with kf3:
            cidades = df_f["cidade"].nunique()
            st.metric("Cidades atendidas", cidades)
        with kf4:
            com_preco = (df_f["n_precos"] > 0).sum()
            st.metric("Com preços cadastrados", com_preco)

        st.divider()

        col_sup, col_tmpl = st.columns([3, 2])

        with col_sup:
            st.subheader("Catálogo de Fornecedores")

            # Filtros
            ff1, ff2, ff3 = st.columns([2, 2, 3])
            with ff1:
                cats_disp = ["Todas"] + sorted(df_f["categoria"].unique().tolist())
                cat_sel = st.selectbox(
                    "Categoria",
                    cats_disp,
                    format_func=lambda x: SUPPLIER_CAT_LABELS.get(x, x),
                    key="cat_fornecedores",
                )
            with ff2:
                cidades_disp = ["Todas"] + sorted(df_f["cidade"].unique().tolist())
                cidade_sel = st.selectbox("Cidade", cidades_disp, key="cidade_fornecedores")
            with ff3:
                busca_f = st.text_input("Buscar por nome", placeholder="...", key="busca_fornecedores")

            exibir_f = df_f.copy()
            if cat_sel != "Todas":
                exibir_f = exibir_f[exibir_f["categoria"] == cat_sel]
            if cidade_sel != "Todas":
                exibir_f = exibir_f[exibir_f["cidade"] == cidade_sel]
            if busca_f:
                exibir_f = exibir_f[exibir_f["nome"].str.contains(busca_f, case=False, na=False)]

            exibir_f["cat_label"] = exibir_f["categoria"].map(SUPPLIER_CAT_LABELS).fillna(exibir_f["categoria"])
            show_f = exibir_f[[
                "nome", "cat_label", "cidade", "regiao", "contato", "telefone", "n_precos", "preco_min_avg", "preco_max_avg", "notas"
            ]].rename(columns={
                "nome": "Fornecedor",
                "cat_label": "Categoria",
                "cidade": "Cidade",
                "regiao": "Região",
                "contato": "Contato",
                "telefone": "Telefone",
                "n_precos": "Faixas de Preço",
                "preco_min_avg": "Menor Avg (R$)",
                "preco_max_avg": "Maior Avg (R$)",
                "notas": "Obs",
            })

            st.caption(f"{len(show_f)} fornecedores exibidos")
            st.dataframe(
                show_f,
                use_container_width=True,
                height=480,
                column_config={
                    "Menor Avg (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                    "Maior Avg (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                    "Faixas de Preço": st.column_config.NumberColumn(format="%d"),
                },
            )

            csv_f = show_f.to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button(
                "Exportar CSV",
                data=csv_f,
                file_name="fornecedores_ms.csv",
                mime="text/csv",
                key="export_fornecedores",
            )

            # Gráfico por categoria
            por_cat = (
                df_f.groupby("categoria").size()
                .reset_index(name="total")
                .sort_values("total")
            )
            por_cat["cat_label"] = por_cat["categoria"].map(SUPPLIER_CAT_LABELS).fillna(por_cat["categoria"])
            fig_f = px.bar(
                por_cat,
                x="total",
                y="cat_label",
                orientation="h",
                text="total",
                title="Fornecedores por Categoria",
                labels={"total": "Qtde", "cat_label": ""},
                height=340,
            )
            fig_f.update_traces(textposition="outside", marker_color="#e15759")
            fig_f.update_layout(margin={"t": 40, "r": 60})
            st.plotly_chart(fig_f, use_container_width=True)

        with col_tmpl:
            st.subheader("Templates de Orçamento")

            if df_tmpl.empty:
                st.info("Execute `python scripts/seed_rodeio_templates.py` para carregar os templates.")
            else:
                for _, row in df_tmpl.iterrows():
                    porte_label = EVENT_SIZE_LABELS.get(row["porte"], row["porte"])
                    with st.expander(f"{row['nome']} — {porte_label}"):
                        st.caption(row["descricao"])
                        tc1, tc2, tc3 = st.columns(3)
                        with tc1:
                            st.metric("Público", f"{row['publico']:,}".replace(",", "."))
                        with tc2:
                            st.metric("Duração", f"{row['dias']} dias")
                        with tc3:
                            st.metric("Orç. Médio", f"R$ {row['total_avg']:,.0f}".replace(",", "."))

                        st.write("**Faixa estimada:**")
                        st.write(
                            f"Mínimo: R$ {row['total_min']:,.0f} | "
                            f"Médio: R$ {row['total_avg']:,.0f} | "
                            f"Máximo: R$ {row['total_max']:,.0f}".replace(",", ".")
                        )

                        # tabela de itens
                        itens = row["itens_json"]
                        item_rows = []
                        for cat, vals in itens.items():
                            if cat.startswith("_"):
                                continue
                            item_rows.append({
                                "Item": SUPPLIER_CAT_LABELS.get(cat, cat),
                                "Mín (R$)": vals.get("min", 0),
                                "Médio (R$)": vals.get("avg", 0),
                                "Máx (R$)": vals.get("max", 0),
                            })
                        if item_rows:
                            df_items = pd.DataFrame(item_rows)
                            st.dataframe(
                                df_items,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Mín (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                                    "Médio (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                                    "Máx (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                                },
                            )

    # ── Simulador com Margem ──────────────────────────────────────────────────
    st.divider()
    st.subheader("Simulador de Proposta com Margem")
    st.caption("Calcule o custo do evento e o valor a cobrar da prefeitura.")

    from analytics.simulador_rodeio import SimuladorRodeio

    sim_c1, sim_c2 = st.columns([2, 3])

    with sim_c1:
        sim_porte = st.selectbox(
            "Porte do evento",
            options=["pequeno", "medio", "grande", "mega"],
            format_func=lambda x: EVENT_SIZE_LABELS.get(x, x),
            key="sim_porte",
        )
        sim_dias = st.number_input("Dias de evento", min_value=1, max_value=10, value=2, key="sim_dias")
        sim_publico = st.number_input("Público estimado", min_value=100, max_value=200_000, value=3000, step=500, key="sim_publico")
        sim_margem = st.slider(
            "Margem da Sell (%)",
            min_value=0, max_value=50, value=20, step=5,
            help="Percentual aplicado sobre o custo total de estrutura",
            key="sim_margem",
        )
        sim_cache = st.number_input(
            "Cachê do artista (R$)",
            min_value=0, max_value=5_000_000, value=0, step=10_000,
            help="Valor do cachê — entra na proposta mas não no custo de estrutura",
            key="sim_cache",
        )

    with sim_c2:
        sim = SimuladorRodeio(
            event_size=sim_porte,
            dias=sim_dias,
            publico=sim_publico,
            margem_percentual=float(sim_margem),
            cache_artista=float(sim_cache),
        )
        orc = sim.calcular()
        res = orc.resumo()

        # KPIs principais
        sk1, sk2, sk3 = st.columns(3)
        with sk1:
            st.metric(
                "Custo estrutura (avg)",
                f"R$ {res['total_avg']:,.0f}".replace(",", "."),
            )
        with sk2:
            st.metric(
                "Margem Sell",
                f"R$ {res['margem_valor_avg']:,.0f}".replace(",", "."),
                delta=f"{sim_margem}%",
            )
        with sk3:
            st.metric(
                "Proposta total (avg)",
                f"R$ {res['proposta_avg']:,.0f}".replace(",", "."),
                help="Estrutura + margem + cachê do artista",
            )

        # Faixa da proposta
        st.write(
            f"**Faixa da proposta:** "
            f"R$ {res['proposta_min']:,.0f} (min) — "
            f"R$ {res['proposta_avg']:,.0f} (avg) — "
            f"R$ {res['proposta_max']:,.0f} (max)".replace(",", ".")
        )

        if sim_cache > 0:
            st.write(
                f"Cachê do artista: **R$ {sim_cache:,.0f}** &nbsp;|&nbsp; "
                f"Custo estrutura: **R$ {res['total_avg']:,.0f}** &nbsp;|&nbsp; "
                f"Margem: **R$ {res['margem_valor_avg']:,.0f}**".replace(",", ".")
            )

        # Tabela de itens
        df_sim_itens = pd.DataFrame(res["itens"])
        if not df_sim_itens.empty:
            df_sim_itens = df_sim_itens.rename(columns={
                "categoria": "Item",
                "descricao": "Descrição",
                "dias": "Dias",
                "min": "Mín (R$)",
                "avg": "Médio (R$)",
                "max": "Máx (R$)",
            })
            df_sim_itens["Item"] = df_sim_itens["Item"].map(SUPPLIER_CAT_LABELS).fillna(df_sim_itens["Item"])
            st.dataframe(
                df_sim_itens[["Item", "Descrição", "Dias", "Mín (R$)", "Médio (R$)", "Máx (R$)"]],
                use_container_width=True,
                hide_index=True,
                height=320,
                column_config={
                    "Mín (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                    "Médio (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                    "Máx (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
                },
            )

# ── TAB 8: OPORTUNIDADES ──────────────────────────────────────────────────────

STATUS_LABELS_OPP = {
    "novo":             "Novo",
    "pesquisar":        "Pesquisar",
    "abordar":          "Abordar",
    "em_contato":       "Em Contato",
    "proposta_enviada": "Proposta Enviada",
    "negociacao":       "Negociação",
    "ganho":            "Ganho",
    "perdido":          "Perdido",
    "suspenso":         "Suspenso",
}

STATUS_CORES = {
    "novo":             "#aaaaaa",
    "pesquisar":        "#4e79a7",
    "abordar":          "#f28e2b",
    "em_contato":       "#edc948",
    "proposta_enviada": "#76b7b2",
    "negociacao":       "#59a14f",
    "ganho":            "#2ca02c",
    "perdido":          "#e15759",
    "suspenso":         "#9edae5",
}

JANELA_LABEL = {
    1.0: "ABORDAR AGORA",
    0.9: "ABORDAR AGORA",
    0.7: "Em até 2 semanas",
    0.5: "Em 1-2 meses",
    0.2: "Sem urgência",
    0.0: "Sem evento mapeado",
}


MESES_PT = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}


@st.cache_data(ttl=300)
def load_radar_oportunidades(janela_meses: int = 6) -> pd.DataFrame:
    """
    Uma linha por evento anual recorrente previsto na janela, com os contratos
    do mesmo mês (±1) do ano passado — sem data de contrato em 2026 ainda.
    """
    from collections import defaultdict
    from datetime import date
    from sqlalchemy import extract

    from app.models.commercial_opportunity import CommercialOpportunity
    from app.models.municipal_event import MunicipalEvent
    from app.models.public_contract import PublicContract

    db = SessionLocal()
    try:
        today = date.today()
        ano_passado = today.year - 1
        ano_atual = today.year

        meses_janela = [(today.month - 1 + i) % 12 + 1 for i in range(janela_meses + 1)]

        munis = {m.id: m for m in db.query(Municipality).filter(Municipality.state == "MS").all()}

        # Apenas eventos anuais recorrentes na janela
        eventos_anuais = db.query(MunicipalEvent).filter(
            MunicipalEvent.usual_month.in_(meses_janela),
            MunicipalEvent.recurrence_pattern == "anual",
        ).all()

        # Todos os contratos do ano passado nos meses da janela
        contratos_lp = db.query(PublicContract).filter(
            extract("year", PublicContract.publication_date) == ano_passado,
            extract("month", PublicContract.publication_date).in_(meses_janela),
            PublicContract.municipality_id.isnot(None),
        ).all()

        # Índice: (muni_id, mes) → lista de contratos
        contratos_idx: dict = defaultdict(list)
        for c in contratos_lp:
            if c.publication_date:
                contratos_idx[(c.municipality_id, c.publication_date.month)].append(c)

        # Municípios que já publicaram contrato em 2026 no mesmo período
        ids_ja_2026 = {
            row.municipality_id
            for row in db.query(PublicContract.municipality_id).filter(
                extract("year", PublicContract.publication_date) == ano_atual,
                extract("month", PublicContract.publication_date).in_(meses_janela),
                PublicContract.municipality_id.isnot(None),
            ).all()
        }

        contacts_por_muni: dict = defaultdict(list)
        for ct in db.query(PublicContact).all():
            contacts_por_muni[ct.municipality_id].append(ct)

        scores = {o.municipality_id: o.final_opportunity_score for o in db.query(CommercialOpportunity).all()}

        rows = []
        for ev in eventos_anuais:
            if ev.municipality_id in ids_ja_2026:
                continue  # já contratou este ano, fora do radar

            muni = munis.get(ev.municipality_id)
            if not muni:
                continue

            # Contratos do mês do evento ±1
            meses_ev = {(ev.usual_month - 2 + i) % 12 + 1 for i in range(3)}
            contratos_ev = []
            for m in meses_ev:
                contratos_ev.extend(contratos_idx.get((ev.municipality_id, m), []))

            valores = [float(c.contract_value) for c in contratos_ev
                       if c.contract_value and float(c.contract_value) > 0]
            orcamento_medio = round(sum(valores) / len(valores), 0) if valores else 0
            orcamento_total = sum(valores)

            suppliers = list({c.supplier_name for c in contratos_ev
                               if c.supplier_name and c.supplier_name.strip()})

            contatos = contacts_por_muni[ev.municipality_id]
            contato = None
            for role in ("secretario_cultura", "secretario_turismo", "prefeito"):
                ct = next((c for c in contatos if c.role == role), None)
                if ct:
                    contato = ct
                    break

            rows.append({
                "municipio": muni.name,
                "mesorregiao": muni.mesorregiao or "",
                "evento": ev.name,
                "tipo_evento": (ev.event_type or "").replace("_", " ").title(),
                "mes_previsto": ev.usual_month,
                "mes_nome": MESES_PT.get(ev.usual_month, "?"),
                "n_contratos_lp": len(contratos_ev),
                "orcamento_medio": orcamento_medio,
                "orcamento_total_lp": orcamento_total,
                "fornecedores_lp": " | ".join(suppliers[:3]) if suppliers else "Sem historico PNCP",
                "contato_nome": contato.name if contato else "",
                "contato_cargo": (contato.role or "").replace("_", " ").title() if contato else "",
                "contato_email": contato.email or "" if contato else "",
                "score": scores.get(ev.municipality_id, 0),
            })

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        return df.sort_values(["mes_previsto", "score"], ascending=[True, False]).reset_index(drop=True)
    finally:
        db.close()


@st.cache_data(ttl=300)
def load_diario_alertas(dias: int = 30) -> pd.DataFrame:
    """Hits recentes do DOE/MS e DIOGRANDE com shows/artistas."""
    from datetime import date, timedelta
    from sqlalchemy import text
    db = SessionLocal()
    try:
        cutoff = str(date.today() - timedelta(days=dias))
        rows = db.execute(text("""
            SELECT
                dh.data_publicacao,
                COALESCE(m.name, dh.municipio_detectado, 'Não identificado') AS municipio,
                COALESCE(m.mesorregiao, '')                                   AS mesorregiao,
                COALESCE(dh.artista_detectado, '')                            AS artista,
                COALESCE(dh.tipo_contratacao, 'outro')                        AS tipo,
                dh.keyword,
                LEFT(COALESCE(dh.highlight, ''), 200)                         AS contexto,
                ROUND(COALESCE(dh.confidence_score, 0) * 100)                 AS confianca,
                dh.municipio_id,
                COALESCE(dh.raw_json->>'fonte', 'doe')                        AS fonte
            FROM diario_oficial_hits dh
            LEFT JOIN municipalities m ON dh.municipio_id = m.id
            WHERE dh.status IN ('novo', 'potencial')
              AND dh.data_publicacao >= :cutoff
            ORDER BY dh.data_publicacao DESC
        """), {"cutoff": cutoff}).fetchall()
        if not rows:
            return pd.DataFrame()
        records = [
            {
                "data": r.data_publicacao,
                "municipio": r.municipio,
                "mesorregiao": r.mesorregiao,
                "artista": r.artista,
                "tipo": (r.tipo or "outro").title(),
                "keyword": r.keyword,
                "contexto": r.contexto or "",
                "confianca": int(r.confianca or 0),
                "municipio_id": r.municipio_id,
                "fonte": (r.fonte or "doe").upper(),
            }
            for r in rows
        ]
        return pd.DataFrame(records)
    finally:
        db.close()


@st.cache_data(ttl=60)
def load_accreditation_notices() -> pd.DataFrame:
    from app.models.accreditation_notice import AccreditationNotice
    db = SessionLocal()
    try:
        rows = (
            db.query(AccreditationNotice, Municipality)
            .join(Municipality, AccreditationNotice.municipality_id == Municipality.id)
            .filter(AccreditationNotice.is_active == True)
            .order_by(AccreditationNotice.data_publicacao.desc())
            .all()
        )
        records = []
        for an, m in rows:
            records.append({
                "municipio": m.name,
                "mesorregiao": m.mesorregiao or "",
                "objeto": an.objeto or "",
                "publicado": an.data_publicacao,
                "encerramento": an.data_encerramento,
                "valor": float(an.valor_estimado) if an.valor_estimado else 0.0,
                "link": f"https://pncp.gov.br/app/editais/{an.numero_controle}",
                "numero_controle": an.numero_controle,
            })
        return pd.DataFrame(records)
    finally:
        db.close()


def load_opportunities() -> pd.DataFrame:
    from datetime import date
    from app.models.accreditation_notice import AccreditationNotice
    from app.models.commercial_opportunity import CommercialOpportunity
    from sqlalchemy import func, text
    db = SessionLocal()
    try:
        rows = (
            db.query(CommercialOpportunity, Municipality)
            .join(Municipality, CommercialOpportunity.municipality_id == Municipality.id)
            .order_by(CommercialOpportunity.final_opportunity_score.desc())
            .all()
        )
        cred_rows = (
            db.query(
                AccreditationNotice.municipality_id,
                func.count(AccreditationNotice.id).label("n_cred"),
            )
            .filter(AccreditationNotice.is_active == True)
            .group_by(AccreditationNotice.municipality_id)
            .all()
        )
        cred_map = {row.municipality_id: row.n_cred for row in cred_rows}

        # Janela aberta: municípios com contratos no mesmo período do ano passado mas não ainda este ano
        today = date.today()
        meses_janela = [(today.month - 1 + i) % 12 + 1 for i in range(7)]
        meses_in = "(" + ",".join(str(m) for m in meses_janela) + ")"
        ids_lp = {
            r[0] for r in db.execute(text(f"""
                SELECT DISTINCT municipality_id FROM public_contracts
                WHERE EXTRACT(YEAR FROM publication_date) = :ano
                  AND EXTRACT(MONTH FROM publication_date) IN {meses_in}
                  AND municipality_id IS NOT NULL
            """), {"ano": today.year - 1}).fetchall()
        }
        ids_atual = {
            r[0] for r in db.execute(text(f"""
                SELECT DISTINCT municipality_id FROM public_contracts
                WHERE EXTRACT(YEAR FROM publication_date) = :ano
                  AND EXTRACT(MONTH FROM publication_date) IN {meses_in}
                  AND municipality_id IS NOT NULL
            """), {"ano": today.year}).fetchall()
        }
        janela_aberta_ids = ids_lp - ids_atual

        records = []
        for o, m in rows:
            artists_json = o.recommended_artists_json or {}
            artistas = artists_json.get("artistas", [])
            artistas_nomes = ", ".join(
                a["nome"] for a in artistas[:3] if a.get("ja_atuou_regiao") or True
            )
            artistas_regiao = ", ".join(
                a["nome"] for a in artistas if a.get("ja_atuou_regiao")
            )

            urgency = o.urgency_score or 0.0
            janela_label = JANELA_LABEL.get(urgency)
            if janela_label is None:
                if urgency >= 0.9:
                    janela_label = "ABORDAR AGORA"
                elif urgency >= 0.7:
                    janela_label = "Em até 2 semanas"
                elif urgency >= 0.5:
                    janela_label = "Em 1-2 meses"
                elif urgency > 0:
                    janela_label = "Sem urgência"
                else:
                    janela_label = "Sem evento mapeado"

            aniv_mes = m.aniversario_mes
            aniv_dia = m.aniversario_dia
            aniv_fmt = ""
            if aniv_mes and aniv_dia:
                _mn = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                       "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                aniv_fmt = f"{int(aniv_dia):02d}/{_mn[int(aniv_mes)]}"

            records.append({
                "municipio": m.name,
                "mesorregiao": m.mesorregiao or "",
                "populacao": m.population or 0,
                "score": o.final_opportunity_score or 0.0,
                "urgencia": urgency,
                "janela": janela_label,
                "fit": o.fit_score or 0.0,
                "recorrencia": o.margin_potential_score or 0.0,
                "status": o.status.value if o.status else "novo",
                "budget_medio": float(o.estimated_budget) if o.estimated_budget else 0.0,
                "data_evento_est": o.estimated_event_date,
                "n_shows": artists_json.get("n_shows_historico", 0),
                "valor_total_shows": artists_json.get("valor_medio_historico", 0) * artists_json.get("n_shows_historico", 0),
                "estilo_dominante": artists_json.get("padrao_estilo", ""),
                "artistas_sugeridos": artistas_nomes,
                "artistas_regiao": artistas_regiao,
                "proxima_acao": o.suggested_next_action or "",
                "aniversario": aniv_fmt,
                "aniversario_mes": aniv_mes,
                "n_credenciamentos": cred_map.get(m.id, 0),
                "janela_aberta": m.id in janela_aberta_ids,
                "id": o.id,
                "ibge_code": m.ibge_code,
                "lat": COORDS.get(m.ibge_code, (None, None))[0],
                "lon": COORDS.get(m.ibge_code, (None, None))[1],
            })
        return pd.DataFrame(records)
    finally:
        db.close()


def _months_until_approx(month: int, today) -> int:
    if month == today.month:
        return 0
    return (month - today.month) % 12


def _mes_nome(mes: int | None) -> str:
    meses = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    if mes and 1 <= mes <= 12:
        return meses[mes]
    return "—"


@st.cache_data(ttl=60)
def load_closest_events() -> dict:
    import datetime
    from app.models.municipal_event import MunicipalEvent
    today = datetime.date.today()
    db = SessionLocal()
    try:
        eventos = (
            db.query(MunicipalEvent, Municipality)
            .join(Municipality, MunicipalEvent.municipality_id == Municipality.id)
            .filter(MunicipalEvent.usual_month.isnot(None))
            .all()
        )
        by_muni: dict[str, dict] = {}
        for e, m in eventos:
            months_ahead = _months_until_approx(e.usual_month, today)
            existing = by_muni.get(m.name)
            if existing is None or months_ahead < existing["months_ahead"]:
                by_muni[m.name] = {
                    "nome": e.name,
                    "mes": e.usual_month,
                    "data_est": e.estimated_start_date,
                    "months_ahead": months_ahead,
                }
        return by_muni
    finally:
        db.close()


def _gerar_resumo(row: "pd.Series", closest_event: "dict | None") -> str:
    partes = []
    n = int(row["n_shows"])
    budget = row["budget_medio"]
    if n > 0:
        budget_str = f'R$ {budget:,.0f}'.replace(",", ".")
        partes.append(f"{n} show(s) contratado(s) no PNCP — budget médio {budget_str}/show")
    else:
        partes.append("Sem historico de shows registrados no PNCP")

    if closest_event:
        data_est = closest_event.get("data_est")
        if data_est:
            data_str = data_est.strftime("%d/%m/%Y")
        else:
            data_str = _mes_nome(closest_event["mes"])
        partes.append(f"proximo evento mapeado: '{closest_event['nome']}' ({data_str})")

    janela = row["janela"]
    if "AGORA" in janela:
        partes.append("janela URGENTE — abordar esta semana antes da licitacao")
    elif "semanas" in janela:
        partes.append("janela aberta — abordar nas proximas 2 semanas")
    elif "meses" in janela:
        partes.append("janela em 1-2 meses — planejar abordagem")

    estilo = row.get("estilo_dominante", "")
    if estilo and estilo not in ("nao_identificado", ""):
        estilo_label = STYLE_LABELS.get(estilo, estilo)
        partes.append(f"estilo historico: {estilo_label}")

    return ". ".join(partes) + "."


@st.cache_data(ttl=120)
def load_contract_status() -> dict:
    import datetime
    from collections import Counter
    from app.models.public_contract import PublicContract
    from app.models.enums import ContractType

    today = datetime.date.today()
    current_year = today.year
    db = SessionLocal()
    try:
        rows = (
            db.query(PublicContract, Municipality)
            .join(Municipality, PublicContract.municipality_id == Municipality.id)
            .filter(PublicContract.contract_type == ContractType.show_artistico)
            .filter(PublicContract.publication_date.isnot(None))
            .order_by(PublicContract.publication_date.desc())
            .all()
        )
        by_muni: dict[str, list] = {}
        for c, m in rows:
            by_muni.setdefault(m.name, []).append(c)

        result = {}
        for muni_name, contracts in by_muni.items():
            this_year = [c for c in contracts if c.publication_date.year == current_year]
            historical = [c for c in contracts if c.publication_date.year < current_year]

            if this_year:
                total_val = sum(float(c.contract_value) for c in this_year if c.contract_value)
                result[muni_name] = {
                    "status": "contrato_aberto",
                    "valor": total_val,
                    "n": len(this_year),
                    "ano": current_year,
                }
            elif historical:
                most_recent = historical[0]  # já ordenado desc
                months = [c.publication_date.month for c in historical]
                mes_tipico = Counter(months).most_common(1)[0][0]
                result[muni_name] = {
                    "status": "momento_contatar",
                    "ultimo_mes": most_recent.publication_date.month,
                    "ultimo_ano": most_recent.publication_date.year,
                    "mes_tipico": mes_tipico,
                    "meses_ate": (mes_tipico - today.month) % 12,
                    "valor_ultimo": float(most_recent.contract_value) if most_recent.contract_value else 0,
                }
        return result
    finally:
        db.close()


def _fmt_contract_status(muni_name: str, cs: dict) -> str:
    info = cs.get(muni_name)
    if not info:
        return "—"
    if info["status"] == "contrato_aberto":
        val = info["valor"]
        val_str = f"R$ {val/1000:.0f}k" if val >= 1_000 else f"R$ {val:.0f}"
        sufixo = f" ({info['n']} contratos)" if info["n"] > 1 else ""
        return f"Contrato {info['ano']}: {val_str}{sufixo}"
    if info["status"] == "momento_contatar":
        ultimo = f"{_mes_nome(info['ultimo_mes'])}/{info['ultimo_ano']}"
        ma = info["meses_ate"]
        mes_tip = _mes_nome(info["mes_tipico"])
        if ma == 0:
            return f"JANELA AGORA — ultimo em {ultimo}"
        if ma <= 2:
            return f"Abre em {ma}m ({mes_tip}) — ultimo em {ultimo}"
        return f"Contrata em {mes_tip} (~{ma}m) — ultimo em {ultimo}"
    return "—"


with tab_opp:
    df_o = load_opportunities()
    df_cred_notices = load_accreditation_notices()
    _closest = load_closest_events()

    df_o["proximo_evento"] = df_o["municipio"].map(
        lambda m: (
            f"{_closest[m]['nome']} ({_mes_nome(_closest[m]['mes'])})"
            if m in _closest else "—"
        )
    )
    df_o["resumo"] = df_o.apply(
        lambda r: _gerar_resumo(r, _closest.get(r["municipio"])),
        axis=1,
    )

    df_c_opp = load_contacts()

    def _decisor_resumo(muni_name: str) -> str:
        ct = df_c_opp[df_c_opp["municipio"] == muni_name]
        pref = ct[ct["cargo"] == "prefeito"]
        secs = ct[ct["cargo"].isin(["secretario_cultura", "secretario_turismo"])]
        parts = []
        if not pref.empty:
            parts.append(pref.iloc[0]["nome"])
        if not secs.empty:
            c_row = secs.iloc[0]
            label = CARGO_LABELS.get(c_row["cargo"], c_row["cargo"])
            parts.append(f"{label}: {c_row['nome']}")
        return " | ".join(parts) if parts else "—"

    df_o["decisor"] = df_o["municipio"].apply(_decisor_resumo)

    if df_o.empty:
        st.info("Nenhuma oportunidade calculada. Execute `python scripts/run_opportunity_engine.py`.")
        st.stop()

    # KPIs
    ko1, ko2, ko3, ko4, ko5, ko6, ko7 = st.columns(7)
    abordar_agora = (df_o["urgencia"] >= 0.9).sum()
    com_historico = (df_o["n_shows"] > 0).sum()
    com_credenciamento = (df_o["n_credenciamentos"] > 0).sum()
    com_janela_aberta = df_o["janela_aberta"].sum()

    with ko1:
        st.metric("Municípios ranqueados", len(df_o))
    with ko2:
        st.metric("Abordar agora", abordar_agora)
    with ko3:
        st.metric("Janela aberta", com_janela_aberta, help="Contrataram no mesmo período do ano passado mas ainda não este ano")
    with ko4:
        st.metric("Com histórico de shows", com_historico)
    with ko5:
        st.metric("Credenciamento ativo", com_credenciamento, help="Municipios com edital de credenciamento aberto no PNCP")
    with ko6:
        st.metric("Score médio", f"{df_o['score'].mean():.1f}")
    with ko7:
        st.metric("Budget médio top 10", f"R$ {df_o.nlargest(10, 'score')['budget_medio'].mean():,.0f}".replace(",", "."))

    st.divider()

    # Filtros
    fo1, fo2, fo3, fo4, fo5 = st.columns([2, 2, 2, 2, 2])
    with fo1:
        meso_opts_o = ["Todas"] + sorted(df_o["mesorregiao"].unique().tolist())
        meso_sel_o = st.selectbox("Mesorregião", meso_opts_o, key="meso_opp")
    with fo2:
        janela_opts = ["Todas", "ABORDAR AGORA", "Em até 2 semanas", "Em 1-2 meses", "Sem urgência", "Sem evento mapeado"]
        janela_sel = st.selectbox("Janela comercial", janela_opts, key="janela_opp")
    with fo3:
        historico_sel = st.selectbox(
            "Histórico",
            ["Todos", "Com histórico", "Sem histórico"],
            key="hist_opp",
        )
    with fo4:
        janela_aberta_sel = st.selectbox(
            "Janela aberta",
            ["Todas", "Janela aberta", "Sem janela"],
            key="janela_aberta_opp",
            help="Municípios que contrataram no mesmo período do ano passado mas não ainda este ano",
        )
    with fo5:
        score_min = st.slider("Score mínimo", 0, 100, 0, key="score_opp")

    exibir_o = df_o.copy()
    if meso_sel_o != "Todas":
        exibir_o = exibir_o[exibir_o["mesorregiao"] == meso_sel_o]
    if janela_sel != "Todas":
        exibir_o = exibir_o[exibir_o["janela"] == janela_sel]
    if historico_sel == "Com histórico":
        exibir_o = exibir_o[exibir_o["n_shows"] > 0]
    elif historico_sel == "Sem histórico":
        exibir_o = exibir_o[exibir_o["n_shows"] == 0]
    if janela_aberta_sel == "Janela aberta":
        exibir_o = exibir_o[exibir_o["janela_aberta"] == True]
    elif janela_aberta_sel == "Sem janela":
        exibir_o = exibir_o[exibir_o["janela_aberta"] == False]
    exibir_o = exibir_o[exibir_o["score"] >= score_min]

    # Mapa de calor de oportunidades
    mapa_o = exibir_o.dropna(subset=["lat", "lon"]).copy()
    if not mapa_o.empty:
        mapa_o["score_fmt"] = mapa_o["score"].apply(lambda x: f"{x:.0f}/100")
        mapa_o["budget_fmt"] = mapa_o["budget_medio"].apply(
            lambda x: f"R$ {x:,.0f}".replace(",", ".") if x > 0 else "Não mapeado"
        )
        fig_mapa_o = px.scatter_mapbox(
            mapa_o,
            lat="lat",
            lon="lon",
            size="score",
            size_max=35,
            color="score",
            color_continuous_scale="RdYlGn",
            range_color=[0, 100],
            hover_name="municipio",
            hover_data={
                "lat": False,
                "lon": False,
                "score": False,
                "score_fmt": True,
                "janela": True,
                "n_shows": True,
                "budget_fmt": True,
                "artistas_sugeridos": True,
            },
            labels={
                "score_fmt": "Score",
                "janela": "Janela",
                "n_shows": "Shows históricos",
                "budget_fmt": "Budget médio",
                "artistas_sugeridos": "Artistas sugeridos",
            },
            mapbox_style="open-street-map",
            zoom=5.5,
            center={"lat": -20.5, "lon": -54.5},
            height=500,
            title="Mapa de Oportunidades — Score por Município",
        )
        fig_mapa_o.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig_mapa_o, use_container_width=True)

    st.divider()

    # Ranking
    st.subheader(f"Ranking de Oportunidades — {len(exibir_o)} municípios")

    exibir_o["status_label"] = exibir_o["status"].map(STATUS_LABELS_OPP).fillna(exibir_o["status"])
    exibir_o["estilo_label"] = exibir_o["estilo_dominante"].map(STYLE_LABELS).fillna(exibir_o["estilo_dominante"])
    exibir_o["valor_total_fmt"] = exibir_o["valor_total_shows"].apply(
        lambda x: f"R$ {x:,.0f}".replace(",", ".") if x > 0 else "—"
    )
    exibir_o["budget_fmt2"] = exibir_o["budget_medio"].apply(
        lambda x: f"R$ {x:,.0f}".replace(",", ".") if x > 0 else "—"
    )
    exibir_o["janela_aberta_icon"] = exibir_o["janela_aberta"].map({True: "Sim", False: ""})

    show_o = exibir_o[[
        "municipio", "decisor", "score", "n_credenciamentos", "janela_aberta_icon",
        "janela", "aniversario",
        "proximo_evento", "n_shows", "valor_total_fmt",
        "budget_fmt2", "artistas_sugeridos", "resumo", "status_label",
    ]].rename(columns={
        "municipio": "Município",
        "decisor": "Decisor",
        "score": "Score",
        "n_credenciamentos": "Cred.",
        "janela_aberta_icon": "Janela Aberta",
        "janela": "Janela Comercial",
        "aniversario": "Aniversário",
        "proximo_evento": "Próximo Evento",
        "n_shows": "Shows Hist.",
        "valor_total_fmt": "Total Gasto",
        "budget_fmt2": "Budget Médio/Show",
        "artistas_sugeridos": "Artistas Sugeridos",
        "resumo": "Por que abordar",
        "status_label": "Status",
    })

    st.dataframe(
        show_o,
        use_container_width=True,
        height=560,
        column_config={
            "Score": st.column_config.ProgressColumn(
                format="%.0f",
                min_value=0,
                max_value=100,
            ),
            "Shows Hist.": st.column_config.NumberColumn(format="%d"),
            "Cred.": st.column_config.NumberColumn(
                format="%d",
                help="Editais de credenciamento ativos no PNCP",
            ),
        },
    )

    csv_o = show_o.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "Exportar lista de oportunidades",
        data=csv_o,
        file_name="oportunidades_ms.csv",
        mime="text/csv",
        key="export_opp",
    )

    st.divider()

    # Editais de credenciamento ativos
    if not df_cred_notices.empty:
        n_cred_total = len(df_cred_notices)
        n_muni_cred = df_cred_notices["municipio"].nunique()
        with st.expander(
            f"Editais de Credenciamento Ativos — {n_cred_total} edital(is) em {n_muni_cred} município(s)",
            expanded=True,
        ):
            st.info(
                "Credenciamentos são editais onde o município convida fornecedores a se cadastrar "
                "para contratações futuras. Municipio com credenciamento aberto = sinal de compra imediato."
            )
            cred_show = df_cred_notices.copy()
            cred_show["valor_fmt"] = cred_show["valor"].apply(
                lambda x: f"R$ {x:,.0f}".replace(",", ".") if x > 0 else "—"
            )
            cred_show["publicado_fmt"] = pd.to_datetime(cred_show["publicado"]).dt.strftime("%d/%m/%Y").fillna("—")
            cred_show["encerramento_fmt"] = pd.to_datetime(cred_show["encerramento"]).dt.strftime("%d/%m/%Y").fillna("Em aberto")
            st.dataframe(
                cred_show[[
                    "municipio", "objeto", "publicado_fmt", "encerramento_fmt", "valor_fmt", "link"
                ]].rename(columns={
                    "municipio": "Município",
                    "objeto": "Objeto",
                    "publicado_fmt": "Publicado",
                    "encerramento_fmt": "Encerramento",
                    "valor_fmt": "Valor Estimado",
                    "link": "Link PNCP",
                }),
                use_container_width=True,
                column_config={
                    "Link PNCP": st.column_config.LinkColumn(display_text="Abrir"),
                },
            )
    else:
        with st.expander("Editais de Credenciamento Ativos — nenhum encontrado"):
            st.info(
                "Nenhum edital de credenciamento ativo. "
                "Execute `python scripts/run_accreditation_crawler.py` para buscar no PNCP."
            )

    st.divider()

    # Detalhe de um município
    st.subheader("Detalhes por Município")
    muni_sel = st.selectbox(
        "Selecionar município",
        exibir_o["municipio"].tolist(),
        key="muni_det_opp",
    )
    if muni_sel:
        row = exibir_o[exibir_o["municipio"] == muni_sel].iloc[0]

        dc1, dc2, dc3, dc4, dc5 = st.columns(5)
        with dc1:
            st.metric("Score", f"{row['score']:.0f}/100")
        with dc2:
            st.metric("Shows históricos", row["n_shows"])
        with dc3:
            st.metric("Total gasto", row["valor_total_fmt"])
        with dc4:
            st.metric("Budget médio/show", row["budget_fmt2"])
        with dc5:
            st.metric("Próximo evento", row["proximo_evento"])

        st.info(f"**Por que abordar:** {row['resumo']}")
        st.warning(f"**Próxima ação:** {row['proxima_acao']}")

        col_det1, col_det2 = st.columns(2)
        with col_det1:
            st.write("**Artistas sugeridos (top 3):**")
            if row["artistas_sugeridos"]:
                for nome in row["artistas_sugeridos"].split(", "):
                    st.write(f"- {nome}")
            else:
                st.write("Nenhum artista compatível no banco.")
        with col_det2:
            st.write("**Artistas que já atuaram na região:**")
            if row["artistas_regiao"]:
                for nome in row["artistas_regiao"].split(", "):
                    st.write(f"- {nome}")
            else:
                st.write("Nenhum identificado.")

        st.divider()
        st.write("**Decisores do município:**")
        ct_det = df_c_opp[df_c_opp["municipio"] == muni_sel]
        if ct_det.empty:
            st.caption("Nenhum contato cadastrado.")
        else:
            roles_ordem = ["prefeito", "secretario_cultura", "secretario_turismo"]
            for role in roles_ordem:
                ct_role = ct_det[ct_det["cargo"] == role]
                if ct_role.empty:
                    continue
                c_row = ct_role.iloc[0]
                label = CARGO_LABELS.get(role, role)
                nome_str = c_row["nome"] or "—"
                partido_str = f" ({c_row['partido']})" if c_row["partido"] else ""
                st.markdown(f"**{label}:** {nome_str}{partido_str}")
                info_parts = []
                if c_row["email"]:
                    info_parts.append(f"✉ {c_row['email']}")
                if c_row["telefone"]:
                    info_parts.append(f"☎ {c_row['telefone']}")
                if c_row["instagram"]:
                    info_parts.append(f"[Instagram]({c_row['instagram']})")
                if info_parts:
                    st.caption(" · ".join(info_parts))

# ── TAB 9: RELATÓRIOS COMERCIAIS ──────────────────────────────────────────────

@st.cache_data(ttl=120)
def load_eventos_municipio(municipio_nome: str) -> list[dict]:
    from app.models.municipal_event import MunicipalEvent
    db = SessionLocal()
    try:
        mun = db.query(Municipality).filter(Municipality.name == municipio_nome).first()
        if not mun:
            return []
        eventos = (
            db.query(MunicipalEvent)
            .filter(MunicipalEvent.municipality_id == mun.id)
            .order_by(MunicipalEvent.usual_month)
            .all()
        )
        return [
            {
                "nome": e.name,
                "tipo": e.event_type.value if e.event_type else "",
                "mes": e.usual_month,
                "inicio_est": e.estimated_start_date,
                "fim_est": e.estimated_end_date,
                "conf": e.confidence_score or 0.0,
            }
            for e in eventos
        ]
    finally:
        db.close()


@st.cache_data(ttl=120)
def load_contratos_municipio(municipio_nome: str) -> list[dict]:
    from app.models.public_contract import PublicContract
    db = SessionLocal()
    try:
        mun = db.query(Municipality).filter(Municipality.name == municipio_nome).first()
        if not mun:
            return []
        contratos = (
            db.query(PublicContract)
            .filter(PublicContract.municipality_id == mun.id)
            .order_by(PublicContract.publication_date.desc())
            .limit(20)
            .all()
        )
        records = []
        for c in contratos:
            llm = (c.extracted_json or {}).get("llm_extracted", {})
            records.append({
                "tipo": c.contract_type.value if c.contract_type else "",
                "modalidade": c.procurement_modality.value if c.procurement_modality else "",
                "fornecedor": c.supplier_name or "",
                "valor": float(c.contract_value) if c.contract_value else 0.0,
                "evento": llm.get("event_name") or "",
                "data_pub": c.publication_date,
                "objeto": (c.object_description or "")[:100],
            })
        return records
    finally:
        db.close()


def _gerar_html_relatorio(
    mun_row: pd.Series,
    contatos: list[dict],
    contratos: list[dict],
    eventos: list[dict],
    artistas_df: pd.DataFrame,
) -> str:
    nome = mun_row["municipio"]
    score = mun_row["score"]
    janela = mun_row["janela"]
    pop = mun_row["populacao"]
    meso = mun_row["mesorregiao"]
    n_shows = mun_row["n_shows"]
    valor_total = mun_row["valor_total_shows"]
    budget_medio = mun_row["budget_medio"]
    proxima_acao = mun_row["proxima_acao"]
    artistas_sug = mun_row["artistas_sugeridos"]
    artistas_reg = mun_row["artistas_regiao"]

    import datetime
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    # Score color
    if score >= 70:
        score_color = "#27ae60"
    elif score >= 45:
        score_color = "#f39c12"
    else:
        score_color = "#e74c3c"

    # Urgency badge
    if "AGORA" in janela:
        urgencia_badge = f'<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:12px;font-size:13px;">{janela}</span>'
    elif "semanas" in janela:
        urgencia_badge = f'<span style="background:#f39c12;color:white;padding:3px 10px;border-radius:12px;font-size:13px;">{janela}</span>'
    else:
        urgencia_badge = f'<span style="background:#95a5a6;color:white;padding:3px 10px;border-radius:12px;font-size:13px;">{janela}</span>'

    # Contatos section
    contatos_html = ""
    for c in contatos:
        cargo_label = CARGO_LABELS.get(c["cargo"], c["cargo"])
        telefone = c["telefone"] or "—"
        email = c["email"] or "—"
        contatos_html += f"""
        <tr>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;font-weight:600;">{cargo_label}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;">{c["nome"] or "—"}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;">{telefone}</td>
            <td style="padding:6px 10px;border-bottom:1px solid #eee;">{email}</td>
        </tr>"""

    if not contatos_html:
        contatos_html = '<tr><td colspan="4" style="padding:8px 10px;color:#999;">Nenhum contato cadastrado</td></tr>'

    # Contratos section
    contratos_html = ""
    valor_acum = 0.0
    for c in contratos[:10]:
        data_str = c["data_pub"].strftime("%m/%Y") if c["data_pub"] else "—"
        valor_str = f'R$ {c["valor"]:,.0f}'.replace(",", ".") if c["valor"] else "—"
        valor_acum += c["valor"]
        tipo_label = TIPO_LABELS.get(c["tipo"], c["tipo"])
        mod_label = c["modalidade"].replace("_", " ").capitalize() if c["modalidade"] else "—"
        contratos_html += f"""
        <tr>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{data_str}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{tipo_label}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{c["fornecedor"][:30] if c["fornecedor"] else "—"}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{valor_str}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{mod_label}</td>
        </tr>"""

    if not contratos_html:
        contratos_html = '<tr><td colspan="5" style="padding:8px 10px;color:#999;">Nenhum contrato encontrado</td></tr>'

    # Eventos section
    eventos_html = ""
    for e in eventos:
        mes_str = _mes_nome(e["mes"])
        tipo_str = e["tipo"].replace("_", " ").capitalize() if e["tipo"] else "—"
        data_str = e["inicio_est"].strftime("%d/%m/%Y") if e["inicio_est"] else "—"
        conf_pct = int(e["conf"] * 100)
        eventos_html += f"""
        <tr>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;font-weight:600;">{e["nome"]}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{tipo_str}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{mes_str}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{data_str}</td>
            <td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;">{conf_pct}%</td>
        </tr>"""

    if not eventos_html:
        eventos_html = '<tr><td colspan="5" style="padding:8px 10px;color:#999;">Nenhum evento mapeado</td></tr>'

    # Artistas sugeridos — enrich with fee info
    artistas_html = ""
    if artistas_sug:
        for nome_art in artistas_sug.split(", "):
            nome_art = nome_art.strip()
            match = artistas_df[artistas_df["nome"] == nome_art]
            if not match.empty:
                a = match.iloc[0]
                estilo_label = STYLE_LABELS.get(a["estilo"], a["estilo"])
                cache_label = FEE_TIER_LABELS.get(a["cache"], a["cache"])
                pop_label = POP_LABELS.get(a["popularidade"], a["popularidade"])
                ja_regiao = nome_art in (artistas_reg or "")
                regiao_badge = ' <span style="background:#27ae60;color:white;padding:1px 6px;border-radius:8px;font-size:11px;">Já na região</span>' if ja_regiao else ""
                artistas_html += f"""
                <tr>
                    <td style="padding:6px 10px;border-bottom:1px solid #eee;font-weight:600;">{nome_art}{regiao_badge}</td>
                    <td style="padding:6px 10px;border-bottom:1px solid #eee;">{estilo_label}</td>
                    <td style="padding:6px 10px;border-bottom:1px solid #eee;">{cache_label}</td>
                    <td style="padding:6px 10px;border-bottom:1px solid #eee;">{pop_label}</td>
                    <td style="padding:6px 10px;border-bottom:1px solid #eee;">{a["contratos"]} contrato(s)</td>
                </tr>"""
            else:
                artistas_html += f"""
                <tr>
                    <td style="padding:6px 10px;border-bottom:1px solid #eee;font-weight:600;">{nome_art}</td>
                    <td colspan="4" style="padding:6px 10px;border-bottom:1px solid #eee;color:#999;">—</td>
                </tr>"""

    if not artistas_html:
        artistas_html = '<tr><td colspan="5" style="padding:8px 10px;color:#999;">Nenhum artista sugerido</td></tr>'

    budget_str = f'R$ {budget_medio:,.0f}'.replace(",", ".") if budget_medio > 0 else "Não mapeado"
    valor_total_str = f'R$ {valor_total:,.0f}'.replace(",", ".") if valor_total > 0 else "—"
    pop_str = f'{pop:,}'.replace(",", ".")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Comercial — {nome}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 30px; color: #2c3e50; background: #fff; }}
  .header {{ background: linear-gradient(135deg, #1a252f 0%, #2c3e50 100%); color: white; padding: 28px 32px; border-radius: 10px; margin-bottom: 24px; }}
  .header h1 {{ margin: 0 0 6px 0; font-size: 26px; letter-spacing: 0.5px; }}
  .header .subtitle {{ opacity: 0.75; font-size: 13px; }}
  .score-badge {{ display: inline-block; background: {score_color}; color: white; font-size: 22px; font-weight: 700; padding: 8px 18px; border-radius: 8px; margin-right: 12px; }}
  .section {{ margin-bottom: 24px; }}
  .section-title {{ font-size: 15px; font-weight: 700; color: #1a252f; border-left: 4px solid #3498db; padding-left: 10px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }}
  .kpi-box {{ background: #f8f9fa; border-radius: 8px; padding: 14px 16px; border: 1px solid #e9ecef; }}
  .kpi-label {{ font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
  .kpi-value {{ font-size: 20px; font-weight: 700; color: #2c3e50; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ background: #f1f3f5; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 10px; text-align: left; }}
  .acao-box {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 14px 18px; font-weight: 600; color: #856404; }}
  .footer {{ margin-top: 32px; text-align: center; font-size: 11px; color: #adb5bd; border-top: 1px solid #e9ecef; padding-top: 16px; }}
  @media print {{ body {{ padding: 15px; }} }}
</style>
</head>
<body>

<div class="header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <h1>{nome}</h1>
      <div class="subtitle">{meso} &nbsp;|&nbsp; {pop_str} habitantes &nbsp;|&nbsp; Gerado em {hoje}</div>
    </div>
    <div style="text-align:right;">
      <div class="score-badge">{score:.0f}/100</div>
      {urgencia_badge}
    </div>
  </div>
</div>

<div class="kpi-grid">
  <div class="kpi-box">
    <div class="kpi-label">Shows Históricos</div>
    <div class="kpi-value">{n_shows}</div>
  </div>
  <div class="kpi-box">
    <div class="kpi-label">Total Gasto (shows)</div>
    <div class="kpi-value" style="font-size:16px;">{valor_total_str}</div>
  </div>
  <div class="kpi-box">
    <div class="kpi-label">Budget Médio/Show</div>
    <div class="kpi-value" style="font-size:16px;">{budget_str}</div>
  </div>
  <div class="kpi-box">
    <div class="kpi-label">Eventos Mapeados</div>
    <div class="kpi-value">{len(eventos)}</div>
  </div>
</div>

<div class="section">
  <div class="section-title">Proxima Acao Recomendada</div>
  <div class="acao-box">{proxima_acao or "Iniciar prospecção — ligar para secretaria de cultura/turismo"}</div>
</div>

<div class="section">
  <div class="section-title">Contatos da Prefeitura</div>
  <table>
    <tr>
      <th>Cargo</th><th>Nome</th><th>Telefone</th><th>E-mail</th>
    </tr>
    {contatos_html}
  </table>
</div>

<div class="section">
  <div class="section-title">Artistas Sugeridos</div>
  <table>
    <tr>
      <th>Artista</th><th>Estilo</th><th>Cache</th><th>Popularidade</th><th>Historico MS</th>
    </tr>
    {artistas_html}
  </table>
</div>

<div class="section">
  <div class="section-title">Eventos Municipais Mapeados</div>
  <table>
    <tr>
      <th>Evento</th><th>Tipo</th><th>Mes Usual</th><th>Data Est.</th><th>Confianca</th>
    </tr>
    {eventos_html}
  </table>
</div>

<div class="section">
  <div class="section-title">Historico de Contratos (ultimos 10)</div>
  <table>
    <tr>
      <th>Data</th><th>Tipo</th><th>Fornecedor</th><th>Valor</th><th>Modalidade</th>
    </tr>
    {contratos_html}
  </table>
</div>

<div class="footer">
  Sell Produtora — Sistema de Inteligencia Comercial &nbsp;|&nbsp; Dados: PNCP / TSE / fontes publicas &nbsp;|&nbsp; {hoje}
</div>
</body>
</html>"""
    return html


def _gerar_plano_semanal_html(df_top: pd.DataFrame, df_contatos: pd.DataFrame) -> str:
    import datetime
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    linhas_html = ""
    for i, row in enumerate(df_top.itertuples(), 1):
        mun_nome = row.municipio
        score = row.score
        janela = row.janela
        budget = row.budget_medio
        proxima = row.proxima_acao
        n_shows = row.n_shows

        # Pegar contato principal
        contato_mun = df_contatos[df_contatos["municipio"] == mun_nome]
        contato_pref = contato_mun[contato_mun["cargo"] == "prefeito"]
        contato_sec = contato_mun[contato_mun["cargo"].isin(["secretario_cultura", "secretario_turismo"])]

        if not contato_pref.empty:
            c = contato_pref.iloc[0]
            contato_str = f"{c['nome'] or 'Prefeito'} | {c['telefone'] or c['email'] or '—'}"
        elif not contato_sec.empty:
            c = contato_sec.iloc[0]
            cargo_label = CARGO_LABELS.get(c["cargo"], c["cargo"])
            contato_str = f"{c['nome'] or cargo_label} | {c['telefone'] or c['email'] or '—'}"
        else:
            contato_str = "Contato não cadastrado"

        if "AGORA" in janela:
            row_bg = "#fff5f5"
            janela_color = "#e74c3c"
        elif "semanas" in janela:
            row_bg = "#fffbf0"
            janela_color = "#f39c12"
        else:
            row_bg = "#f8f9fa"
            janela_color = "#6c757d"

        budget_str = f'R$ {budget:,.0f}'.replace(",", ".") if budget > 0 else "—"
        hist_str = f"{n_shows} show(s)" if n_shows > 0 else "Sem histórico"

        linhas_html += f"""
        <tr style="background:{row_bg};">
          <td style="padding:10px 12px;font-weight:700;font-size:15px;color:#1a252f;">{i}. {mun_nome}</td>
          <td style="padding:10px 12px;">
            <span style="color:{janela_color};font-weight:600;">{janela}</span>
          </td>
          <td style="padding:10px 12px;font-weight:700;color:#2c3e50;">{score:.0f}/100</td>
          <td style="padding:10px 12px;font-size:13px;">{contato_str}</td>
          <td style="padding:10px 12px;font-size:13px;color:#6c757d;">{hist_str} | {budget_str}</td>
          <td style="padding:10px 12px;font-size:13px;color:#856404;">{proxima or "—"}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Plano Semanal — Sell Produtora</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 30px; color: #2c3e50; background: #fff; }}
  .header {{ background: linear-gradient(135deg, #1a252f 0%, #2c3e50 100%); color: white; padding: 24px 32px; border-radius: 10px; margin-bottom: 28px; }}
  .header h1 {{ margin: 0; font-size: 24px; }}
  .header .sub {{ opacity: 0.7; font-size: 13px; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ background: #2c3e50; color: white; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; padding: 10px 12px; text-align: left; }}
  tr:hover {{ filter: brightness(0.97); }}
  .footer {{ margin-top: 28px; text-align: center; font-size: 11px; color: #adb5bd; border-top: 1px solid #e9ecef; padding-top: 16px; }}
  @media print {{ body {{ padding: 15px; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>Plano Semanal de Prospecção</h1>
  <div class="sub">Sell Produtora &nbsp;|&nbsp; Top oportunidades por urgência + score &nbsp;|&nbsp; {hoje}</div>
</div>
<table>
  <tr>
    <th>Município</th>
    <th>Janela</th>
    <th>Score</th>
    <th>Contato Principal</th>
    <th>Histórico / Budget</th>
    <th>Próxima Ação</th>
  </tr>
  {linhas_html}
</table>
<div class="footer">
  Sell Produtora — Sistema de Inteligencia Comercial &nbsp;|&nbsp; {hoje}
</div>
</body>
</html>"""
    return html


with tab_rel:
    sub_rel, sub_plano, sub_pipeline, sub_radar, sub_do = st.tabs(
        ["Relatório por Município", "Plano Semanal", "Pipeline", "Radar de Oportunidades", "Alertas DO"]
    )

    # ── SUB-TAB: RELATÓRIO POR MUNICÍPIO ──────────────────────────────────────
    with sub_rel:
        st.subheader("Relatório de Prospecção por Município")
        st.caption(
            "Selecione um município para gerar um relatório completo com histórico de contratos, "
            "eventos, artistas sugeridos e contatos — exportável como HTML (salve como PDF pelo browser)."
        )

        df_opp_rel = load_opportunities()
        df_art_rel = load_artists()
        df_cont_rel = load_contacts()

        if df_opp_rel.empty:
            st.info("Nenhuma oportunidade calculada. Execute `python scripts/run_opportunity_engine.py`.")
        else:
            municipios_ordenados = df_opp_rel.sort_values("score", ascending=False)["municipio"].tolist()
            muni_rel = st.selectbox(
                "Município",
                municipios_ordenados,
                key="muni_relatorio",
                help="Municípios ordenados por score de oportunidade (maior primeiro)",
            )

            if muni_rel:
                mun_row_rel = df_opp_rel[df_opp_rel["municipio"] == muni_rel].iloc[0]

                # Métricas rápidas
                mr1, mr2, mr3, mr4 = st.columns(4)
                with mr1:
                    st.metric("Score", f"{mun_row_rel['score']:.0f}/100")
                with mr2:
                    st.metric("Janela", mun_row_rel["janela"])
                with mr3:
                    budget_rel = mun_row_rel["budget_medio"]
                    st.metric("Budget médio", f"R$ {budget_rel:,.0f}".replace(",", ".") if budget_rel > 0 else "—")
                with mr4:
                    st.metric("Shows históricos", mun_row_rel["n_shows"])

                st.divider()

                col_btn, col_info = st.columns([1, 3])
                with col_btn:
                    if st.button("Gerar Relatório HTML", type="primary", key="btn_rel_html"):
                        with st.spinner("Gerando relatório..."):
                            contatos_rel = df_cont_rel[df_cont_rel["municipio"] == muni_rel].to_dict("records")
                            contratos_rel = load_contratos_municipio(muni_rel)
                            eventos_rel = load_eventos_municipio(muni_rel)
                            html_rel = _gerar_html_relatorio(
                                mun_row_rel, contatos_rel, contratos_rel, eventos_rel, df_art_rel
                            )
                            nome_arq = f"relatorio_{muni_rel.lower().replace(' ', '_')}.html"
                            st.download_button(
                                label="Baixar HTML",
                                data=html_rel.encode("utf-8"),
                                file_name=nome_arq,
                                mime="text/html",
                                key="dl_rel_html",
                            )
                            st.success("Relatório gerado. Clique em 'Baixar HTML' para salvar.")

                            # Preview inline
                            with st.expander("Preview do relatório", expanded=True):
                                st.components.v1.html(html_rel, height=900, scrolling=True)
                with col_info:
                    st.info(
                        "Clique em **Gerar Relatório HTML** para criar o documento. "
                        "Após baixar, abra no navegador e use **Ctrl+P → Salvar como PDF** para exportar em PDF."
                    )

    # ── SUB-TAB: PLANO SEMANAL ────────────────────────────────────────────────
    with sub_plano:
        st.subheader("Plano Semanal de Prospecção")
        st.caption(
            "Top oportunidades a abordar nesta semana, ordenadas por urgência e score. "
            "Exportável como HTML ou CSV."
        )

        df_opp_ps = load_opportunities()
        df_cont_ps = load_contacts()

        if df_opp_ps.empty:
            st.info("Nenhuma oportunidade calculada.")
        else:
            ps1, ps2 = st.columns([1, 3])
            with ps1:
                n_top = st.selectbox("Quantidade", [5, 10, 15, 20], index=1, key="ps_ntop")
            with ps2:
                meso_ps = st.selectbox(
                    "Filtrar por mesorregião",
                    ["Todas"] + sorted(df_opp_ps["mesorregiao"].unique().tolist()),
                    key="ps_meso",
                )

            df_ps = df_opp_ps.copy()
            if meso_ps != "Todas":
                df_ps = df_ps[df_ps["mesorregiao"] == meso_ps]

            # Ordenar: urgência primeiro, depois score
            df_ps["urgencia_rank"] = df_ps["urgencia"].rank(ascending=False, method="first")
            df_ps["score_rank"] = df_ps["score"].rank(ascending=False, method="first")
            df_ps["rank_final"] = df_ps["urgencia_rank"] * 0.6 + df_ps["score_rank"] * 0.4
            df_top_ps = df_ps.nsmallest(n_top, "rank_final")

            # Exibir tabela resumida
            show_ps = df_top_ps[[
                "municipio", "janela", "score", "n_shows", "budget_medio", "proxima_acao"
            ]].copy()
            show_ps["budget_fmt"] = show_ps["budget_medio"].apply(
                lambda x: f"R$ {x:,.0f}".replace(",", ".") if x > 0 else "—"
            )
            show_ps_display = show_ps[[
                "municipio", "janela", "score", "n_shows", "budget_fmt", "proxima_acao"
            ]].rename(columns={
                "municipio": "Município",
                "janela": "Janela",
                "score": "Score",
                "n_shows": "Shows Hist.",
                "budget_fmt": "Budget Médio",
                "proxima_acao": "Próxima Ação",
            })

            st.dataframe(
                show_ps_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=100),
                },
            )

            st.divider()

            col_h, col_c = st.columns(2)
            with col_h:
                if st.button("Gerar Plano HTML", type="primary", key="btn_plano_html"):
                    with st.spinner("Gerando plano..."):
                        html_plano = _gerar_plano_semanal_html(df_top_ps, df_cont_ps)
                        st.download_button(
                            label="Baixar Plano HTML",
                            data=html_plano.encode("utf-8"),
                            file_name="plano_semanal_sell.html",
                            mime="text/html",
                            key="dl_plano_html",
                        )
                        with st.expander("Preview do plano", expanded=True):
                            st.components.v1.html(html_plano, height=700, scrolling=True)
            with col_c:
                csv_ps = show_ps_display.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button(
                    "Exportar CSV",
                    data=csv_ps,
                    file_name="plano_semanal_sell.csv",
                    mime="text/csv",
                    key="dl_plano_csv",
                )

    # ── SUB-TAB: PIPELINE ─────────────────────────────────────────────────────
    with sub_pipeline:
        st.subheader("Pipeline Comercial")

        df_opp_pip = load_opportunities()

        if df_opp_pip.empty:
            st.info("Nenhuma oportunidade calculada.")
        else:
            # Funil por status
            status_counts = df_opp_pip["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            status_counts["label"] = status_counts["status"].map(STATUS_LABELS_OPP).fillna(status_counts["status"])
            status_counts["cor"] = status_counts["status"].map(STATUS_CORES).fillna("#cccccc")

            pip1, pip2 = st.columns([1, 1])

            with pip1:
                fig_status = px.bar(
                    status_counts,
                    x="count",
                    y="label",
                    orientation="h",
                    color="label",
                    color_discrete_map={row["label"]: row["cor"] for _, row in status_counts.iterrows()},
                    title="Municípios por Status no Pipeline",
                    labels={"count": "Quantidade", "label": "Status"},
                    height=350,
                )
                fig_status.update_layout(showlegend=False, yaxis_title="", xaxis_title="Municípios")
                st.plotly_chart(fig_status, use_container_width=True)

            with pip2:
                # Distribuição por mesorregião
                meso_scores = df_opp_pip.groupby("mesorregiao").agg(
                    score_medio=("score", "mean"),
                    n_municipios=("municipio", "count"),
                    urgentes=("urgencia", lambda x: (x >= 0.9).sum()),
                ).reset_index()

                fig_meso = px.bar(
                    meso_scores.sort_values("score_medio", ascending=True),
                    x="score_medio",
                    y="mesorregiao",
                    orientation="h",
                    color="urgentes",
                    color_continuous_scale="OrRd",
                    title="Score Médio por Mesorregião",
                    labels={"score_medio": "Score Médio", "mesorregiao": "", "urgentes": "Urgentes"},
                    text="score_medio",
                    height=350,
                )
                fig_meso.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                fig_meso.update_layout(xaxis_range=[0, 100])
                st.plotly_chart(fig_meso, use_container_width=True)

            st.divider()

            # KPIs do pipeline
            kp1, kp2, kp3, kp4, kp5 = st.columns(5)
            with kp1:
                total_pip = len(df_opp_pip)
                st.metric("Total no pipeline", total_pip)
            with kp2:
                urgentes_pip = (df_opp_pip["urgencia"] >= 0.9).sum()
                st.metric("Abordar agora", urgentes_pip)
            with kp3:
                com_hist = (df_opp_pip["n_shows"] > 0).sum()
                st.metric("Com histórico", com_hist)
            with kp4:
                valor_potencial = df_opp_pip[df_opp_pip["budget_medio"] > 0]["budget_medio"].sum()
                st.metric("Potencial total", f"R$ {valor_potencial:,.0f}".replace(",", "."))
            with kp5:
                score_medio_pip = df_opp_pip["score"].mean()
                st.metric("Score médio", f"{score_medio_pip:.1f}")

            st.divider()

            # Tabela completa do pipeline com janela e status
            st.markdown("**Visão completa do pipeline**")
            pip_display = df_opp_pip[[
                "municipio", "mesorregiao", "score", "janela", "status", "n_shows", "budget_medio", "proxima_acao"
            ]].copy()
            pip_display["status_label"] = pip_display["status"].map(STATUS_LABELS_OPP).fillna(pip_display["status"])
            pip_display["budget_fmt"] = pip_display["budget_medio"].apply(
                lambda x: f"R$ {x:,.0f}".replace(",", ".") if x > 0 else "—"
            )
            pip_table = pip_display[[
                "municipio", "mesorregiao", "score", "janela", "status_label", "n_shows", "budget_fmt", "proxima_acao"
            ]].rename(columns={
                "municipio": "Município",
                "mesorregiao": "Mesorregião",
                "score": "Score",
                "janela": "Janela",
                "status_label": "Status",
                "n_shows": "Shows Hist.",
                "budget_fmt": "Budget Médio",
                "proxima_acao": "Próxima Ação",
            })
            st.dataframe(
                pip_table,
                use_container_width=True,
                height=500,
                column_config={
                    "Score": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=100),
                },
            )

            csv_pip = pip_table.to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button(
                "Exportar pipeline CSV",
                data=csv_pip,
                file_name="pipeline_sell.csv",
                mime="text/csv",
                key="dl_pipeline_csv",
            )

    # ── SUB-TAB: RADAR DE OPORTUNIDADES ───────────────────────────────────────
    with sub_radar:
        st.subheader("Radar de Oportunidades Abertas")
        st.caption(
            "Eventos anuais recorrentes previstos nos proximos meses, com historico de "
            "contratos do mesmo periodo em 2025 e sem contrato publicado em 2026 ainda. "
            "Uma linha por evento — os contratos sao especificos do mes daquele evento (+-1 mes)."
        )

        janela_sel = st.slider(
            "Janela de meses a frente",
            min_value=2, max_value=9, value=6, step=1,
            key="radar_janela",
            help="Quantos meses a frente verificar. Ex: 6 = olha de hoje ate dezembro.",
        )

        df_radar = load_radar_oportunidades(janela_meses=janela_sel)

        if df_radar.empty:
            st.info("Nenhuma oportunidade aberta identificada nesta janela.")
        else:
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric(
                "Eventos anuais com janela aberta",
                len(df_radar),
                help="Eventos recorrentes previstos na janela sem contrato publicado em 2026",
            )
            col_r2.metric(
                "Contratos historicos (mesmo mes 2025)",
                int(df_radar["n_contratos_lp"].sum()),
                help="Contratos publicados no mesmo mes (+-1) de cada evento em 2025",
            )
            total_orc = df_radar["orcamento_total_lp"].sum()
            col_r3.metric(
                "Orcamento historico total",
                f"R$ {total_orc / 1_000:.0f}k" if total_orc < 1_000_000 else f"R$ {total_orc / 1_000_000:.1f}M",
                help="Soma dos valores dos contratos do mesmo periodo em 2025",
            )

            st.markdown("---")

            # Filtros
            fc1, fc2 = st.columns(2)
            with fc1:
                mesos_disp = ["Todas"] + sorted(df_radar["mesorregiao"].dropna().unique().tolist())
                meso_filt = st.selectbox("Mesorregiao", mesos_disp, key="radar_meso")
            with fc2:
                meses_disp = ["Todos"] + sorted(df_radar["mes_nome"].unique().tolist())
                mes_filt = st.selectbox("Mes previsto", meses_disp, key="radar_mes")

            df_show_r = df_radar.copy()
            if meso_filt != "Todas":
                df_show_r = df_show_r[df_show_r["mesorregiao"] == meso_filt]
            if mes_filt != "Todos":
                df_show_r = df_show_r[df_show_r["mes_nome"] == mes_filt]

            st.markdown(f"**{len(df_show_r)} municipio(s) listado(s)**")

            colunas_exib = {
                "municipio": "Municipio",
                "evento": "Evento esperado",
                "mes_nome": "Mes",
                "n_contratos_lp": "Contratos 2025",
                "orcamento_medio": "Orc. medio 2025",
                "fornecedores_lp": "Quem contratou em 2025",
                "contato_nome": "Contato",
                "contato_cargo": "Cargo",
                "contato_email": "Email",
                "score": "Score",
            }
            tabela_radar = df_show_r[list(colunas_exib.keys())].rename(columns=colunas_exib)

            st.dataframe(
                tabela_radar,
                use_container_width=True,
                height=500,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Score", min_value=0, max_value=100, format="%.0f"
                    ),
                    "Orc. medio 2025": st.column_config.NumberColumn(
                        "Orc. medio 2025", format="R$ %.0f"
                    ),
                    "Contratos 2025": st.column_config.NumberColumn(
                        "Contr. 2025", format="%d"
                    ),
                },
                hide_index=True,
            )

            csv_radar = tabela_radar.to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button(
                "Exportar Radar CSV",
                data=csv_radar,
                file_name="radar_oportunidades_sell.csv",
                mime="text/csv",
                key="dl_radar_csv",
            )

    # ── SUB-TAB: ALERTAS DO ────────────────────────────────────────────────────
    with sub_do:
        st.subheader("Alertas — Diário Oficial (DOE/MS + DIOGRANDE)")
        st.caption(
            "Contratações de shows/artistas publicadas nos Diários Oficiais. "
            "DOE = Diário Oficial do Estado (com contexto). DIOGRANDE = Campo Grande (edição-nível, PDF pendente)."
        )

        col_do1, col_do2, col_do3 = st.columns([2, 1, 1])
        with col_do1:
            dias_do = st.slider("Janela de dias", min_value=7, max_value=365, value=30, step=7, key="do_dias")
        with col_do2:
            tipo_do = st.selectbox("Tipo", ["Todos", "Inexigibilidade", "Dispensa", "Pregao", "Potencial"], key="do_tipo")
        with col_do3:
            fonte_do = st.selectbox("Fonte", ["Todas", "DOE", "DIOGRANDE"], key="do_fonte")

        df_do = load_diario_alertas(dias=dias_do)

        if df_do.empty:
            st.info(
                "Nenhum alerta no periodo. Execute `python scripts/run_diario_crawler.py` "
                "e `python scripts/run_diogrande_crawler.py` para coletar publicacoes recentes."
            )
        else:
            df_do_fil = df_do.copy()
            if tipo_do != "Todos":
                df_do_fil = df_do_fil[df_do_fil["tipo"].str.lower() == tipo_do.lower()]
            if fonte_do != "Todas":
                df_do_fil = df_do_fil[df_do_fil["fonte"] == fonte_do]

            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            inex_cnt = len(df_do[df_do["tipo"].str.lower() == "inexigibilidade"])
            doe_cnt = len(df_do[df_do["fonte"] == "DOE"])
            dg_cnt  = len(df_do[df_do["fonte"] == "DIOGRANDE"])
            munis_uniq = df_do[df_do["municipio_id"].notna()]["municipio"].nunique()
            col_kpi1.metric("Total alertas", len(df_do))
            col_kpi2.metric("Inexigibilidade (DOE)", inex_cnt)
            col_kpi3.metric("DOE / DIOGRANDE", f"{doe_cnt} / {dg_cnt}")
            col_kpi4.metric("Municípios", munis_uniq)

            st.dataframe(
                df_do_fil[["data", "fonte", "municipio", "artista", "tipo", "keyword", "contexto", "confianca"]].rename(columns={
                    "data": "Data",
                    "fonte": "Fonte",
                    "municipio": "Município",
                    "artista": "Artista/Banda",
                    "tipo": "Tipo",
                    "keyword": "Termo",
                    "contexto": "Contexto",
                    "confianca": "Conf.%",
                }),
                use_container_width=True,
                height=450,
                column_config={
                    "Conf.%": st.column_config.ProgressColumn("Conf.%", min_value=0, max_value=100, format="%d%%"),
                },
                hide_index=True,
            )

            csv_do = df_do_fil.to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button("Exportar Alertas CSV", data=csv_do,
                               file_name="alertas_do_sell.csv", mime="text/csv", key="dl_do_csv")
