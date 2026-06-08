import sys; sys.path.insert(0,'C:/claude/sell-inteligencia')
import logging; logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from app.models.commercial_opportunity import CommercialOpportunity
from app.models.municipality import Municipality

db = SessionLocal()
opps = db.query(CommercialOpportunity).order_by(CommercialOpportunity.final_opportunity_score.desc()).all()
alto = sum(1 for o in opps if (o.final_opportunity_score or 0) >= 60)
medio = sum(1 for o in opps if 30 <= (o.final_opportunity_score or 0) < 60)
baixo = sum(1 for o in opps if (o.final_opportunity_score or 0) < 30)
print(f'Total: {len(opps)} | Alto(>=60): {alto} | Medio(30-60): {medio} | Baixo(<30): {baixo}')
print()
print('TOP 15:')
for o in opps[:15]:
    m = db.query(Municipality).filter(Municipality.id == o.municipality_id).first()
    nome = m.name if m else '?'
    acao = (o.suggested_next_action or '')[:52]
    score = o.final_opportunity_score or 0
    print(f'  {score:>5.1f} | {nome:<28} | {acao}')

print()
cg = db.query(Municipality).filter(Municipality.name.ilike('%Campo Grande%')).first()
opp_cg = db.query(CommercialOpportunity).filter(CommercialOpportunity.municipality_id == cg.id).first()
score_cg = opp_cg.final_opportunity_score if opp_cg else None
print(f'Campo Grande: score={score_cg}')
db.close()
