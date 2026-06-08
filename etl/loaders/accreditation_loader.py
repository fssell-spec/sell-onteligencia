"""Persiste editais de credenciamento do PNCP no banco de dados."""
from datetime import date

from sqlalchemy.orm import Session

from app.models.accreditation_notice import AccreditationNotice
from app.models.municipality import Municipality
from crawlers.pncp.collector import CollectedContract
from crawlers.pncp.keywords import classify


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _extract_encerramento(raw: dict) -> date | None:
    """Tenta extrair a data de encerramento do edital a partir do JSON bruto."""
    for field in (
        "dataEncerramentoProposta",
        "dataEncerramentoPropostas",
        "dataAberturaPropostas",
        "dataEncerramentoPrazoImpugnacao",
    ):
        val = raw.get(field)
        if val:
            return _parse_date(str(val))
    return None


def build_ibge_map(db: Session) -> dict[str, int]:
    rows = db.query(Municipality.ibge_code, Municipality.id).all()
    return {row.ibge_code: row.id for row in rows if row.ibge_code}


def save_accreditations(
    db: Session,
    contracts: list[CollectedContract],
    ibge_map: dict[str, int],
) -> tuple[int, int]:
    """Persiste editais de credenciamento; retorna (criados, ignorados_duplicatas)."""
    today = date.today()
    created = skipped = 0

    for cc in contracts:
        item = cc.item
        numero = item.numero_controle or ""
        if not numero:
            skipped += 1
            continue

        exists = (
            db.query(AccreditationNotice.id)
            .filter(AccreditationNotice.numero_controle == numero)
            .first()
        )
        if exists:
            skipped += 1
            continue

        municipality_id = ibge_map.get(item.ibge_code) if item.ibge_code else None
        if not municipality_id:
            skipped += 1
            continue

        data_enc = _extract_encerramento(item.raw)
        is_active = data_enc is None or data_enc >= today

        contract_type = classify(item.objeto or "")
        contract_types_json = {"tipo_principal": contract_type.value}

        notice = AccreditationNotice(
            municipality_id=municipality_id,
            numero_controle=numero[:255],
            objeto=item.objeto[:4000] if item.objeto else None,
            valor_estimado=item.valor_estimado,
            data_publicacao=_parse_date(item.data_publicacao),
            data_encerramento=data_enc,
            is_active=is_active,
            contract_types_json=contract_types_json,
            orgao_cnpj=(item.orgao_cnpj or "")[:20] or None,
            orgao_nome=(item.orgao_nome or "")[:500] or None,
            raw_json=item.raw,
        )
        db.add(notice)
        created += 1

    db.commit()
    return created, skipped
