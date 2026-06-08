"""Roda o Prefeitura Scanner para extrair secretários via Playwright + LLM.

Uso:
  python scripts/run_prefeitura_scanner.py --all
  python scripts/run_prefeitura_scanner.py --municipio "Campo Grande"
  python scripts/run_prefeitura_scanner.py --all --limit 10 --only-alvo
  python scripts/run_prefeitura_scanner.py --all --dry-run
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact
from crawlers.prefeituras.scanner import ROLES_ALVO, PrefeituraScanner

ROLE_SOURCE = "prefeitura_scanner_llm"


def parse_args():
    p = argparse.ArgumentParser()
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--all", action="store_true", help="Escaneia todos os municipios")
    grp.add_argument("--municipio", metavar="NOME", help="Nome do municipio especifico")
    p.add_argument("--limit", type=int, default=0, help="Limite de municipios (0=sem limite)")
    p.add_argument("--only-alvo", action="store_true",
                   help="Pula municipios que ja tem secretario_cultura ou secretario_turismo")
    p.add_argument("--dry-run", action="store_true", help="Nao salva no banco")
    p.add_argument("--verbose", action="store_true", help="Log detalhado")
    return p.parse_args()


def _already_has_alvo(db, municipality_id: int) -> bool:
    return db.query(PublicContact).filter(
        PublicContact.municipality_id == municipality_id,
        PublicContact.role.in_(list(ROLES_ALVO)),
    ).first() is not None


def _save_contacts(db, municipality, contacts: list[dict], dry_run: bool) -> int:
    saved = 0
    for c in contacts:
        role = c.get("role_normalized", "outro")
        if role not in ROLES_ALVO:
            continue
        name = (c.get("name") or "").strip()
        if not name:
            continue

        existing = db.query(PublicContact).filter(
            PublicContact.municipality_id == municipality.id,
            PublicContact.role == role,
        ).first()

        if existing:
            existing.name = name
            existing.department = c.get("role_display")
            existing.phone = c.get("phone")
            existing.email = c.get("email")
            existing.source_url = municipality.official_website
            existing.confidence_score = 0.7
        else:
            contact = PublicContact(
                municipality_id=municipality.id,
                name=name,
                role=role,
                department=c.get("role_display"),
                phone=c.get("phone"),
                email=c.get("email"),
                source_url=municipality.official_website,
                confidence_score=0.7,
            )
            db.add(contact)
        saved += 1

    if not dry_run:
        db.commit()
    return saved


def main():
    args = parse_args()
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        print("ERRO: GROQ_API_KEY nao configurada no .env")
        sys.exit(1)

    scanner = PrefeituraScanner(groq_api_key=groq_key, headless=True, verbose=args.verbose)

    db = SessionLocal()
    try:
        query = db.query(Municipality).filter(
            Municipality.state == "MS",
            Municipality.official_website.isnot(None),
        ).order_by(Municipality.population.desc())

        if args.municipio:
            query = query.filter(Municipality.name.ilike(f"%{args.municipio}%"))

        munis = query.all()

        if args.only_alvo:
            munis = [m for m in munis if not _already_has_alvo(db, m.id)]
            print(f"Municipios sem secretario_cultura/turismo: {len(munis)}")

        if args.limit:
            munis = munis[:args.limit]

        print(f"Escaneando {len(munis)} municipio(s)...")
        if args.dry_run:
            print("DRY-RUN — nada sera salvo.\n")

        total_found = total_saved = 0
        failed = []

        for i, muni in enumerate(munis, 1):
            print(f"[{i}/{len(munis)}] {muni.name} — {muni.official_website}")
            t0 = time.time()

            contacts = scanner.scan(muni.name, muni.official_website)
            alvo = [c for c in contacts if c.get("role_normalized") in ROLES_ALVO]

            elapsed = round(time.time() - t0, 1)
            print(f"  -> {len(contacts)} secretarios | {len(alvo)} alvo | {elapsed}s")

            for c in contacts:
                marker = "**" if c.get("role_normalized") in ROLES_ALVO else "  "
                print(f"  {marker} {c.get('role_normalized')}: {c.get('name')} / {c.get('role_display')}")

            total_found += len(alvo)

            if alvo:
                saved = _save_contacts(db, muni, contacts, args.dry_run)
                total_saved += saved

            if not contacts:
                failed.append(muni.name)

        print(f"\nResultado: {total_found} secretarios alvo encontrados | {total_saved} salvos")
        if failed:
            print(f"Sem resultado ({len(failed)}): {failed}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
