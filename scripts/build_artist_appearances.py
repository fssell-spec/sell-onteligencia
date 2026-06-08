"""Constrói (ou reconstrói) artist_contract_appearances a partir do PNCP e DOE.

Cruza artistas × municípios × contratos em uma tabela unificada que serve
de fonte única de verdade para o dashboard e o motor de oportunidades.

Fontes:
  pncp  — public_contracts com artist_id já resolvido pelo LLM extractor
  doe   — diario_oficial_hits com artista_detectado (matching fuzzy contra artists)

Uso:
  python scripts/build_artist_appearances.py            # adiciona novos
  python scripts/build_artist_appearances.py --rebuild  # limpa e reconstrói
  python scripts/build_artist_appearances.py --dry-run  # exibe sem salvar
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.artist import Artist
from app.models.artist_contract_appearance import ArtistContractAppearance
from app.models.diario_oficial_hit import DiarioOficialHit
from app.models.public_contract import PublicContract

# ── Normalização ───────────────────────────────────────────────────────────────

def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = "".join(c for c in s if c.isalnum() or c.isspace())
    return " ".join(s.split())


_NOISE = {
    "show", "apresentacao", "artis", "projeto", "acoes", "contrat",
    "producao", "evento", "cultural", "musical", "espetaculo", "teatral",
    "formacao", "capacitacao", "oficina", "palestra",
}


def _is_valid_name(name: str) -> bool:
    n = name.lower().strip()
    if len(n) < 4:
        return False
    return not any(p in n for p in _NOISE)


_SPLITTER = re.compile(r"[,;]|\s+e\s+", re.IGNORECASE)


def _split_names(raw: str) -> list[str]:
    """Separa strings multi-artista como 'Banda V12, Banda Alzira's, Max Henrique'."""
    parts = _SPLITTER.split(raw)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) >= 4]


# ── Índice de artistas ─────────────────────────────────────────────────────────

ArtistIndex = dict[str, Artist]


def _build_index(db) -> ArtistIndex:
    artists = db.query(Artist).all()
    idx: ArtistIndex = {}
    for a in artists:
        if a.name:
            idx[_normalize(a.name)] = a
        if a.normalized_name:
            idx[_normalize(a.normalized_name)] = a
    return idx


def _match(raw: str, idx: ArtistIndex) -> tuple[Artist | None, float]:
    """Retorna (artist, confidence) ou (None, 0.0).

    Estratégias em ordem decrescente de confiança:
      1.0 — match exato após normalização
      0.9 — um contém o outro (mínimo 4 chars)
      0.7 — primeira palavra do raw bate com início da chave (mín. 5 chars)
    """
    norm = _normalize(raw)
    if not norm:
        return None, 0.0

    # 1. Exato
    if norm in idx:
        return idx[norm], 1.0

    # 2. Contém
    for key, artist in idx.items():
        if len(key) >= 4 and (key in norm or norm in key):
            return artist, 0.9

    # 3. Primeira palavra
    words = norm.split()
    if words and len(words[0]) >= 5:
        for key, artist in idx.items():
            if key.startswith(words[0]):
                return artist, 0.7

    return None, 0.0


# ── Inserção única ─────────────────────────────────────────────────────────────

def _upsert(
    db,
    artist_id: int,
    municipality_id: int | None,
    source: str,
    source_ref_id: int,
    cache_value: float | None,
    event_date,
    publication_date,
    raw_artist_name: str,
    match_confidence: float,
    dry_run: bool,
    seen: set,
) -> bool:
    """Retorna True se inseriu, False se já existia."""
    key = (source, source_ref_id, artist_id)
    if key in seen:
        return False
    exists = (
        db.query(ArtistContractAppearance)
        .filter_by(source=source, source_ref_id=source_ref_id, artist_id=artist_id)
        .first()
    )
    if exists:
        seen.add(key)
        return False
    if not dry_run:
        db.add(ArtistContractAppearance(
            artist_id=artist_id,
            municipality_id=municipality_id,
            source=source,
            source_ref_id=source_ref_id,
            cache_value=cache_value,
            event_date=event_date,
            publication_date=publication_date,
            raw_artist_name=raw_artist_name,
            match_confidence=match_confidence,
        ))
    seen.add(key)
    return True


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói artist_contract_appearances")
    parser.add_argument("--rebuild", action="store_true", help="Limpa e reconstrói do zero")
    parser.add_argument("--dry-run", action="store_true", help="Exibe sem salvar")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        idx = _build_index(db)
        print(f"Artistas indexados: {len(idx)} entradas (pode haver duplicatas de normalized)")

        if args.rebuild and not args.dry_run:
            n = db.query(ArtistContractAppearance).delete()
            db.commit()
            print(f"Removidas {n} aparicoes anteriores (rebuild)")

        # ── PNCP ──────────────────────────────────────────────────────────────
        pncp = (
            db.query(PublicContract)
            .filter(PublicContract.artist_id.isnot(None))
            .all()
        )
        print(f"\nPNCP: {len(pncp)} contratos com artist_id")

        seen: set = set()
        n_pncp_new = n_pncp_dup = 0
        for c in pncp:
            val = float(c.contract_value) if c.contract_value and float(c.contract_value) > 0 else None
            inserted = _upsert(
                db=db,
                artist_id=c.artist_id,
                municipality_id=c.municipality_id,
                source="pncp",
                source_ref_id=c.id,
                cache_value=val,
                event_date=c.event_date,
                publication_date=c.publication_date,
                raw_artist_name="",
                match_confidence=1.0,
                dry_run=args.dry_run,
                seen=seen,
            )
            if inserted:
                n_pncp_new += 1
            else:
                n_pncp_dup += 1

        if not args.dry_run:
            db.commit()
        print(f"  Novas: {n_pncp_new} | Duplicatas: {n_pncp_dup}")

        # ── DOE / DIOGRANDE ───────────────────────────────────────────────────
        doe_hits = (
            db.query(DiarioOficialHit)
            .filter(
                DiarioOficialHit.artista_detectado.isnot(None),
                DiarioOficialHit.artista_detectado != "",
            )
            .all()
        )
        print(f"\nDOE/DIOGRANDE: {len(doe_hits)} hits com artista_detectado")

        n_doe_new = n_doe_dup = n_doe_nomatch = n_doe_noise = 0
        unmatched: dict[str, int] = {}

        for hit in doe_hits:
            raw = hit.artista_detectado
            if not _is_valid_name(raw):
                n_doe_noise += 1
                continue

            parts = _split_names(raw)
            if not parts:
                parts = [raw]

            for part in parts:
                if not _is_valid_name(part):
                    continue
                artist, conf = _match(part, idx)
                if artist is None or conf < 0.7:
                    n_doe_nomatch += 1
                    unmatched[part] = unmatched.get(part, 0) + 1
                    continue

                val = float(hit.valor_estimado) if hit.valor_estimado and float(hit.valor_estimado) > 0 else None
                src = hit.raw_json.get("fonte", "doe") if hit.raw_json else "doe"
                inserted = _upsert(
                    db=db,
                    artist_id=artist.id,
                    municipality_id=hit.municipio_id,
                    source=src,
                    source_ref_id=hit.id,
                    cache_value=val,
                    event_date=None,
                    publication_date=hit.data_publicacao,
                    raw_artist_name=part,
                    match_confidence=conf,
                    dry_run=args.dry_run,
                    seen=seen,
                )
                if inserted:
                    n_doe_new += 1
                else:
                    n_doe_dup += 1

        if not args.dry_run:
            db.commit()

        print(f"  Novas: {n_doe_new} | Duplicatas: {n_doe_dup} | Sem match: {n_doe_nomatch} | Ruido: {n_doe_noise}")

        if unmatched:
            top = sorted(unmatched.items(), key=lambda x: -x[1])[:15]
            print(f"\n  Top nomes sem match no catalogo (candidatos para adicionar):")
            for name, cnt in top:
                print(f"    {cnt}x  {name}")

        total = (
            db.query(ArtistContractAppearance).count()
            if not args.dry_run
            else n_pncp_new + n_doe_new
        )
        print(f"\nTotal em artist_contract_appearances: {total}")
        if args.dry_run:
            print("(DRY RUN — nada foi salvo)")

    finally:
        db.close()


if __name__ == "__main__":
    main()
