"""Persiste contratos coletados do PNCP no banco de dados."""
import re
import unicodedata
from datetime import date

from sqlalchemy.orm import Session

from app.models.enums import ContractType, ProcurementModality
from app.models.municipality import Municipality
from app.models.public_contract import PublicContract
from crawlers.pncp.collector import CollectedContract

_MODALITY_MAP = {
    4: ProcurementModality.concorrencia,
    5: ProcurementModality.concorrencia,
    6: ProcurementModality.pregao,
    7: ProcurementModality.pregao,
    8: ProcurementModality.dispensa,
    9: ProcurementModality.inexigibilidade,
}

# Padrões para extrair município destino do texto do contrato
# Ex: "no município de Brasilândia-MS", "em Caracol-MS", "no Município de Cassilândia/MS"
_MUNI_PATTERNS = [
    re.compile(r"(?:no\s+município\s+de|em|no\s+munic[íi]pio\s+de)\s+([A-ZÀ-Ú][a-zA-ZÀ-ú\s]+?)(?:\s*[-/]\s*MS|\s*,|\s*\.|\s+pelo|\s+por|\s+para|\s*$)", re.IGNORECASE),
    re.compile(r"([A-ZÀ-Ú][a-zA-ZÀ-ú\s]+?)\s*[-/]\s*MS\b"),
]


def _normalize(text: str) -> str:
    """Remove acentos e coloca em minúsculas para comparação."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()


def _extract_municipality_id(
    texto: str,
    name_map: dict[str, int],
    fallback_id: int | None,
) -> int | None:
    """Tenta extrair o município destino do texto; retorna fallback se não encontrar."""
    if not texto:
        return fallback_id
    for pattern in _MUNI_PATTERNS:
        for match in pattern.finditer(texto):
            candidate = _normalize(match.group(1).strip())
            if candidate in name_map:
                return name_map[candidate]
    return fallback_id


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def build_ibge_map(db: Session) -> dict[str, int]:
    """Retorna {ibge_code: municipality.id} para todos os municípios."""
    rows = db.query(Municipality.ibge_code, Municipality.id).all()
    return {row.ibge_code: row.id for row in rows if row.ibge_code}


def build_name_map(db: Session) -> dict[str, int]:
    """Retorna {normalized_name: municipality.id} para todos os municípios."""
    rows = db.query(Municipality.normalized_name, Municipality.id).all()
    return {row.normalized_name: row.id for row in rows}


def save_contracts(
    db: Session,
    contracts: list[CollectedContract],
    ibge_map: dict[str, int],
    name_map: dict[str, int] | None = None,
) -> tuple[int, int]:
    """Persiste contratos; retorna (criados, ignorados_duplicatas)."""
    if name_map is None:
        name_map = build_name_map(db)

    created = skipped = 0
    for cc in contracts:
        item = cc.item
        numero = item.numero_controle or ""
        if not numero:
            skipped += 1
            continue
        # Deduplicação por (process_number, source_name)
        exists = (
            db.query(PublicContract.id)
            .filter(
                PublicContract.process_number == numero,
                PublicContract.source_name == "PNCP",
            )
            .first()
        )
        if exists:
            skipped += 1
            continue

        # Município: tenta extrair do texto para contratos de show (Inexigibilidade/Fundação)
        fallback_id = ibge_map.get(item.ibge_code) if item.ibge_code else None
        if cc.contract_type_value == ContractType.show_artistico.value and item.objeto:
            municipality_id = _extract_municipality_id(item.objeto, name_map, fallback_id)
        else:
            municipality_id = fallback_id

        contract = PublicContract(
            municipality_id=municipality_id,
            contract_type=ContractType(cc.contract_type_value),
            object_description=item.objeto[:4000] if item.objeto else None,
            supplier_name=(item.orgao_nome or "")[:255] or None,
            supplier_document=(item.orgao_cnpj or "")[:20] or None,
            contract_value=item.valor_estimado,
            publication_date=_parse_date(item.data_publicacao),
            process_number=numero[:255],
            procurement_modality=_MODALITY_MAP.get(
                item.modalidade_id, ProcurementModality.desconhecido
            ),
            source_name="PNCP",
            source_url=f"https://pncp.gov.br/app/editais/{numero}",
            extracted_json=item.raw,
        )
        db.add(contract)
        created += 1
    db.commit()
    return created, skipped
