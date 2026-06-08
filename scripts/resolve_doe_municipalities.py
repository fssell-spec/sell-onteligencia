"""Resolve municipio_id em diario_oficial_hits a partir de municipio_detectado.

Dois passos:
  1. Limpa o string literal "null" -> NULL real no banco
  2. Faz fuzzy match de municipio_detectado contra a tabela municipalities
     e preenche municipio_id onde ainda falta FK

Após resolver, propaga municipality_id para artist_contract_appearances
(todos os registros DOE/DIOGRANDE que referenciam os hits atualizados).

Uso:
  python scripts/resolve_doe_municipalities.py            # processa tudo
  python scripts/resolve_doe_municipalities.py --dry-run  # exibe sem salvar
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.diario_oficial_hit import DiarioOficialHit
from app.models.artist_contract_appearance import ArtistContractAppearance


def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = "".join(c for c in s if c.isalnum() or c.isspace())
    return " ".join(s.split())


def _build_muni_index(db) -> dict[str, Municipality]:
    munis = db.query(Municipality).all()
    idx: dict[str, Municipality] = {}
    for m in munis:
        idx[_normalize(m.name)] = m
        if m.normalized_name:
            idx[_normalize(m.normalized_name)] = m
    return idx


def _match_municipality(raw: str, idx: dict[str, Municipality]) -> tuple[Municipality | None, float]:
    """Retorna (Municipality, confidence) ou (None, 0.0).
    Estratégias:
      1.0 — match exato
      0.9 — sobreposição de tokens: todos os tokens do nome menor estão no maior,
             com mínimo de 2 tokens para evitar "Lagoas" casar com "Três Lagoas"
    """
    norm = _normalize(raw)
    if not norm or len(norm) < 4:
        return None, 0.0

    if norm in idx:
        return idx[norm], 1.0

    norm_tokens = set(norm.split())
    for key, muni in idx.items():
        key_tokens = set(key.split())
        shorter = norm_tokens if len(norm_tokens) <= len(key_tokens) else key_tokens
        longer = key_tokens if len(norm_tokens) <= len(key_tokens) else norm_tokens
        if len(shorter) >= 2 and shorter.issubset(longer):
            return muni, 0.9

    return None, 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve municipio_id em diario_oficial_hits")
    parser.add_argument("--dry-run", action="store_true", help="Exibe sem salvar")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        muni_idx = _build_muni_index(db)
        print(f"Municípios indexados: {len(muni_idx)} entradas")

        # ── Passo 1: limpar string literal "null" ─────────────────────────────
        null_hits = (
            db.query(DiarioOficialHit)
            .filter(DiarioOficialHit.municipio_detectado == "null")
            .all()
        )
        print(f'\nPasso 1: {len(null_hits)} hits com municipio_detectado = "null" (string literal)')
        if null_hits and not args.dry_run:
            for h in null_hits:
                h.municipio_detectado = None
            db.commit()
            print(f'  Corrigidos: {len(null_hits)} -> NULL real')
        elif args.dry_run:
            print(f'  (dry-run) Seriam corrigidos: {len(null_hits)}')

        # ── Passo 2: match fuzzy nos que têm nome mas sem FK ──────────────────
        unresolved = (
            db.query(DiarioOficialHit)
            .filter(
                DiarioOficialHit.municipio_id.is_(None),
                DiarioOficialHit.municipio_detectado.isnot(None),
                DiarioOficialHit.municipio_detectado != "",
            )
            .all()
        )
        print(f'\nPasso 2: {len(unresolved)} hits com municipio_detectado real mas sem municipio_id')

        n_matched = n_nomatch = 0
        for hit in unresolved:
            muni, conf = _match_municipality(hit.municipio_detectado, muni_idx)
            if muni and conf >= 0.9:
                print(f'  MATCH {conf:.1f}: "{hit.municipio_detectado}" -> {muni.name} (hit id={hit.id})')
                if not args.dry_run:
                    hit.municipio_id = muni.id
                n_matched += 1
            else:
                print(f'  SEM MATCH: "{hit.municipio_detectado}" (hit id={hit.id})')
                n_nomatch += 1

        if not args.dry_run and n_matched > 0:
            db.commit()
        print(f'  Resolvidos: {n_matched} | Sem match: {n_nomatch}')

        # ── Passo 3: propagar municipality_id para artist_contract_appearances ─
        if not args.dry_run and n_matched > 0:
            updated = (
                db.query(ArtistContractAppearance)
                .filter(
                    ArtistContractAppearance.source.in_(["doe", "diogrande"]),
                    ArtistContractAppearance.municipality_id.is_(None),
                )
                .all()
            )
            n_propagated = 0
            hit_cache: dict[int, int | None] = {}
            for app in updated:
                if app.source_ref_id is None:
                    continue
                if app.source_ref_id not in hit_cache:
                    hit = db.get(DiarioOficialHit, app.source_ref_id)
                    hit_cache[app.source_ref_id] = hit.municipio_id if hit else None
                muni_id = hit_cache[app.source_ref_id]
                if muni_id:
                    app.municipality_id = muni_id
                    n_propagated += 1
            if n_propagated:
                db.commit()
            print(f'\nPasso 3: {n_propagated} aparições atualizadas em artist_contract_appearances')
        elif args.dry_run:
            print('\nPasso 3: propagação seria executada após resolução (dry-run)')

        # ── Resumo final ──────────────────────────────────────────────────────
        if not args.dry_run:
            resolved_total = (
                db.query(DiarioOficialHit)
                .filter(
                    DiarioOficialHit.municipio_id.isnot(None),
                    DiarioOficialHit.artista_detectado.isnot(None),
                    DiarioOficialHit.artista_detectado != "",
                )
                .count()
            )
            print(f'\nTotal DOE hits com artista E municipio resolvido: {resolved_total}')
        if args.dry_run:
            print('\n(DRY RUN — nada foi salvo)')

    finally:
        db.close()


if __name__ == "__main__":
    main()
