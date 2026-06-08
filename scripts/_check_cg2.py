import logging
logging.disable(logging.CRITICAL)
import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')

from app.database import SessionLocal
from app.models.public_contract import PublicContract
from app.models.municipality import Municipality
from sqlalchemy import text

db = SessionLocal()

cg = db.query(Municipality).filter(Municipality.name.ilike('%Campo Grande%')).first()
contratos = db.query(PublicContract).filter(PublicContract.municipality_id == cg.id).order_by(PublicContract.publication_date.desc()).all()
print(f'=== {len(contratos)} contratos vinculados a Campo Grande (id={cg.id}, ibge={cg.ibge_code}) ===')
for c in contratos:
    llm = (c.extracted_json or {}).get('llm_extracted', {})
    print(f'  {c.publication_date} | {(c.object_description or "")[:70]}')
    print(f'    source_url={c.source_url}')
    print(f'    supplier={c.supplier_name} | valor=R${c.contract_value}')

print()
print('=== Contratos com ibge 5002704 na URL ===')
rows = db.execute(text("SELECT id, source_url, municipality_id, object_description FROM public_contracts WHERE source_url LIKE '%5002704%' LIMIT 20")).fetchall()
print(f'Total: {len(rows)}')
for r in rows:
    print(f'  id={r[0]} muni_id={r[2]} | {(r[3] or "")[:50]}')
    print(f'    url={r[1][:100]}')

print()
print('=== Como o crawler linka: amostra de source_url ===')
rows2 = db.execute(text("SELECT source_url, municipality_id FROM public_contracts WHERE source_url IS NOT NULL LIMIT 5")).fetchall()
for r in rows2:
    print(f'  muni_id={r[1]} | {r[0]}')

print()
print('=== Contratos sem municipality_id ===')
sem = db.execute(text("SELECT COUNT(*) FROM public_contracts WHERE municipality_id IS NULL")).scalar()
total = db.execute(text("SELECT COUNT(*) FROM public_contracts")).scalar()
print(f'Sem link: {sem} / Total: {total}')

db.close()
