"""Importa prefeitos eleitos em 2024 via dados abertos do TSE.

Uso:
  python scripts/seed_prefeitos_tse.py
  python scripts/seed_prefeitos_tse.py --dry-run
"""
import argparse
import io
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact

TSE_CAND_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2024.zip"
TSE_SOCIAL_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/rede_social_candidato_2024.zip"
ROLE = "prefeito"


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text.upper()).encode("ascii", "ignore").decode().strip()


def _fmt_phone(raw: str | None) -> str | None:
    if not raw or str(raw).strip() in ("", "#NULO#", "-1"):
        return None
    digits = "".join(c for c in str(raw) if c.isdigit())
    if not digits or digits == "0":
        return None
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return digits


def _clean(val) -> str | None:
    if pd.isna(val):
        return None
    s = str(val).strip()
    return None if s in ("", "#NULO#", "-1") else s


def _download_zip_ms(url: str, label: str, state: str = "MS") -> pd.DataFrame:
    print(f"Baixando {label}: {url}")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        target = next((n for n in names if f"_{state}." in n.upper()), names[0])
        print(f"  Lendo: {target}")
        with zf.open(target) as f:
            df = pd.read_csv(f, sep=";", encoding="latin-1", dtype=str, low_memory=False)
    print(f"  {len(df)} linhas carregadas")
    return df


def download_csv() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_cand = _download_zip_ms(TSE_CAND_URL, "candidatos 2024")
    df_social = _download_zip_ms(TSE_SOCIAL_URL, "redes sociais 2024")
    return df_cand, df_social


def filter_prefeitos(df: pd.DataFrame) -> pd.DataFrame:
    cargo_col = next(c for c in df.columns if "DS_CARGO" in c.upper())
    sit_col = next(c for c in df.columns if "CD_SIT_TOT_TURNO" in c.upper())
    turno_col = next((c for c in df.columns if c.upper() == "NR_TURNO"), None)
    mun_col = next(c for c in df.columns if "NM_UE" in c.upper())

    mask = (df[cargo_col].str.strip().str.upper() == "PREFEITO") & (df[sit_col].str.strip() == "1")
    eleitos = df[mask].copy()

    # Para municipios com 2 turnos, manter apenas o de turno mais alto (resultado final)
    if turno_col:
        eleitos[turno_col] = pd.to_numeric(eleitos[turno_col], errors="coerce")
        eleitos = eleitos.sort_values(turno_col, ascending=False).drop_duplicates(subset=[mun_col])

    print(f"  {len(eleitos)} prefeitos eleitos no MS")
    return eleitos


def build_name_map(db) -> dict[str, Municipality]:
    rows = db.query(Municipality).filter(Municipality.state == "MS").all()
    return {_normalize(m.name): m for m in rows}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Nao salva no banco")
    return p.parse_args()


def build_social_map(df_social: pd.DataFrame) -> dict[str, dict]:
    """Retorna {sq_candidato: {instagram_url, facebook_url}}. Tipo detectado pelo dominio."""
    col = {c.upper(): c for c in df_social.columns}
    sq_col = col.get("SQ_CANDIDATO")
    url_col = col.get("DS_URL")
    if not sq_col or not url_col:
        print(f"  Colunas redes sociais nao encontradas: {list(df_social.columns)}")
        return {}
    result: dict[str, dict] = {}
    for _, row in df_social.iterrows():
        sq = str(row[sq_col]).strip()
        url = str(row[url_col]).strip()
        if not url or url in ("nan", ""):
            continue
        if sq not in result:
            result[sq] = {}
        if "instagram.com" in url.lower():
            result[sq].setdefault("instagram_url", url)
        elif "facebook.com" in url.lower():
            result[sq].setdefault("facebook_url", url)
    return result


def main():
    args = parse_args()
    df_raw, df_social = download_csv()
    df = filter_prefeitos(df_raw)
    social_map = build_social_map(df_social)
    print(f"  {len(social_map)} candidatos com redes sociais")

    col = {c.upper(): c for c in df.columns}

    def get(row, key):
        return _clean(row.get(col.get(key)))

    db = SessionLocal()
    try:
        name_map = build_name_map(db)
        created = updated = unmatched = 0
        unmatched_names = []

        for _, row in df.iterrows():
            mun_name = get(row, "NM_UE") or ""
            mun = name_map.get(_normalize(mun_name))
            if not mun:
                unmatched += 1
                unmatched_names.append(mun_name)
                continue

            nome = get(row, "NM_CANDIDATO")
            partido = get(row, "SG_PARTIDO")
            email = get(row, "DS_EMAIL")
            telefone = _fmt_phone(get(row, "NR_TELEFONE"))
            celular = _fmt_phone(get(row, "NR_CELULAR"))
            tse_id = get(row, "SQ_CANDIDATO") or get(row, "NR_CPF_CANDIDATO")
            phone = celular or telefone
            socials = social_map.get(str(tse_id).strip(), {})

            existing = (
                db.query(PublicContact)
                .filter(
                    PublicContact.municipality_id == mun.id,
                    PublicContact.role == ROLE,
                )
                .first()
            )

            if existing:
                existing.name = nome
                existing.party = partido
                existing.email = email
                existing.phone = phone
                existing.tse_id = tse_id
                existing.instagram_url = socials.get("instagram_url")
                existing.facebook_url = socials.get("facebook_url")
                existing.source_url = TSE_CAND_URL
                existing.confidence_score = 1.0
                updated += 1
                status = "atualizado"
            else:
                contact = PublicContact(
                    municipality_id=mun.id,
                    name=nome,
                    role=ROLE,
                    party=partido,
                    email=email,
                    phone=phone,
                    tse_id=tse_id,
                    instagram_url=socials.get("instagram_url"),
                    facebook_url=socials.get("facebook_url"),
                    source_url=TSE_CAND_URL,
                    confidence_score=1.0,
                )
                db.add(contact)
                created += 1
                status = "criado"

            ig = "ig" if socials.get("instagram_url") else "  "
            fb = "fb" if socials.get("facebook_url") else "  "
            ph = "tel" if phone else "   "
            em = "email" if email else "     "
            print(f"  {mun.name:<25} {nome:<35} {partido:<8} [{ig}][{fb}][{ph}][{em}] {status}")

        if not args.dry_run:
            db.commit()
            print(f"\nSalvo no banco.")
        else:
            db.rollback()
            print(f"\nDry-run — nenhuma alteracao salva.")

        print(
            f"\nResultado: {created} criados | {updated} atualizados | {unmatched} sem match"
        )
        if unmatched_names:
            print(f"Sem match: {unmatched_names}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
