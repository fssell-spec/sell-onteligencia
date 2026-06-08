"""Monitora o Diário Oficial do MS em busca de contratações de shows/artistas.

Uso:
  python scripts/run_diario_crawler.py                     # ultimos 30 dias
  python scripts/run_diario_crawler.py --dias 7            # ultimos 7 dias
  python scripts/run_diario_crawler.py --inicio 2026-05-01 # desde data
  python scripts/run_diario_crawler.py --dry-run           # mostra sem salvar
"""
import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from groq import Groq
from app.database import SessionLocal
from app.models.diario_oficial_hit import DiarioOficialHit
from crawlers.diarios_oficiais.collector import DiarioOficialCollector
from etl.loaders.diario_loader import save_diario_hits


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitor do Diario Oficial do MS")
    p.add_argument("--inicio", default=None, help="Data inicial AAAA-MM-DD")
    p.add_argument("--fim",    default=None, help="Data final AAAA-MM-DD (padrao: hoje)")
    p.add_argument("--dias",   type=int, default=30, help="Janela em dias se --inicio nao fornecido")
    p.add_argument("--dry-run", action="store_true", help="Exibe hits sem salvar no banco")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("ERRO: GROQ_API_KEY nao encontrada no .env")
        sys.exit(1)

    hoje = date.today()
    data_final   = date.fromisoformat(args.fim)    if args.fim    else hoje
    data_inicial = date.fromisoformat(args.inicio) if args.inicio else hoje - timedelta(days=args.dias)

    print(f"Diario Oficial Monitor | {data_inicial} a {data_final} | dry-run={args.dry_run}")
    print()

    collector = DiarioOficialCollector()
    hits = collector.collect(data_inicial=data_inicial, data_final=data_final)
    print(f"\nTotal coletado: {len(hits)} hits")

    if not hits:
        print("Nenhum hit encontrado.")
        return

    if args.dry_run:
        print("\nPrimeiros 10 hits:")
        for h in hits[:10]:
            d = h.hit.data_publicacao[:10]
            hl = (h.hit.highlight or "")[:120]
            print(f"  {d} | kw={h.keyword:<25} | {hl}")
        return

    groq = Groq(api_key=groq_key)
    db = SessionLocal()
    try:
        criados, duplicatas = save_diario_hits(db, hits, groq, verbose=True)
        print(f"\nSalvos: {criados} | Duplicatas: {duplicatas}")

        novos = (
            db.query(DiarioOficialHit)
            .filter(
                DiarioOficialHit.status == "novo",
                DiarioOficialHit.data_publicacao >= str(data_inicial),
            )
            .count()
        )
        inex = (
            db.query(DiarioOficialHit)
            .filter(
                DiarioOficialHit.status == "novo",
                DiarioOficialHit.tipo_contratacao == "inexigibilidade",
                DiarioOficialHit.data_publicacao >= str(data_inicial),
            )
            .count()
        )
        print(f"\nAlertas ativos no periodo: {novos} novos | {inex} inexigibilidade")
    finally:
        db.close()


if __name__ == "__main__":
    main()
