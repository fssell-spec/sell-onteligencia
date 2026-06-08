"""Extrai artistas dos contratos enriquecidos e vincula na tabela artists.

Uso:
  python scripts/run_artist_extractor.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.artist import Artist
from app.models.public_contract import PublicContract
from etl.loaders.artist_loader import load_artists_from_contracts


def main() -> None:
    db = SessionLocal()
    try:
        total_contratos = db.query(PublicContract).filter(
            PublicContract.extracted_json.isnot(None)
        ).count()
        ja_vinculados = db.query(PublicContract).filter(
            PublicContract.artist_id.isnot(None)
        ).count()

        print(f"Contratos enriquecidos: {total_contratos}")
        print(f"Ja com artista vinculado: {ja_vinculados}")
        print(f"A processar: {total_contratos - ja_vinculados}")
        print()

        resultado = load_artists_from_contracts(db)

        print(f"Artistas criados:  {resultado['criados']}")
        print(f"Contratos vinculados a artista ja existente: {resultado['vinculados']}")
        print(f"Contratos sem artista identificado: {resultado['sem_artista']}")
        print(f"Erros: {resultado['erros']}")

        total_artistas = db.query(Artist).count()
        print(f"\nTotal de artistas no banco: {total_artistas}")

        # Lista artistas com contratos vinculados
        artistas_com_contrato = (
            db.query(Artist)
            .filter(Artist.contracts.any())
            .order_by(Artist.name)
            .all()
        )
        if artistas_com_contrato:
            print(f"\nArtistas com contratos ({len(artistas_com_contrato)}):")
            for a in artistas_com_contrato:
                n_contratos = len(a.contracts)
                tier = a.fee_tier or "?"
                pop = a.popularity_level or "?"
                style = a.main_style or "?"
                print(f"  {a.name:<35} contratos={n_contratos}  estilo={style}  cache={tier}  popularidade={pop}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
