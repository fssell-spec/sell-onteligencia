"""Endpoints REST para artistas."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artist import Artist
from app.schemas.artist import ArtistListOut, ArtistOut

router = APIRouter(prefix="/artists", tags=["Artistas"])

VALID_FEE_TIERS = ["micro", "pequeno", "medio", "grande"]
VALID_POPULARITY = ["local", "estadual", "nacional", "nacional_top"]


@router.get("", response_model=ArtistListOut, summary="Listar artistas")
def list_artists(
    search: str | None = Query(None, description="Busca por nome"),
    main_style: str | None = Query(None, description="Filtrar por estilo musical"),
    fee_tier: str | None = Query(None, description="micro | pequeno | medio | grande"),
    popularity_level: str | None = Query(None, description="local | estadual | nacional | nacional_top"),
    origin_state: str | None = Query(None, description="Estado de origem (ex: MS, SP)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Artist)

    if search:
        q = q.filter(Artist.name.ilike(f"%{search}%"))
    if main_style:
        q = q.filter(Artist.main_style.ilike(f"%{main_style}%"))
    if fee_tier:
        q = q.filter(Artist.fee_tier == fee_tier)
    if popularity_level:
        q = q.filter(Artist.popularity_level == popularity_level)
    if origin_state:
        q = q.filter(Artist.origin_state == origin_state.upper())

    q = q.order_by(Artist.name)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return ArtistListOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[ArtistOut.model_validate(a) for a in items],
    )


@router.get("/{artist_id}", response_model=ArtistOut, summary="Detalhe de um artista")
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artista não encontrado")
    return ArtistOut.model_validate(artist)
