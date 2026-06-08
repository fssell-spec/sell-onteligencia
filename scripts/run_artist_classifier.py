"""Classifica artistas sem fee_tier/popularity_level usando Groq.

Uso:
  python scripts/run_artist_classifier.py
  python scripts/run_artist_classifier.py --limit 20
  python scripts/run_artist_classifier.py --reprocessar
"""
import argparse
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.artist import Artist
from app.models.public_contract import PublicContract
from etl.extractors.artist_classifier import classify_artist_validated


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Classificador LLM de artistas")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--reprocessar", action="store_true", help="Reclassifica artistas ja classificados")
    return p.parse_args()


def _build_context(artist: Artist, db) -> str:
    """Monta contexto extra com contratos vinculados para ajudar o LLM."""
    parts = []
    if artist.origin_city and artist.origin_state:
        parts.append(f"Origem: {artist.origin_city}/{artist.origin_state}")
    if artist.main_style:
        parts.append(f"Estilo conhecido: {artist.main_style}")

    # adiciona exemplos de contratos para dar contexto de mercado
    contracts = artist.contracts[:3]
    for c in contracts:
        desc = (c.object_description or "")[:80]
        if desc:
            parts.append(f"Contrato: {desc}")

    return ". ".join(parts) if parts else ""


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        query = db.query(Artist)
        if not args.reprocessar:
            query = query.filter(
                (Artist.fee_tier.is_(None)) | (Artist.popularity_level.is_(None))
            )
        if args.limit:
            query = query.limit(args.limit)

        artistas = query.all()
        total = len(artistas)
        print(f"Artistas a classificar: {total}")
        if total == 0:
            print("Todos ja classificados. Use --reprocessar para forcar.")
            return

        ok = erros = 0
        for i, a in enumerate(artistas, 1):
            print(f"  [{i}/{total}] {a.name:<35}", end=" ", flush=True)
            context = _build_context(a, db)
            result = classify_artist_validated(a.name, context)

            if "error" in result:
                print(f"ERRO: {result['error']}")
                erros += 1
                continue

            conf = float(result.get("confidence") or 0.0)

            if not a.main_style or args.reprocessar:
                a.main_style = result.get("main_style")
            if not a.sub_style or args.reprocessar:
                a.sub_style = result.get("sub_style")
            if not a.fee_tier or args.reprocessar:
                a.fee_tier = result.get("fee_tier")
            if not a.popularity_level or args.reprocessar:
                a.popularity_level = result.get("popularity_level")

            style = a.main_style or "?"
            sub = a.sub_style or "?"
            tier = a.fee_tier or "?"
            pop = a.popularity_level or "?"
            print(f"estilo={style}/{sub}  cache={tier}  pop={pop}  conf={conf:.2f}")

            ok += 1
            if i % 10 == 0:
                db.commit()

            time.sleep(0.5)

        db.commit()
        print(f"\nConcluido: {ok} classificados | {erros} erros")

    finally:
        db.close()


if __name__ == "__main__":
    main()
