"""Seed de templates de orcamento de rodeio por porte de evento.

Usa o SimuladorRodeio para calcular os itens e persiste como
RodeoBudgetTemplate no banco.

Uso:
  python scripts/seed_rodeio_templates.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.rodeo_budget_template import RodeoBudgetTemplate
from analytics.simulador_rodeio import SimuladorRodeio

TEMPLATES = [
    {
        "name": "Show Simples - Pequeno Municipio",
        "event_size": "pequeno",
        "expected_audience": 1500,
        "duration_days": 1,
        "dias_simulacao": 1,
        "descricao": "Show artistico em municipio de ate 10k hab. Sem arena, palco simples.",
    },
    {
        "name": "Festa do Peao - Municipio Medio",
        "event_size": "medio",
        "expected_audience": 4000,
        "duration_days": 2,
        "dias_simulacao": 2,
        "descricao": "Festa do peao ou aniversario de cidade. Arena + arquibancada + show.",
    },
    {
        "name": "Rodeio Regional - Grande Municipio",
        "event_size": "grande",
        "expected_audience": 12000,
        "duration_days": 4,
        "dias_simulacao": 4,
        "descricao": "Rodeio com etapa de circuito. Arena completa, LED, shows nacionais.",
    },
    {
        "name": "Expoagro Estadual - Mega Evento",
        "event_size": "mega",
        "expected_audience": 30000,
        "duration_days": 6,
        "dias_simulacao": 6,
        "descricao": "Expo com rodeio, shows e parque de exposicoes. Campo Grande/Dourados.",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        criados = atualizados = 0
        for t in TEMPLATES:
            sim = SimuladorRodeio(
                event_size=t["event_size"],
                dias=t["dias_simulacao"],
                publico=t["expected_audience"],
            )
            orcamento = sim.calcular()
            resumo = orcamento.resumo()

            required_items = {
                item["categoria"]: {
                    "descricao": item["descricao"],
                    "dias": item["dias"],
                    "min": item["min"],
                    "avg": item["avg"],
                    "max": item["max"],
                }
                for item in resumo["itens"]
            }
            required_items["_totais"] = {
                "min": resumo["total_min"],
                "avg": resumo["total_avg"],
                "max": resumo["total_max"],
            }
            required_items["_meta"] = {
                "descricao": t["descricao"],
            }

            existing = db.query(RodeoBudgetTemplate).filter_by(name=t["name"]).first()
            if existing:
                existing.event_size = t["event_size"]
                existing.expected_audience = t["expected_audience"]
                existing.duration_days = t["duration_days"]
                existing.required_items_json = required_items
                atualizados += 1
            else:
                tmpl = RodeoBudgetTemplate(
                    name=t["name"],
                    event_size=t["event_size"],
                    expected_audience=t["expected_audience"],
                    duration_days=t["duration_days"],
                    required_items_json=required_items,
                )
                db.add(tmpl)
                criados += 1

            total_avg = required_items["_totais"]["avg"]
            total_max = required_items["_totais"]["max"]
            print(f"  {t['name']}")
            print(f"    avg R${total_avg:,.0f} | max R${total_max:,.0f}")

        db.commit()
        print(f"\nTemplates: {criados} criados, {atualizados} atualizados")

    finally:
        db.close()


if __name__ == "__main__":
    main()
