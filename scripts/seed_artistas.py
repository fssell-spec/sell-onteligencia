"""Seed do catalogo inicial de artistas para o mercado de eventos municipais do MS.

Cobre sertanejo (universitario, raiz, romantico), forro, gospel e samba/pagode (menor volume).

Uso:
  python scripts/seed_artistas.py
  python scripts/seed_artistas.py --limpar   # apaga artistas sem contratos vinculados antes
"""
import argparse
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.artist import Artist

# (nome, main_style, sub_style, fee_tier, popularity_level, origin_city, origin_state)
ARTISTAS = [
    # --- Sertanejo Universitario - Nacional Top (cache >500k) ---
    ("Gusttavo Lima",          "sertanejo", "universitario", "grande",  "nacional_top", "Unai",                 "MG"),
    ("Jorge & Mateus",         "sertanejo", "universitario", "grande",  "nacional_top", "Campo Grande",         "MS"),
    ("Henrique & Juliano",     "sertanejo", "universitario", "grande",  "nacional_top", "Canaverde",            "GO"),
    ("Luan Santana",           "sertanejo", "universitario", "grande",  "nacional_top", "Campo Grande",         "MS"),
    ("Marilia Mendonca",       "sertanejo", "universitario", "grande",  "nacional_top", "Goianesia",            "GO"),
    ("Maiara & Maraisa",       "sertanejo", "universitario", "grande",  "nacional_top", "Goias",                "GO"),
    ("Simone Mendes",          "sertanejo", "universitario", "grande",  "nacional_top", "Simolandia",           "GO"),
    ("Xand Aviao",             "forro",     "universitario", "grande",  "nacional_top", "Fortaleza",            "CE"),
    ("Wesley Safadao",         "forro",     "universitario", "grande",  "nacional_top", "Fortaleza",            "CE"),

    # --- Sertanejo Universitario - Nacional (cache 200k-500k) ---
    ("Diego & Victor Hugo",    "sertanejo", "universitario", "medio",   "nacional",     "Goiania",              "GO"),
    ("Matheus & Kauan",        "sertanejo", "universitario", "medio",   "nacional",     "Trindade",             "GO"),
    ("Joao Neto & Frederico",  "sertanejo", "universitario", "medio",   "nacional",     "Goianesia",            "GO"),
    ("Israel & Rodolffo",      "sertanejo", "universitario", "medio",   "nacional",     "Quirinopolis",         "GO"),
    ("Ze Neto & Cristiano",    "sertanejo", "universitario", "medio",   "nacional",     "Fernandopolis",        "SP"),
    ("Lauana Prado",           "sertanejo", "universitario", "medio",   "nacional",     "Goiania",              "GO"),
    ("Tierry",                 "sertanejo", "universitario", "medio",   "nacional",     "Vitoria da Conquista", "BA"),
    ("Felipe Araujo",          "sertanejo", "universitario", "medio",   "nacional",     "Goiania",              "GO"),
    ("Munhoz & Mariano",       "sertanejo", "universitario", "medio",   "nacional",     "Presidente Prudente",  "SP"),
    ("Marcos & Belutti",       "sertanejo", "universitario", "medio",   "nacional",     "Sao Paulo",            "SP"),
    ("Thiaguinho",             "samba_pagode", "pagode",     "medio",   "nacional",     "Sao Paulo",            "SP"),

    # --- Sertanejo Raiz/Romantico - Nacional (cache 200k-500k) ---
    ("Zeze di Camargo & Luciano", "sertanejo", "raiz",       "medio",   "nacional",     "Pirenopolis",          "GO"),
    ("Bruno & Marrone",        "sertanejo", "romantico",     "medio",   "nacional",     "Campo Grande",         "MS"),
    ("Leonardo",               "sertanejo", "romantico",     "medio",   "nacional",     "Goianesia",            "GO"),
    ("Chitaozinho & Xororo",   "sertanejo", "raiz",          "medio",   "nacional",     "Astorga",              "PR"),
    ("Fernando & Sorocaba",    "sertanejo", "universitario", "medio",   "nacional",     "Sorocaba",             "SP"),
    ("Eduardo Costa",          "sertanejo", "romantico",     "medio",   "nacional",     "Uberaba",              "MG"),
    ("Roberta Miranda",        "sertanejo", "romantico",     "pequeno", "nacional",     "Sao Paulo",            "SP"),
    ("Rionegro & Solimoes",    "sertanejo", "raiz",          "pequeno", "nacional",     "Sao Paulo",            "SP"),

    # --- Sertanejo - Pequeno (cache 50k-200k, alcance nacional/estadual) ---
    ("Victor & Leo",           "sertanejo", "universitario", "pequeno", "nacional",     "Carangola",            "MG"),
    ("Joao Lucas & Marcelo",   "sertanejo", "universitario", "pequeno", "nacional",     "Sao Paulo",            "SP"),
    ("Trio Parada Dura",       "sertanejo", "raiz",          "pequeno", "nacional",     "Sao Paulo",            "SP"),
    ("Brenno & Matheus",       "sertanejo", "universitario", "pequeno", "estadual",     "Sidrolandia",          "MS"),
    ("Almir Sater",            "sertanejo", "raiz",          "pequeno", "nacional",     "Campo Grande",         "MS"),

    # --- Forro - Nacional ---
    ("Calcinha Preta",         "forro",     "tradicional",   "medio",   "nacional",     "Aracaju",              "SE"),
    ("Solteiroes do Forro",    "forro",     "universitario", "medio",   "nacional",     "Fortaleza",            "CE"),

    # --- Gospel - Nacional ---
    ("Aline Barros",           "gospel",    "gospel",        "pequeno", "nacional",     "Caratinga",            "MG"),
    ("Fernanda Brum",          "gospel",    "gospel",        "pequeno", "nacional",     "Rio de Janeiro",       "RJ"),
    ("Anderson Freire",        "gospel",    "gospel",        "pequeno", "nacional",     "Goiania",              "GO"),
    ("Leonardo Goncalves",     "gospel",    "gospel",        "micro",   "nacional",     "Sao Paulo",            "SP"),
    ("Ministerio Zoe",         "gospel",    "louvor",        "pequeno", "nacional",     "Curitiba",             "PR"),

    # --- Samba/Pagode - Nacional (menor volume) ---
    ("Pericles",               "samba_pagode", "pagode",     "pequeno", "nacional",     "Sao Paulo",            "SP"),
    ("Dilsinho",               "samba_pagode", "pagode",     "pequeno", "nacional",     "Rio de Janeiro",       "RJ"),
    ("Grupo Fundo de Quintal", "samba_pagode", "samba",      "pequeno", "nacional",     "Rio de Janeiro",       "RJ"),
]


def normalize(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return nfkd.encode("ascii", "ignore").decode("ascii").lower().strip()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed catalogo de artistas")
    p.add_argument("--limpar", action="store_true", help="Remove artistas sem contratos antes de inserir")
    return p.parse_args()


def seed(limpar: bool = False) -> None:
    db = SessionLocal()
    try:
        if limpar:
            sem_contratos = (
                db.query(Artist)
                .filter(~Artist.contracts.any())
                .all()
            )
            if sem_contratos:
                for a in sem_contratos:
                    db.delete(a)
                db.commit()
                print(f"Removidos {len(sem_contratos)} artistas sem contratos.")

        inseridos = atualizados = ignorados = 0

        for (nome, main_style, sub_style, fee_tier, popularity_level, origin_city, origin_state) in ARTISTAS:
            norm = normalize(nome)
            existing = db.query(Artist).filter_by(normalized_name=norm).first()

            if existing:
                changed = False
                if not existing.main_style:
                    existing.main_style = main_style
                    changed = True
                if not existing.sub_style:
                    existing.sub_style = sub_style
                    changed = True
                if not existing.fee_tier:
                    existing.fee_tier = fee_tier
                    changed = True
                if not existing.popularity_level:
                    existing.popularity_level = popularity_level
                    changed = True
                if not existing.origin_city:
                    existing.origin_city = origin_city
                    changed = True
                if not existing.origin_state:
                    existing.origin_state = origin_state
                    changed = True
                if changed:
                    atualizados += 1
                else:
                    ignorados += 1
            else:
                db.add(Artist(
                    name=nome,
                    normalized_name=norm,
                    main_style=main_style,
                    sub_style=sub_style,
                    fee_tier=fee_tier,
                    popularity_level=popularity_level,
                    origin_city=origin_city,
                    origin_state=origin_state,
                ))
                inseridos += 1

        db.commit()
        print(f"OK: {inseridos} inseridos | {atualizados} atualizados | {ignorados} ja existiam")

        total = db.query(Artist).count()
        print(f"Total de artistas no banco: {total}")

    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    args = parse_args()
    seed(limpar=args.limpar)
