"""Monitora o DIOGRANDE (Diário Oficial de Campo Grande) em busca de shows/artistas.

Uso:
  python scripts/run_diogrande_crawler.py                     # últimos 30 dias
  python scripts/run_diogrande_crawler.py --dias 7            # últimos 7 dias
  python scripts/run_diogrande_crawler.py --inicio 2026-01-01 # desde data
  python scripts/run_diogrande_crawler.py --dry-run           # mostra sem salvar

Obs: o download de PDFs está temporariamente fora (backend em manutenção).
Os hits são salvos como status='potencial' para extração futura quando o download voltar.
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.diario_oficial_hit import DiarioOficialHit
from crawlers.diogrande.collector import DioGrandeCollector
from etl.loaders.diario_loader import save_diogrande_hits


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitor do DIOGRANDE (Campo Grande - MS)")
    p.add_argument("--inicio", default=None, help="Data inicial AAAA-MM-DD")
    p.add_argument("--fim",    default=None, help="Data final AAAA-MM-DD (padrao: hoje)")
    p.add_argument("--dias",   type=int, default=30, help="Janela em dias se --inicio nao fornecido")
    p.add_argument("--dry-run", action="store_true", help="Exibe hits sem salvar no banco")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    hoje = date.today()
    data_final   = date.fromisoformat(args.fim)    if args.fim    else hoje
    data_inicial = date.fromisoformat(args.inicio) if args.inicio else hoje - timedelta(days=args.dias)

    print(f"DIOGRANDE Monitor | {data_inicial} a {data_final} | dry-run={args.dry_run}")
    print()

    collector = DioGrandeCollector()
    hits = collector.collect(data_inicial=data_inicial, data_final=data_final)
    print(f"\nTotal coletado: {len(hits)} hits")

    if not hits:
        print("Nenhum hit encontrado.")
        return

    if args.dry_run:
        print("\nPrimeiros 10 hits:")
        for h in hits[:10]:
            print(f"  {h.edicao.dia} | ed.{h.edicao.numero} | kw={h.keyword:<30} | {h.edicao.arquivo}")
        return

    db = SessionLocal()
    try:
        criados, duplicatas = save_diogrande_hits(db, hits, verbose=True)
        print(f"\nSalvos: {criados} | Duplicatas: {duplicatas}")

        total_cg = (
            db.query(DiarioOficialHit)
            .filter(
                DiarioOficialHit.status == "potencial",
                DiarioOficialHit.municipio_id.isnot(None),
            )
            .count()
        )
        print(f"Total hits DIOGRANDE no banco: {total_cg}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
