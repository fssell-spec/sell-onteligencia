# scripts/relink_contracts.py
"""
Re-linka contratos com municipality_id = NULL usando 3 passes:
  Pass 1 — ibge_code do raw_json
  Pass 2 — regex no objeto_descricao
  Pass 3 — Groq LLM (llama-3.1-8b-instant) para os restantes
"""
import argparse
import os
import re
import requests
import time
import unicodedata
import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')

from sqlalchemy import text
from app.database import SessionLocal
from app.models.public_contract import PublicContract
from etl.loaders.contract_loader import build_ibge_map, build_name_map

_REGEX_PATTERNS = [
    re.compile(
        r"(?:no\s+munic[íi]pio\s+de|na\s+cidade\s+de|em)\s+"
        r"([A-ZÀ-Ú][a-zA-ZÀ-ú\s]+?)(?:\s*[-/]\s*MS|\s*,|\s*\.|\s+pelo\b|\s+por\b|\s+para\b|\s*$)",
        re.IGNORECASE,
    ),
    re.compile(r"([A-ZÀ-Ú][a-zA-ZÀ-ú\s]+?)\s*[-/]\s*MS\b"),
]

FUNDACAO_CULTURA_CNPJ = "15579196000198"


def _normalize(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()


def extract_from_raw_json(raw: dict, ibge_map: dict) -> int | None:
    """Pass 1: extrai municipality_id do campo ibge_code no raw_json."""
    unidade = raw.get("unidadeOrgao") or {}
    ibge_raw = unidade.get("codigoIbge")
    if not ibge_raw:
        return None
    return ibge_map.get(str(ibge_raw))


def extract_from_texto(texto, name_map: dict) -> int | None:
    """Pass 2: extrai municipality_id via regex no texto do objeto."""
    if not texto:
        return None
    for pattern in _REGEX_PATTERNS:
        for match in pattern.finditer(texto):
            candidate = _normalize(match.group(1).strip())
            if candidate in name_map:
                return name_map[candidate]
    return None


def extract_from_llm(textos: list, name_map: dict) -> list:
    """Pass 3: usa Groq (llama-3.1-8b-instant) para extrair município."""
    api_key = os.environ.get("GROQ_API_KEY") or _load_env_key()
    if not api_key:
        print("  [AVISO] GROQ_API_KEY nao encontrada -- Pass 3 pulado.")
        return [None] * len(textos)

    results = []
    batch_size = 10
    for i in range(0, len(textos), batch_size):
        batch = textos[i : i + batch_size]
        for texto in batch:
            try:
                resp = _groq_request(api_key, texto)
                nome = _normalize(resp.strip().split("\n")[0])
                results.append(name_map.get(nome))
            except Exception as e:
                print(f"  [ERRO Groq] {e}")
                results.append(None)
        if i + batch_size < len(textos):
            time.sleep(1)
    return results


def _load_env_key():
    """Carrega GROQ_API_KEY do arquivo .env na raiz do projeto."""
    env_path = "C:/claude/sell-inteligencia/.env"
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GROQ_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return None


def _groq_request(api_key: str, texto: str) -> str:
    """Chama Groq e retorna apenas o nome do municipio."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Voce e um extrator de informacoes. Leia o texto de um contrato publico "
                    "do Mato Grosso do Sul e responda APENAS com o nome do municipio onde "
                    "o show/evento vai acontecer. Se nao encontrar, responda 'DESCONHECIDO'."
                ),
            },
            {"role": "user", "content": texto[:500]},
        ],
        "max_tokens": 20,
        "temperature": 0,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(3):
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    return "DESCONHECIDO"


def _mark_estadual(db, contract_id: int) -> None:
    """Marca contrato como estadual no extracted_json."""
    db.execute(
        text("""
            UPDATE public_contracts
            SET extracted_json = COALESCE(extracted_json, '{}')::jsonb || '{"source_type": "estadual"}'
            WHERE id = :id
        """),
        {"id": contract_id},
    )


def relink(dry_run: bool = False, only_pass=None) -> None:
    db = SessionLocal()
    try:
        ibge_map = build_ibge_map(db)
        name_map = build_name_map(db)

        contratos = (
            db.query(PublicContract)
            .filter(PublicContract.municipality_id.is_(None))
            .all()
        )
        print(f"Contratos sem municipio: {len(contratos)}")

        pendentes = list(contratos)
        p1 = p2 = p3 = estadual = 0

        # Pass 1 -- raw_json ibge_code
        if only_pass in (None, 1):
            restantes = []
            for c in pendentes:
                raw = c.extracted_json or {}
                muni_id = extract_from_raw_json(raw, ibge_map)
                if muni_id:
                    if not dry_run:
                        c.municipality_id = muni_id
                    p1 += 1
                else:
                    restantes.append(c)
            pendentes = restantes
            print(f"Pass 1 (raw_json ibge): {p1} resolvidos")

        # Pass 2 -- regex no texto
        if only_pass in (None, 2):
            restantes = []
            for c in pendentes:
                muni_id = extract_from_texto(c.object_description, name_map)
                if muni_id:
                    if not dry_run:
                        c.municipality_id = muni_id
                    p2 += 1
                else:
                    restantes.append(c)
            pendentes = restantes
            print(f"Pass 2 (regex texto):   {p2} resolvidos")

        # Pass 3 -- Groq LLM
        if only_pass in (None, 3) and pendentes:
            textos = [c.object_description or "" for c in pendentes]
            llm_results = extract_from_llm(textos, name_map)
            restantes = []
            for c, muni_id in zip(pendentes, llm_results):
                if muni_id:
                    if not dry_run:
                        c.municipality_id = muni_id
                    p3 += 1
                else:
                    restantes.append(c)
            pendentes = restantes
            print(f"Pass 3 (Groq LLM):      {p3} resolvidos")

        # Marcar estaduais (Fundacao de Cultura)
        for c in pendentes:
            doc = (c.supplier_document or "").replace(".", "").replace("/", "").replace("-", "")
            if doc == FUNDACAO_CULTURA_CNPJ.replace(".", "").replace("/", "").replace("-", ""):
                if not dry_run:
                    _mark_estadual(db, c.id)
                estadual += 1

        if not dry_run:
            db.commit()

        sem_link = len(pendentes) - estadual
        print(f"Estadual (sem link):    {estadual} marcados")
        print(f"Sem link restantes:     {sem_link}")
        print(f"Total linkados: {p1 + p2 + p3} / {len(contratos)}")
        if dry_run:
            print("[DRY-RUN] Nenhuma alteracao gravada.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-linka contratos sem municipio.")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem gravar")
    parser.add_argument("--pass", dest="only_pass", type=int, choices=[1, 2, 3], help="Roda so o pass N")
    args = parser.parse_args()
    relink(dry_run=args.dry_run, only_pass=args.only_pass)
