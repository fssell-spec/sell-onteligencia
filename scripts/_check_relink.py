import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')
import logging
logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
total = db.execute(text('SELECT COUNT(*) FROM public_contracts')).scalar()
linkados = db.execute(text('SELECT COUNT(*) FROM public_contracts WHERE municipality_id IS NOT NULL')).scalar()
sem_link = db.execute(text('SELECT COUNT(*) FROM public_contracts WHERE municipality_id IS NULL')).scalar()
estaduais = db.execute(text("SELECT COUNT(*) FROM public_contracts WHERE extracted_json->>'source_type' = 'estadual'")).scalar()
print(f'Total: {total} | Linkados: {linkados} | Sem link: {sem_link} | Estaduais: {estaduais}')
print()
rows = db.execute(text('''
    SELECT m.name, COUNT(*) as n
    FROM public_contracts pc
    JOIN municipalities m ON pc.municipality_id = m.id
    GROUP BY m.name ORDER BY n DESC LIMIT 15
''')).fetchall()
print('Top municipios com contratos:')
for r in rows:
    print(f'  {r[0]:<30} {r[1]}')
db.close()
