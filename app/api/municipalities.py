"""Endpoints REST para municípios."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact
from app.models.municipal_event import MunicipalEvent
from app.models.public_contract import PublicContract
from app.schemas.municipality import MunicipalityListOut, MunicipalityOut
from app.schemas.contact import ContactOut

router = APIRouter(prefix="/municipalities", tags=["Municípios"])


@router.get("", response_model=MunicipalityListOut, summary="Listar municípios")
def list_municipalities(
    search: str | None = Query(None, description="Busca por nome"),
    mesorregiao: str | None = Query(None, description="Filtrar por mesorregião"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Municipality).filter(Municipality.state == "MS")

    if search:
        q = q.filter(Municipality.name.ilike(f"%{search}%"))
    if mesorregiao:
        q = q.filter(Municipality.mesorregiao == mesorregiao)

    q = q.order_by(Municipality.name)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return MunicipalityListOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[MunicipalityOut.model_validate(m) for m in items],
    )


@router.get("/{municipality_id}", summary="Detalhe de um município com contexto comercial")
def get_municipality(municipality_id: int, db: Session = Depends(get_db)):
    muni = db.get(Municipality, municipality_id)
    if not muni:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    contacts = (
        db.query(PublicContact)
        .filter(PublicContact.municipality_id == municipality_id)
        .all()
    )
    events = (
        db.query(MunicipalEvent)
        .filter(MunicipalEvent.municipality_id == municipality_id)
        .all()
    )
    contracts = (
        db.query(PublicContract)
        .filter(PublicContract.municipality_id == municipality_id)
        .order_by(PublicContract.publication_date.desc())
        .limit(10)
        .all()
    )

    return {
        "municipality": MunicipalityOut.model_validate(muni),
        "contacts": [ContactOut.model_validate(c) for c in contacts],
        "events": [
            {
                "id": e.id,
                "name": e.name,
                "event_type": e.event_type,
                "usual_month": e.usual_month,
                "recurrence_pattern": e.recurrence_pattern,
            }
            for e in events
        ],
        "recent_contracts": [
            {
                "id": c.id,
                "contract_type": c.contract_type,
                "object_description": c.object_description,
                "supplier_name": c.supplier_name,
                "contract_value": float(c.contract_value) if c.contract_value else None,
                "publication_date": c.publication_date,
                "procurement_modality": c.procurement_modality,
            }
            for c in contracts
        ],
    }
