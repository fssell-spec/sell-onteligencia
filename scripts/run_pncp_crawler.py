"""Crawl do PNCP para os 79 municípios do MS.

Uso:
  python scripts/run_pncp_crawler.py
  python scripts/run_pncp_crawler.py --inicio 2024-01-01 --fim 2024-12-31
  python scripts/run_pncp_crawler.py --modalidades 8 9
  python scripts/run_pncp_crawler.py --ibge 5002704   # só Campo Grande
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.crawler_run import CrawlerRun
from app.models.enums import CrawlerStatus
from app.models.municipality import Municipality
from crawlers.pncp.collector import PNCPCollector
from etl.loaders.contract_loader import build_ibge_map, save_contracts


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Crawler PNCP — MS")
    p.add_argument("--inicio", default=None, help="Data inicial AAAA-MM-DD (padrão: 2 anos atrás)")
    p.add_argument("--fim",    default=None, help="Data final   AAAA-MM-DD (padrão: hoje)")
    p.add_argument("--modalidades", nargs="+", type=int, default=[6, 7, 8, 9],
                   help="Códigos de modalidade PNCP (padrão: 6 7 8 9)")
    p.add_argument("--ibge", default=None, help="Filtrar por um único código IBGE")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    hoje = date.today()
    data_final   = date.fromisoformat(args.fim)    if args.fim    else hoje
    data_inicial = date.fromisoformat(args.inicio) if args.inicio else hoje - timedelta(days=730)

    db = SessionLocal()
    try:
        # Carrega municípios do banco
        query = db.query(Municipality.ibge_code, Municipality.name).filter(
            Municipality.ibge_code.isnot(None)
        )
        if args.ibge:
            query = query.filter(Municipality.ibge_code == args.ibge)
        municipios = query.all()

        if not municipios:
            print("Nenhum município encontrado. Verifique o banco e o argumento --ibge.")
            return

        ibge_codes = [m.ibge_code for m in municipios]
        print(f"Crawl PNCP | {len(ibge_codes)} municipios | {data_inicial} a {data_final}")
        print(f"Modalidades: {args.modalidades}")
        print()

        # Registra início do crawl
        run = CrawlerRun(
            crawler_name="pncp_contratacoes",
            source_type="PNCP",
            status=CrawlerStatus.running,
            metadata_json={
                "modalidades": args.modalidades,
                "data_inicial": str(data_inicial),
                "data_final": str(data_final),
                "municipios": len(ibge_codes),
            },
        )
        db.add(run)
        db.commit()

        try:
            collector = PNCPCollector(ibge_codes)
            collected = collector.collect(
                data_inicial=data_inicial,
                data_final=data_final,
                modalidades=args.modalidades,
                verbose=True,
            )

            print(f"\nTotal coletado: {len(collected)} contratos relevantes")
            print("Salvando no banco...")

            ibge_map = build_ibge_map(db)
            criados, ignorados = save_contracts(db, collected, ibge_map)

            print(f"Criados: {criados} | Duplicatas ignoradas: {ignorados}")

            run.status = CrawlerStatus.success
            run.records_found = len(collected)
            run.records_created = criados
            run.records_updated = ignorados
            db.commit()

        except Exception as exc:
            run.status = CrawlerStatus.failed
            run.error_message = str(exc)[:1000]
            db.commit()
            raise

    finally:
        db.close()

    # Resumo por tipo de contrato
    if collected:
        from collections import Counter
        tipos = Counter(c.contract_type_value for c in collected)
        print("\nDistribuição por tipo:")
        for tipo, qtd in tipos.most_common():
            print(f"  {tipo:<25} {qtd}")


if __name__ == "__main__":
    main()
