"""
Script de entrada para a Etapa 9 — Motor de Oportunidades.

Executa em sequência:
1. Classifica eventos extraídos e popula municipal_events
2. Calcula scores e popula commercial_opportunities

Uso:
    python scripts/run_opportunity_engine.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from analytics.event_classifier import classify_and_seed, seed_from_diario
from analytics.opportunity_engine import run as run_engine


def main() -> None:
    db = SessionLocal()
    try:
        print("Etapa 1/3 — Classificando eventos dos contratos PNCP...")
        n_events = classify_and_seed(db)
        print(f"  {n_events} eventos criados a partir de contratos.")

        print("Etapa 2/3 — Enriquecendo eventos com Diário Oficial...")
        n_do = seed_from_diario(db)
        print(f"  {n_do} eventos criados a partir do Diário Oficial.")

        print("Etapa 3/3 — Calculando scores de oportunidade...")
        n_opps = run_engine(db)
        print(f"  {n_opps} oportunidades criadas em commercial_opportunities.")

        print("Concluido. Recarregue o dashboard para ver a aba Oportunidades.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
