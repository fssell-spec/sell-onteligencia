"""Enriquece contratos coletados com extracao LLM de informacoes estruturadas.

Fluxo por contrato:
  1. Busca itens detalhados via PNCP api/pncp/v1
  2. Combina objeto + itens em contexto rico
  3. Chama Claude Haiku para extrair: event_name, event_date, artist_name, services, notes
  4. Grava em extracted_json["llm_extracted"] e atualiza event_date + confidence_score

Uso:
  python scripts/run_contract_extractor.py
  python scripts/run_contract_extractor.py --limit 10
  python scripts/run_contract_extractor.py --tipo show_artistico
  python scripts/run_contract_extractor.py --reprocessar
"""
import argparse
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.enums import ContractType
from app.models.public_contract import PublicContract
from crawlers.pncp.items_fetcher import fetch_items
from etl.extractors.llm_extractor import extract_contract_info


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extrator LLM de contratos PNCP")
    p.add_argument("--limit", type=int, default=None, help="Maximo de contratos a processar")
    p.add_argument("--tipo", default=None, help="Filtrar por contract_type (ex: show_artistico)")
    p.add_argument("--reprocessar", action="store_true", help="Reprocessar contratos ja enriquecidos")
    p.add_argument("--sem-itens", action="store_true", help="Nao buscar itens PNCP (mais rapido)")
    return p.parse_args()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def main() -> None:
    args = parse_args()

    db = SessionLocal()
    try:
        query = db.query(PublicContract).filter(
            PublicContract.object_description.isnot(None)
        )
        if not args.reprocessar:
            query = query.filter(PublicContract.confidence_score.is_(None))
        if args.tipo:
            query = query.filter(
                PublicContract.contract_type == ContractType(args.tipo)
            )
        if args.limit:
            query = query.limit(args.limit)

        contracts = query.all()
        total = len(contracts)
        print(f"Contratos a enriquecer: {total}")
        if total == 0:
            print("Nada a fazer.")
            return

        updated = errors = 0
        for i, c in enumerate(contracts, 1):
            mun = c.municipality.name if c.municipality else "?"
            print(
                f"  [{i}/{total}] #{c.id} {c.contract_type.value:<20} {mun:<25}",
                end=" ",
                flush=True,
            )

            # Busca itens PNCP para contexto mais rico
            items = []
            if not args.sem_itens and c.process_number:
                items = fetch_items(
                    process_number=c.process_number,
                    extracted_json=c.extracted_json,
                )
                if items:
                    print(f"[{len(items)} itens]", end=" ", flush=True)

            result = extract_contract_info(c.object_description, items)

            if "error" in result:
                print(f"ERRO: {result['error']}")
                errors += 1
                continue

            confidence = float(result.get("confidence") or 0.0)
            c.confidence_score = confidence

            if not c.event_date:
                c.event_date = _parse_date(result.get("event_date_iso"))

            payload = dict(c.extracted_json) if c.extracted_json else {}
            payload["llm_extracted"] = {
                k: v for k, v in result.items()
                if k != "confidence"
            }
            c.extracted_json = payload

            event_name = result.get("event_name") or "-"
            artist = result.get("artist_name") or ""
            artist_str = f"  artista={artist}" if artist else ""
            print(f"conf={confidence:.2f}  evento={event_name[:35]}{artist_str}")

            updated += 1
            if i % 10 == 0:
                db.commit()

        db.commit()
        print(f"\nConcluido: {updated} atualizados | {errors} erros")

        # Resumo de eventos e artistas identificados
        query2 = db.query(PublicContract).filter(
            PublicContract.confidence_score.isnot(None)
        )
        all_enriched = query2.all()
        eventos = []
        for c in all_enriched:
            llm = (c.extracted_json or {}).get("llm_extracted", {})
            ename = llm.get("event_name")
            artist = llm.get("artist_name")
            if ename or artist:
                mun = c.municipality.name if c.municipality else "?"
                eventos.append((c.id, c.contract_type.value, ename, artist, c.event_date, mun))

        if eventos:
            print(f"\nEventos/Artistas identificados ({len(eventos)}):")
            for cid, ctype, ename, artist, edate, mun in sorted(eventos, key=lambda x: str(x[4] or "")):
                artstr = f"  artista={artist}" if artist else ""
                print(f"  #{cid} [{ctype:<20}] {mun:<22} {ename or '?':<35}  data={edate or '?'}{artstr}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
