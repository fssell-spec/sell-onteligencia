"""
Corrige municipality_id de contratos show_artistico que foram atribuídos
ao órgão contratante (ex: Fundação de Cultura do MS) em vez do município
onde o show ocorreu, que está descrito no object_description.

Uso:
    python scripts/fix_contract_municipalities.py
    python scripts/fix_contract_municipalities.py --dry-run   # só mostra, não salva
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.enums import ContractType
from app.models.public_contract import PublicContract
from etl.loaders.contract_loader import _extract_municipality_id, build_name_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra as correções sem salvar")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        name_map = build_name_map(db)

        contracts = (
            db.query(PublicContract)
            .filter(PublicContract.contract_type == ContractType.show_artistico)
            .all()
        )

        print(f"Contratos show_artistico encontrados: {len(contracts)}")
        corrigidos = 0
        sem_match = 0

        for c in contracts:
            if not c.object_description:
                continue

            novo_id = _extract_municipality_id(c.object_description, name_map, fallback_id=None)

            if novo_id is None:
                sem_match += 1
                print(f"  [SEM MATCH] id={c.id} | {c.object_description[:80]}")
                continue

            if novo_id != c.municipality_id:
                # Busca nome para log legível
                from app.models.municipality import Municipality
                muni_atual = db.get(Municipality, c.municipality_id)
                muni_novo = db.get(Municipality, novo_id)
                print(
                    f"  [CORRIGIR] id={c.id} | "
                    f"{muni_atual.name if muni_atual else '?'} → {muni_novo.name if muni_novo else '?'} | "
                    f"{c.object_description[:70]}"
                )
                if not args.dry_run:
                    c.municipality_id = novo_id
                corrigidos += 1

        if not args.dry_run:
            db.commit()
            print(f"\nOK: {corrigidos} contratos corrigidos | {sem_match} sem match de município")
        else:
            print(f"\nDRY-RUN: {corrigidos} seriam corrigidos | {sem_match} sem match")

    finally:
        db.close()


if __name__ == "__main__":
    main()
