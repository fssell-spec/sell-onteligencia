import sys; sys.path.insert(0,'C:/claude/sell-inteligencia')
import logging; logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contract import PublicContract
from app.models.enums import ContractType
from sqlalchemy import text

db = SessionLocal()
cg = db.query(Municipality).filter(Municipality.name.ilike('%Campo Grande%')).first()
print(f'Campo Grande id={cg.id} | pop={cg.population} | aniv_mes={cg.aniversario_mes}')
print()

contratos = db.query(PublicContract).filter(PublicContract.municipality_id == cg.id).all()
shows = [c for c in contratos if c.contract_type == ContractType.show_artistico]
estaduais = [c for c in contratos if (c.extracted_json or {}).get('source_type') == 'estadual']
print(f'Contratos linkados: {len(contratos)} | Shows: {len(shows)} | Marcados estadual: {len(estaduais)}')
print()
print('Contratos de show linkados a Campo Grande:')
for c in shows:
    st = (c.extracted_json or {}).get('source_type', '-')
    print(f'  R${c.contract_value} | {c.supplier_name} | estadual={st} | {(c.object_description or "")[:60]}')
db.close()
