import logging
logging.disable(logging.CRITICAL)

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.commercial_opportunity import CommercialOpportunity
from app.models.public_contract import PublicContract
from sqlalchemy import func, text

db = SessionLocal()

opps = db.query(CommercialOpportunity).order_by(CommercialOpportunity.final_opportunity_score.desc()).limit(15).all()
print('TOP 15 OPORTUNIDADES:')
for o in opps:
    m = db.query(Municipality).filter(Municipality.id == o.municipality_id).first()
    n_contratos = db.query(func.count(PublicContract.id)).filter(PublicContract.municipality_id == o.municipality_id).scalar()
    v_total = db.query(func.sum(PublicContract.contract_value)).filter(PublicContract.municipality_id == o.municipality_id).scalar() or 0
    print(f'{o.final_opportunity_score:.0f} | {(m.name if m else "?"):<26} | contratos={n_contratos} | R${v_total:,.0f} | urg={o.urgency_score:.0f} fit={o.fit_score:.0f} margin={o.margin_potential_score:.0f}')

print()
print('CONTRATOS 2026 (top municipios):')
rows = db.execute(text("""
    SELECT m.name, COUNT(*) as n, SUM(pc.contract_value) as total
    FROM public_contracts pc
    JOIN municipalities m ON pc.municipality_id = m.id
    WHERE pc.publication_date >= '2026-01-01'
    GROUP BY m.name ORDER BY n DESC LIMIT 10
""")).fetchall()
for r in rows:
    print(f'  {r[0]:<26} | {r[1]} contratos | R${(r[2] or 0):,.0f}')

db.close()
