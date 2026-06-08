"""
Classifica eventos extraídos dos contratos PNCP e popula municipal_events.
Detecta recorrência agrupando eventos similares por município.
"""
import re
import unicodedata
from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.models.diario_oficial_hit import DiarioOficialHit
from app.models.enums import EventType
from app.models.municipal_event import MunicipalEvent
from app.models.public_contract import PublicContract


KEYWORDS: dict[EventType, list[str]] = {
    EventType.aniversario_cidade: [
        "aniversario", "aniversário", "fundacao", "fundação", "emancipacao",
        "emancipação", "aniver", "natalicio", "natalício",
    ],
    EventType.carnaval: ["carnaval", "bloco", "pre carnaval", "pré carnaval", "micareta"],
    EventType.reveillon: ["reveillon", "réveillon", "ano novo", "virada", "31 de dezembro"],
    EventType.festa_peao: [
        "peao", "peão", "rodeio peao", "festa do peao", "cowboy", "vaqueiro",
    ],
    EventType.rodeio: [
        "rodeio", "expo", "exposicao", "exposição", "agropecuaria", "agropecuária",
        "cavalgada", "cavalo", "equestre", "leilao", "leilão",
    ],
    EventType.expoagro: [
        "expoagro", "show rural", "feira agro", "agronegocio", "agronegócio",
        "agricola", "agrícola",
    ],
    EventType.festival_cultural: [
        "festival", "cultura", "cultural", "arte", "teatro", "danca", "dança",
        "musica", "música", "circo", "folclore", "folclórico",
    ],
    EventType.festa_tradicional: [
        "sao joao", "são joão", "festa junina", "arraial", "sao pedro", "são pedro",
        "padroeiro", "padroeira", "natal", "festejo", "tradicional", "folclórica",
        "marcha", "jesus",
    ],
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def classify_event(event_name: str) -> EventType:
    norm = _normalize(event_name)
    for event_type, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in norm:
                return event_type
    return EventType.outro


def extract_event_name(object_description: str) -> str | None:
    """Extrai nome do evento de descrições no formato 'Artista: X | Evento: Y'."""
    if not object_description:
        return None
    match = re.search(r"Evento:\s*(.+?)(?:\||$)", object_description, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def classify_and_seed(db: Session) -> int:
    """Popula municipal_events a partir dos contratos extraídos pelo LLM."""
    db.query(MunicipalEvent).delete()
    db.flush()

    contracts = (
        db.query(PublicContract)
        .filter(PublicContract.municipality_id.isnot(None))
        .all()
    )

    groups: dict[tuple[int, str], list[PublicContract]] = defaultdict(list)
    for c in contracts:
        event_name = extract_event_name(c.object_description or "")
        if not event_name:
            llm = (c.extracted_json or {}).get("llm_extracted", {})
            event_name = llm.get("event_name") or llm.get("evento")
        if not event_name:
            continue
        norm_name = _normalize(event_name)
        key = (c.municipality_id, norm_name[:30])
        groups[key].append(c)

    created = 0
    for (muni_id, _), group_contracts in groups.items():
        event_name = max(
            (extract_event_name(c.object_description or "") or "" for c in group_contracts),
            key=len,
        )
        if not event_name:
            continue

        event_type = classify_event(event_name)

        months = [c.event_date.month for c in group_contracts if c.event_date]
        usual_month = max(set(months), key=months.count) if months else None

        dates = sorted([c.event_date for c in group_contracts if c.event_date])
        last_date = dates[-1] if dates else None

        n = len(group_contracts)
        recurrence = "anual" if n >= 2 else "unico"
        confidence = min(0.5 + n * 0.1, 1.0)

        me = MunicipalEvent(
            municipality_id=muni_id,
            name=event_name[:255],
            normalized_name=_normalize(event_name)[:255],
            event_type=event_type,
            usual_month=usual_month,
            estimated_start_date=last_date,
            recurrence_pattern=recurrence,
            confidence_score=confidence,
        )
        db.add(me)
        created += 1

    db.commit()
    return created


def seed_from_diario(db: Session) -> int:
    """
    Cria MunicipalEvent a partir dos hits do Diário Oficial que têm município detectado.
    Agrupa hits por (municipio_id, mês) para inferir recorrência anual.
    Só cria eventos para municípios que ainda não têm eventos vindos de contratos.
    """
    existing_muni_ids = {
        row[0]
        for row in db.query(MunicipalEvent.municipality_id).distinct().all()
    }

    hits = (
        db.query(DiarioOficialHit)
        .filter(
            DiarioOficialHit.municipio_id.isnot(None),
            DiarioOficialHit.status == "novo",
        )
        .all()
    )

    groups: dict[tuple[int, int], list[DiarioOficialHit]] = defaultdict(list)
    for h in hits:
        if not h.data_publicacao or len(h.data_publicacao) < 7:
            continue
        try:
            month = int(h.data_publicacao[5:7])
        except ValueError:
            continue
        groups[(h.municipio_id, month)].append(h)

    muni_months: dict[int, list[tuple[int, list[DiarioOficialHit]]]] = defaultdict(list)
    for (muni_id, month), group_hits in groups.items():
        muni_months[muni_id].append((month, group_hits))

    created = 0
    for muni_id, month_groups in muni_months.items():
        if muni_id in existing_muni_ids:
            continue

        for month, group_hits in month_groups:
            sample_text = " ".join(
                h.highlight or h.keyword for h in group_hits[:3]
            )
            event_type = classify_event(sample_text)

            artists = [h.artista_detectado for h in group_hits if h.artista_detectado]
            event_name = "Show/Evento " + date(2000, month, 1).strftime("%B")
            if artists:
                artist_counts: dict[str, int] = defaultdict(int)
                for a in artists:
                    artist_counts[a] += 1
                top_artist = max(artist_counts, key=lambda x: artist_counts[x])
                event_name = "Evento com " + top_artist

            n = len(group_hits)
            recurrence = "anual" if n >= 2 else "unico"
            confidence = min(0.3 + n * 0.1, 0.8)

            me = MunicipalEvent(
                municipality_id=muni_id,
                name=event_name[:255],
                normalized_name=_normalize(event_name)[:255],
                event_type=event_type,
                usual_month=month,
                recurrence_pattern=recurrence,
                confidence_score=confidence,
            )
            db.add(me)
            created += 1

    db.commit()
    return created
