"""Varre sites das prefeituras e extrai secretários de cultura/turismo.

Uso:
  python scripts/run_secretary_scanner.py
  python scripts/run_secretary_scanner.py --ibge 5000807
  python scripts/run_secretary_scanner.py --dry-run       # mostra sem salvar
  python scripts/run_secretary_scanner.py --force         # re-escaneia mesmo quem já tem secretario
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact
from crawlers.prefeituras.scanner import PrefeituraScanner, ROLES_ALVO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scanner de Secretarios - prefeituras MS")
    p.add_argument("--ibge",    default=None, help="Filtrar por codigo IBGE especifico")
    p.add_argument("--dry-run", action="store_true", help="Mostra resultados sem salvar no banco")
    p.add_argument("--force",   action="store_true", help="Re-escaneia mesmo municipios que ja tem secretario")
    p.add_argument("--verbose", action="store_true", help="Log detalhado da navegacao")
    p.add_argument("--limit",   type=int, default=None, help="Processar no maximo N municipios")
    return p.parse_args()


def load_municipios(db, args) -> list:
    """Retorna municípios a escanear."""
    query = db.query(Municipality).filter(
        Municipality.state == "MS",
        Municipality.official_website.isnot(None),
    )
    if args.ibge:
        query = query.filter(Municipality.ibge_code == args.ibge)

    if not args.force:
        # Pular municípios que já têm secretario_cultura ou secretario_turismo
        subq = (
            db.query(PublicContact.municipality_id)
            .filter(PublicContact.role.in_(list(ROLES_ALVO)))
            .subquery()
        )
        query = query.filter(~Municipality.id.in_(subq))

    query = query.order_by(Municipality.name)
    if args.limit:
        query = query.limit(args.limit)
    return query.all()


def save_contacts(db, muni: Municipality, contacts: list[dict], dry_run: bool) -> int:
    """Salva os contatos relevantes; retorna qtd salva."""
    saved = 0
    for c in contacts:
        role = c.get("role_normalized", "outro")
        if role not in ROLES_ALVO:
            continue

        if dry_run:
            print(f"    [DRY-RUN] {c.get('name')} | {role} | {c.get('email')} | {c.get('phone')}")
            saved += 1
            continue

        # Dedup: não criar duplicata se já existe mesmo role+municipio
        existing = (
            db.query(PublicContact)
            .filter(
                PublicContact.municipality_id == muni.id,
                PublicContact.role == role,
            )
            .first()
        )
        if existing:
            continue

        ct = PublicContact(
            municipality_id=muni.id,
            name=c.get("name"),
            role=role,
            department=c.get("role_display"),
            email=c.get("email"),
            phone=c.get("phone"),
            source_url=c.get("source_url"),
            confidence_score=c.get("confidence_score", 0.7),
        )
        db.add(ct)
        saved += 1

    if not dry_run and saved > 0:
        db.commit()
    return saved


def main() -> None:
    args = parse_args()

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        from dotenv import load_dotenv
        load_dotenv()
        groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("ERRO: GROQ_API_KEY nao encontrada no ambiente ou .env")
        sys.exit(1)

    db = SessionLocal()
    try:
        municipios = load_municipios(db, args)

        if not municipios:
            print("Nenhum municipio para escanear.")
            return

        print(f"Scanner de Secretarios | {len(municipios)} municipios | dry-run={args.dry_run}")
        print()

        scanner = PrefeituraScanner(groq_api_key=groq_key, headless=True, verbose=args.verbose)

        total_encontrados = 0
        total_salvos = 0
        erros = 0

        for i, muni in enumerate(municipios, 1):
            print(f"[{i:02d}/{len(municipios)}] {muni.name} ({muni.official_website})")
            t0 = time.time()

            contacts = scanner.scan(muni.name, muni.official_website)

            elapsed = round(time.time() - t0, 1)
            alvo = [c for c in contacts if c.get("role_normalized") in ROLES_ALVO]

            if not contacts:
                erros += 1
                print(f"  -> Sem resultado ({elapsed}s)")
            elif not alvo:
                roles_found = [c.get("role_normalized") for c in contacts]
                print(f"  -> {len(contacts)} secretarios (sem cultura/turismo): {roles_found} ({elapsed}s)")
            else:
                total_encontrados += len(alvo)
                saved = save_contacts(db, muni, contacts, args.dry_run)
                total_salvos += saved
                for c in alvo:
                    print(f"  -> {c.get('role_normalized')}: {c.get('name')} | {c.get('email') or c.get('phone') or 'sem contato'}")
                print(f"  -> Salvos: {saved} ({elapsed}s)")

            # Pausa entre municípios para não sobrecarregar os servidores
            if i < len(municipios):
                time.sleep(1.5)

        print()
        print(f"Concluido: {total_encontrados} secretarios encontrados | {total_salvos} salvos | {erros} sem resultado")

    finally:
        db.close()


if __name__ == "__main__":
    main()
