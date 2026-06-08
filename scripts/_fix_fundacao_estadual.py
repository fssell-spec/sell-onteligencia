"""Marca como estadual os contratos da Fundacao de Cultura que ja tinham municipality_id."""
import sys; sys.path.insert(0,'C:/claude/sell-inteligencia')
import logging; logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from sqlalchemy import text

CNPJ = "15579196000198"

db = SessionLocal()
result = db.execute(text("""
    UPDATE public_contracts
    SET extracted_json = COALESCE(extracted_json, '{}')::jsonb || '{"source_type": "estadual"}'
    WHERE regexp_replace(supplier_document, '[.\\-/]', '', 'g') = :cnpj
"""), {"cnpj": CNPJ})
print(f"Contratos atualizados: {result.rowcount}")
db.commit()
db.close()
