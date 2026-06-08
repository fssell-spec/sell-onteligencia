from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.opportunities import router as opportunities_router
from app.api.municipalities import router as municipalities_router
from app.api.artists import router as artists_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Sistema de Inteligência Comercial para Shows, Rodeios e Eventos Públicos",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(opportunities_router)
app.include_router(municipalities_router)
app.include_router(artists_router)


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "env": settings.app_env,
        "docs": "/docs",
    }
