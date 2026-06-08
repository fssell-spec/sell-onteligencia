import logging
logging.disable(logging.CRITICAL)
import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contract import PublicContract
from sqlalchemy import text

db = SessionLocal()

cg = db.query(Municipality).filter(Municipality.name.ilike('%Campo Grande%')).first()
print(f'Campo Grande id={cg.id} ibge={cg.ibge_code} pop={cg.population}')
print()

contratos = db.query(PublicContract).filter(PublicContract.municipality_id == cg.id).order_by(PublicContract.publication_date.desc()).all()
print(f'Contratos vinculados ao municipality_id={cg.id}: {len(contratos)}')
for c in contratos:
    raw = (c.extracted_json or {})
    print(f'  {c.publication_date} | supplier_doc={c.supplier_document} | {(c.object_description or "")[:60][:60]} | R${c.contract_value}')

print()
print('--- Todos contratos com "Campo Grande" no nome do comprador ---')
rows = db.execute(text("""
    SELECT pc.id, pc.buyer_name, pc.buyer_cnpj, pc.municipality_id,
           m.name as muni_name, pc.publication_date, pc.contract_value,
           LEFT(pc.object_description, 60) as obj
    FROM public_contracts pc
    LEFT JOIN municipalities m ON pc.municipality_id = m.id
    WHERE LOWER(pc.supplier_name) LIKE '%campo grande%' OR LOWER(pc.object_description) LIKE '%campo grande%'
    ORDER BY pc.publication_date DESC
""")).fetchall()
print(f'Total: {len(rows)}')
for r in rows:
    print(f'  muni_id={r[2]} ({r[4]}) | supplier={r[1][:40]} | pub={r[3]} | R${r[6]}')

print()
print('--- Contratos SEM municipality_id (não linkados) ---')
sem_link = db.execute(text("SELECT COUNT(*) FROM public_contracts WHERE municipality_id IS NULL")).scalar()
print(f'Contratos sem municipality_id: {sem_link}')

print()
print('--- Distribuição de contratos por município (top 15) ---')
rows2 = db.execute(text("""
    SELECT m.name, COUNT(*) as n, SUM(pc.contract_value) as total
    FROM public_contracts pc
    JOIN municipalities m ON pc.municipality_id = m.id
    GROUP BY m.name ORDER BY n DESC LIMIT 15
""")).fetchall()
for r in rows2:
    print(f'  {r[0]:<30} | {r[1]:>3} contratos | R${(r[2] or 0):>12,.0f}')

db.close()
