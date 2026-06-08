"""Extrai artistas mencionados nos contratos e popula a tabela artists.

Estrategia de extracao (em ordem de prioridade):
  1. extracted_json['llm_extracted']['artist_name']
  2. Regex no object_description: "Artista: <NOME> | ..."  (padrao PNCP)
"""
import re
import unicodedata

from sqlalchemy.orm import Session

from app.models.artist import Artist
from app.models.public_contract import PublicContract

_RE_ARTISTA = re.compile(r"Artista\s*:\s*([^|]+?)(?:\s*\||\s*Evento\s*:|$)", re.IGNORECASE)

_COMPANY_TERMS = {"ltda", "me", "eireli", "s/a", "s.a", "sa", "producoes", "producao",
                  "eventos", "entretenimento", "agencia", "assessoria", "espetaculos"}
_GENERIC_NAMES = {"dupla sertaneja", "artista", "banda", "conjunto", "grupo", "solo",
                  "cantor", "cantora", "musico", "musica", "show", "apresentacao"}


def normalize(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return nfkd.encode("ascii", "ignore").decode("ascii").lower().strip()


def _clean_artist_name(raw: str) -> str | None:
    """Remove ruidos e nomes invalidos."""
    if not raw:
        return None
    name = raw.strip()
    noise = {"desconhecido", "nao informado", "n/a", "nenhum", "none", "-", "?"}
    if name.lower() in noise or len(name) < 3:
        return None
    # descarta empresas (ex: "R3 PRODUCOES ARTISTICAS LTDA")
    lower = name.lower()
    if any(t in lower for t in _COMPANY_TERMS):
        return None
    # descarta descricoes genericas exatas
    if normalize(name) in _GENERIC_NAMES:
        return None
    return name


def _extract_from_description(description: str | None) -> str | None:
    """Tenta extrair nome do artista do padrao PNCP 'Artista: X | Evento: Y'."""
    if not description:
        return None
    m = _RE_ARTISTA.search(description)
    if not m:
        return None
    return _clean_artist_name(m.group(1).strip())


def load_artists_from_contracts(db: Session) -> dict:
    """Cria/vincula artistas a partir dos contratos ja enriquecidos pelo LLM.

    Retorna dict com: criados, vinculados, sem_artista, erros.
    """
    contracts = (
        db.query(PublicContract)
        .filter(PublicContract.extracted_json.isnot(None))
        .filter(PublicContract.artist_id.is_(None))
        .all()
    )

    criados = vinculados = sem_artista = erros = 0

    for c in contracts:
        try:
            llm = (c.extracted_json or {}).get("llm_extracted", {})
            raw_name = llm.get("artist_name")
            name = _clean_artist_name(raw_name)

            # fallback: regex no object_description (padrao PNCP "Artista: X | Evento: Y")
            if not name:
                name = _extract_from_description(c.object_description)

            if not name:
                sem_artista += 1
                continue

            norm = normalize(name)
            artist = db.query(Artist).filter_by(normalized_name=norm).first()

            if not artist:
                artist = Artist(name=name, normalized_name=norm)
                db.add(artist)
                db.flush()
                criados += 1
            else:
                vinculados += 1

            c.artist_id = artist.id

        except Exception as exc:
            erros += 1
            print(f"  Erro contrato #{c.id}: {exc}")

    db.commit()
    return {"criados": criados, "vinculados": vinculados, "sem_artista": sem_artista, "erros": erros}
