"""Descobre e salva as URLs dos sites oficiais das prefeituras do MS.

Testa padroes de URL comuns (*.ms.gov.br) para cada municipio.
Nao usa LLM — apenas requisicoes HTTP.

Uso:
  python scripts/seed_websites_ms.py
  python scripts/seed_websites_ms.py --dry-run
"""
import argparse
import sys
import time
import unicodedata
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.municipality import Municipality

TIMEOUT = 8
SLEEP_BETWEEN = 0.3

# Overrides manuais para municipios com URLs nao-padrao
URL_OVERRIDES: dict[str, str] = {
    "Paraíso das Águas":       "https://www.paraisodaguasms.com.br",
    "Dois Irmãos do Buriti":   "https://www.doisirmaosdoburiti.ms.gov.br",
    "Glória de Dourados":      "https://www.gloriadedourados.ms.gov.br",
    "São Gabriel do Oeste":    "https://www.saogabriel.ms.gov.br",
    # Municipios que nao seguem o padrao slug simples
    "Campo Grande":            "https://www.campogrande.ms.gov.br",
    "Caracol":                 "https://www.caracolms.ms.gov.br",
    "Guia Lopes da Laguna":    "https://www.guialopes.ms.gov.br",
    "Nova Alvorada do Sul":    "https://www.novaalvorada.ms.gov.br",
    "Nova Andradina":          "https://www.novaandradina.ms.gov.br",
    "Novo Horizonte do Sul":   "https://www.novohorizontedosul.ms.gov.br",
    "Rio Verde de Mato Grosso":"https://www.rioverde.ms.gov.br",
    "Sul Brasil":              "https://www.sulbrasil.ms.gov.br",
    "Água Clara":              "https://www.aguaclara.ms.gov.br",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SellInteligencia/1.0)"}

# Suprime aviso de SSL para sites governamentais com certificado invalido
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _slug(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return nfkd.encode("ascii", "ignore").decode().lower().replace(" ", "").replace("-", "")


def _slug_hyphen(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return nfkd.encode("ascii", "ignore").decode().lower().replace(" ", "-")


def _is_alive(url: str) -> bool:
    try:
        resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers=HEADERS, verify=False)
        return resp.status_code < 400
    except Exception:
        return False


def find_url(name: str) -> str | None:
    # Overrides: confiar sem checar conectividade
    if name in URL_OVERRIDES:
        return URL_OVERRIDES[name]

    s = _slug(name)
    sh = _slug_hyphen(name)

    candidates = [
        f"https://www.{s}.ms.gov.br",
        f"https://www.{sh}.ms.gov.br",
        f"https://{s}.ms.gov.br",
        f"https://{sh}.ms.gov.br",
        f"https://www.prefeitura{s}.ms.gov.br",
        f"https://prefeitura.{s}.ms.gov.br",
    ]

    for url in candidates:
        if _is_alive(url):
            return url
        time.sleep(0.1)
    return None


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Nao salva no banco")
    p.add_argument("--only-missing", action="store_true", help="Pula municipios que ja tem URL")
    return p.parse_args()


def main():
    args = parse_args()
    db = SessionLocal()
    try:
        munis = db.query(Municipality).filter(Municipality.state == "MS").order_by(Municipality.name).all()
        if args.only_missing:
            munis = [m for m in munis if not m.official_website]
            print(f"Processando apenas os {len(munis)} sem URL cadastrada")

        found = updated = skipped = 0
        not_found_names = []

        for mun in munis:
            url = find_url(mun.name)
            time.sleep(SLEEP_BETWEEN)

            if url:
                found += 1
                if mun.official_website != url:
                    if not args.dry_run:
                        mun.official_website = url
                    updated += 1
                    status = "OK"
                else:
                    skipped += 1
                    status = "ja ok"
                print(f"  {status:<6} {mun.name:<30} {url}")
            else:
                not_found_names.append(mun.name)
                print(f"  MISS   {mun.name:<30} nao encontrado")

        if not args.dry_run:
            db.commit()
            print(f"\nSalvo no banco.")
        else:
            db.rollback()
            print(f"\nDry-run — nada salvo.")

        print(f"\nResultado: {found} encontrados | {updated} atualizados | {len(not_found_names)} sem URL")
        if not_found_names:
            print(f"Sem URL: {not_found_names}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
