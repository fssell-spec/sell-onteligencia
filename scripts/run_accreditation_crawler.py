"""Crawl PNCP — Editais de Credenciamento (modalidade 12) para municípios do MS.

Uso:
  python scripts/run_accreditation_crawler.py
  python scripts/run_accreditation_crawler.py --inicio 2025-01-01 --fim 2026-06-03
  python scripts/run_accreditation_crawler.py --ibge 5002704
"""
import argparse
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality
from crawlers.pncp.collector import PNCPCollector
from etl.loaders.accreditation_loader import build_ibge_map, save_accreditations


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Crawler PNCP — Credenciamentos MS")
    p.add_argument("--inicio", default=None, help="Data inicial AAAA-MM-DD (padrao: 12 meses atras)")
    p.add_argument("--fim",    default=None, help="Data final   AAAA-MM-DD (padrao: hoje)")
    p.add_argument("--ibge",   default=None, help="Filtrar por um unico codigo IBGE")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    hoje = date.today()
    data_final   = date.fromisoformat(args.fim)    if args.fim    else hoje
    data_inicial = date.fromisoformat(args.inicio) if args.inicio else hoje - timedelta(days=365)

    db = SessionLocal()
    try:
        query = db.query(Municipality.ibge_code, Municipality.name).filter(
            Municipality.ibge_code.isnot(None)
        )
        if args.ibge:
            query = query.filter(Municipality.ibge_code == args.ibge)
        municipios = query.all()

        if not municipios:
            print("Nenhum municipio encontrado.")
            return

        ibge_codes = [m.ibge_code for m in municipios]
        ibge_map = build_ibge_map(db)

        print(f"Crawl Credenciamentos | {len(ibge_codes)} municipios | {data_inicial} a {data_final}")
        print()

        collector = PNCPCollector(ibge_codes)
        filtered = collector.collect(
            data_inicial=data_inicial,
            data_final=data_final,
            modalidades=[12],
            verbose=True,
        )

        print(f"\nRelevantes para eventos: {len(filtered)}")

        if not filtered:
            print("Nenhum edital de credenciamento relevante encontrado no periodo.")
            return

        criados, ignorados = save_accreditations(db, filtered, ibge_map)

        munis_unicos = len({cc.item.ibge_code for cc in filtered if cc.item.ibge_code})
        print()
        print(f"\nSalvos: {criados} | Duplicatas: {ignorados} | Municipios: {munis_unicos}")

        if filtered:
            tipos = Counter(c.contract_type_value for c in filtered)
            print("\nDistribuicao por tipo:")
            for tipo, qtd in tipos.most_common():
                print(f"  {tipo:<25} {qtd}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
