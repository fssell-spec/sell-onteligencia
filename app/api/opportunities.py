"""Endpoints REST para oportunidades comerciais."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commercial_opportunity import CommercialOpportunity
from app.models.enums import OpportunityStatus, OpportunityType
from app.models.municipality import Municipality
from app.schemas.opportunity import OpportunityListOut, OpportunityOut, OpportunityUpdate

router = APIRouter(prefix="/opportunities", tags=["Oportunidades"])


def _enrich(opp: CommercialOpportunity, db: Session) -> OpportunityOut:
    """Adiciona nome do município ao schema de saída."""
    data = OpportunityOut.model_validate(opp)
    if opp.municipality_id:
        muni = db.get(Municipality, opp.municipality_id)
        data.municipality_name = muni.name if muni else None
    return data


@router.get("", response_model=OpportunityListOut, summary="Listar oportunidades")
def list_opportunities(
    status: OpportunityStatus | None = Query(None, description="Filtrar por status do funil"),
    opportunity_type: OpportunityType | None = Query(None, description="Filtrar por tipo"),
    owner: str | None = Query(None, description="Filtrar por responsável"),
    min_score: float | None = Query(None, ge=0, le=100, description="Score mínimo"),
    sort_by: Literal["score", "urgency", "budget", "event_date"] = Query(
        "score", description="Campo de ordenação"
    ),
    order: Literal["desc", "asc"] = Query("desc", description="Direção da ordenação"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(CommercialOpportunity)

    if status:
        q = q.filter(CommercialOpportunity.status == status)
    if opportunity_type:
        q = q.filter(CommercialOpportunity.opportunity_type == opportunity_type)
    if owner:
        q = q.filter(CommercialOpportunity.owner == owner)
    if min_score is not None:
        q = q.filter(CommercialOpportunity.final_opportunity_score >= min_score)

    sort_col = {
        "score": CommercialOpportunity.final_opportunity_score,
        "urgency": CommercialOpportunity.urgency_score,
        "budget": CommercialOpportunity.estimated_budget,
        "event_date": CommercialOpportunity.estimated_event_date,
    }[sort_by]

    q = q.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return OpportunityListOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[_enrich(o, db) for o in items],
    )


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityOut,
    summary="Detalhe de uma oportunidade",
)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opp = db.get(CommercialOpportunity, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    return _enrich(opp, db)


@router.patch(
    "/{opportunity_id}",
    response_model=OpportunityOut,
    summary="Atualizar status, responsável ou próxima ação",
)
def update_opportunity(
    opportunity_id: int,
    payload: OpportunityUpdate,
    db: Session = Depends(get_db),
):
    opp = db.get(CommercialOpportunity, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opp, field, value)

    db.commit()
    db.refresh(opp)
    return _enrich(opp, db)


@router.get(
    "/summary/by-status",
    summary="Contagem de oportunidades por status (funil)",
)
def summary_by_status(db: Session = Depends(get_db)):
    from sqlalchemy import func

    rows = (
        db.query(CommercialOpportunity.status, func.count().label("count"))
        .group_by(CommercialOpportunity.status)
        .all()
    )
    return {row.status.value: row.count for row in rows}


@router.get(
    "/summary/top",
    response_model=list[OpportunityOut],
    summary="Top N oportunidades por score final",
)
def top_opportunities(
    n: int = Query(10, ge=1, le=50, description="Quantidade de oportunidades"),
    db: Session = Depends(get_db),
):
    items = (
        db.query(CommercialOpportunity)
        .filter(CommercialOpportunity.status.notin_([OpportunityStatus.ganho, OpportunityStatus.perdido]))
        .order_by(CommercialOpportunity.final_opportunity_score.desc())
        .limit(n)
        .all()
    )
    return [_enrich(o, db) for o in items]
