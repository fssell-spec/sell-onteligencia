# Relink de Contratos + Revisão do Scoring — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-linkar os 466 contratos sem município usando 3 passes (raw_json → regex → Groq) e ajustar os pesos do scoring para que urgência temporal seja o fator dominante.

**Architecture:** Script idempotente `relink_contracts.py` processa contratos com `municipality_id = NULL` em 3 passes sequenciais, gravando o resultado no banco. Em seguida, `opportunity_engine.py` tem seus pesos ajustados e contratos estaduais excluídos do scoring.

**Tech Stack:** Python 3.10, SQLAlchemy, psycopg2, requests (Groq API), pytest. PYTHONPATH deve apontar para `C:/claude/sell-inteligencia`.

---

## File Map

| Arquivo | Ação |
|---------|------|
| `scripts/relink_contracts.py` | Criar — script principal de relinking |
| `analytics/opportunity_engine.py` | Modificar — novos pesos + filtro estadual |
| `tests/test_relink_contracts.py` | Criar — testes unitários do relink |
| `tests/test_opportunity_engine.py` | Criar — testes dos novos pesos |

---

## Task 1: Testes unitários do relink (Pass 1 e 2)

**Files:**
- Create: `tests/test_relink_contracts.py`

- [ ] **Step 1: Criar o arquivo de testes**

```python
# tests/test_relink_contracts.py
"""Testes unitários para a lógica de relinking de contratos."""
import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')

import pytest
from scripts.relink_contracts import extract_from_raw_json, extract_from_texto


NAME_MAP = {
    "corumba": 101,
    "dourados": 102,
    "tres lagoas": 103,
    "campo grande": 104,
    "ponta pora": 105,
}

IBGE_MAP = {
    "5003108": 101,
    "5003504": 102,
    "5008305": 103,
    "5002704": 104,
}


def test_extract_from_raw_json_com_ibge_valido():
    raw = {"unidadeOrgao": {"codigoIbge": 5003108}}
    result = extract_from_raw_json(raw, IBGE_MAP)
    assert result == 101


def test_extract_from_raw_json_sem_ibge():
    raw = {"unidadeOrgao": {}}
    result = extract_from_raw_json(raw, IBGE_MAP)
    assert result is None


def test_extract_from_raw_json_ibge_desconhecido():
    raw = {"unidadeOrgao": {"codigoIbge": 9999999}}
    result = extract_from_raw_json(raw, IBGE_MAP)
    assert result is None


def test_extract_from_raw_json_raw_vazio():
    result = extract_from_raw_json({}, IBGE_MAP)
    assert result is None


def test_extract_from_texto_municipio_de():
    texto = "Contratacao de show no Municipio de Corumba-MS para festa junina"
    result = extract_from_texto(texto, NAME_MAP)
    assert result == 101


def test_extract_from_texto_slash_ms():
    texto = "Show musical em Dourados/MS no dia 15/06"
    result = extract_from_texto(texto, NAME_MAP)
    assert result == 102


def test_extract_from_texto_hifen_ms():
    texto = "Apresentacao artistica em Tres Lagoas-MS"
    result = extract_from_texto(texto, NAME_MAP)
    assert result == 103


def test_extract_from_texto_cidade_de():
    texto = "Realizacao de evento na cidade de Ponta Pora"
    result = extract_from_texto(texto, NAME_MAP)
    assert result == 105


def test_extract_from_texto_sem_municipio():
    texto = "Contratacao de artista para apresentacao musical"
    result = extract_from_texto(texto, NAME_MAP)
    assert result is None


def test_extract_from_texto_none():
    result = extract_from_texto(None, NAME_MAP)
    assert result is None
```

- [ ] **Step 2: Rodar testes para confirmar que falham**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -m pytest tests/test_relink_contracts.py -v 2>&1 | tail -20
```

Esperado: `ImportError` ou `ModuleNotFoundError` (script ainda não existe).

---

## Task 2: Implementar `scripts/relink_contracts.py`

**Files:**
- Create: `scripts/relink_contracts.py`

- [ ] **Step 1: Criar o script com Pass 1 e Pass 2**

```python
# scripts/relink_contracts.py
"""
Re-linka contratos com municipality_id = NULL usando 3 passes:
  Pass 1 — ibge_code do raw_json
  Pass 2 — regex no objeto_descricao
  Pass 3 — Groq LLM (llama-3.1-8b-instant) para os restantes
"""
import argparse
import re
import time
import unicodedata
import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')

from sqlalchemy import text
from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contract import PublicContract
from etl.loaders.contract_loader import build_ibge_map, build_name_map

_REGEX_PATTERNS = [
    re.compile(
        r"(?:no\s+munic[íi]pio\s+de|na\s+cidade\s+de|em)\s+"
        r"([A-ZÀ-Ú][a-zA-ZÀ-ú\s]+?)(?:\s*[-/]\s*MS|\s*,|\s*\.|\s+pelo|\s+por|\s+para|\s*$)",
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


def extract_from_raw_json(raw: dict, ibge_map: dict[str, int]) -> int | None:
    """Pass 1: extrai municipality_id do campo ibge_code no raw_json."""
    unidade = raw.get("unidadeOrgao") or {}
    ibge_raw = unidade.get("codigoIbge")
    if not ibge_raw:
        return None
    return ibge_map.get(str(ibge_raw))


def extract_from_texto(texto: str | None, name_map: dict[str, int]) -> int | None:
    """Pass 2: extrai municipality_id via regex no texto do objeto."""
    if not texto:
        return None
    for pattern in _REGEX_PATTERNS:
        for match in pattern.finditer(texto):
            candidate = _normalize(match.group(1).strip())
            if candidate in name_map:
                return name_map[candidate]
    return None


def extract_from_llm(textos: list[str], name_map: dict[str, int]) -> list[int | None]:
    """Pass 3: usa Groq (llama-3.1-8b-instant) para extrair município."""
    import os
    import requests

    api_key = os.environ.get("GROQ_API_KEY") or _load_env_key()
    if not api_key:
        print("  [AVISO] GROQ_API_KEY não encontrada — Pass 3 pulado.")
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


def _load_env_key() -> str | None:
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
    """Chama Groq e retorna apenas o nome do município."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é um extrator de informações. Leia o texto de um contrato público "
                    "do Mato Grosso do Sul e responda APENAS com o nome do município onde "
                    "o show/evento vai acontecer. Se não encontrar, responda 'DESCONHECIDO'."
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


def relink(dry_run: bool = False, only_pass: int | None = None) -> None:
    db = SessionLocal()
    try:
        ibge_map = build_ibge_map(db)
        name_map = build_name_map(db)

        contratos = (
            db.query(PublicContract)
            .filter(PublicContract.municipality_id.is_(None))
            .all()
        )
        print(f"Contratos sem município: {len(contratos)}")

        pendentes = list(contratos)
        p1 = p2 = p3 = estadual = 0

        # Pass 1 — raw_json ibge_code
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

        # Pass 2 — regex no texto
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

        # Pass 3 — Groq LLM
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

        # Marcar estaduais (Fundação de Cultura)
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
            print("[DRY-RUN] Nenhuma alteração gravada.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-linka contratos sem município.")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem gravar")
    parser.add_argument("--pass", dest="only_pass", type=int, choices=[1, 2, 3], help="Roda só o pass N")
    args = parser.parse_args()
    relink(dry_run=args.dry_run, only_pass=args.only_pass)
```

- [ ] **Step 2: Rodar os testes unitários**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -m pytest tests/test_relink_contracts.py -v 2>&1 | tail -25
```

Esperado: todos os 10 testes passando (PASSED).

- [ ] **Step 3: Rodar dry-run para ver estimativa**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python scripts/relink_contracts.py --dry-run
```

Esperado: log com contagens por pass, linha final `[DRY-RUN] Nenhuma alteração gravada.`

- [ ] **Step 4: Commit**

```bash
cd C:/claude/sell-inteligencia
git add scripts/relink_contracts.py tests/test_relink_contracts.py
git commit -m "feat: relink_contracts.py — 3-pass municipality linking (raw_json, regex, Groq)"
```

---

## Task 3: Executar o relinking no banco

- [ ] **Step 1: Rodar pass 1 e 2 (sem LLM, verificar resultado)**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python scripts/relink_contracts.py --pass 1
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python scripts/relink_contracts.py --pass 2
```

Esperado: log mostrando contratos resolvidos em cada pass.

- [ ] **Step 2: Verificar no banco quantos foram linkados**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -c "
import sys; sys.path.insert(0,'C:/claude/sell-inteligencia')
import logging; logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
total = db.execute(text('SELECT COUNT(*) FROM public_contracts')).scalar()
linkados = db.execute(text('SELECT COUNT(*) FROM public_contracts WHERE municipality_id IS NOT NULL')).scalar()
estaduais = db.execute(text(\"SELECT COUNT(*) FROM public_contracts WHERE extracted_json->>'source_type' = 'estadual'\")).scalar()
print(f'Total: {total} | Linkados: {linkados} | Estaduais: {estaduais} | Sem link: {total - linkados}')
db.close()
"
```

- [ ] **Step 3: Rodar pass 3 (Groq LLM) nos restantes**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python scripts/relink_contracts.py --pass 3
```

Aguardar ~15 minutos. Esperado: log com contratos resolvidos via LLM.

- [ ] **Step 4: Verificar resultado final**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -c "
import sys; sys.path.insert(0,'C:/claude/sell-inteligencia')
import logging; logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
rows = db.execute(text('''
    SELECT m.name, COUNT(*) as n
    FROM public_contracts pc
    JOIN municipalities m ON pc.municipality_id = m.id
    GROUP BY m.name ORDER BY n DESC LIMIT 15
''')).fetchall()
for r in rows:
    print(f'  {r[0]:<30} {r[1]} contratos')
db.close()
"
```

Esperado: distribuição de contratos por município, com vários municípios aparecendo (não só 20 municípios como antes).

---

## Task 4: Testes e ajuste dos pesos do scoring

**Files:**
- Create: `tests/test_opportunity_engine.py`
- Modify: `analytics/opportunity_engine.py` (linhas 25–33)

- [ ] **Step 1: Criar testes para os novos pesos**

```python
# tests/test_opportunity_engine.py
"""Testes para build_opportunity_score com os novos pesos."""
import sys
sys.path.insert(0, 'C:/claude/sell-inteligencia')

from datetime import date
from analytics.opportunity_engine import (
    build_opportunity_score,
    W_JANELA,
    W_HISTORICO_VALOR,
    W_HISTORICO_CONTRATOS,
    W_RECORRENCIA,
    W_CONTATOS,
    W_ANIVERSARIO,
    W_CREDENCIAMENTO,
    W_POPULACAO,
)


def test_pesos_somam_100():
    total = (
        W_JANELA + W_HISTORICO_VALOR + W_HISTORICO_CONTRATOS
        + W_RECORRENCIA + W_CONTATOS + W_ANIVERSARIO
        + W_CREDENCIAMENTO + W_POPULACAO
    )
    assert total == 100, f"Pesos somam {total}, esperado 100"


def test_janela_e_peso_dominante():
    assert W_JANELA >= 25, f"W_JANELA={W_JANELA}, esperado >= 25"


def test_municipio_com_evento_proximo_score_alto():
    """Município com evento no próximo mês deve ter score > 50."""
    today = date(2026, 6, 7)
    # evento em julho (1 mês)
    from unittest.mock import MagicMock
    evento = MagicMock()
    evento.usual_month = 7
    evento.recurrence_pattern = "anual"
    evento.event_type = "festa_junina"

    scores = build_opportunity_score(
        n_contratos=2,
        total_valor=150_000,
        roles={"prefeito"},
        events=[evento],
        population=30_000,
        today=today,
    )
    assert scores["final_opportunity_score"] > 50, (
        f"Score={scores['final_opportunity_score']}, esperado > 50"
    )


def test_municipio_sem_dados_score_baixo():
    """Município sem contratos, sem eventos e sem contatos deve ter score baixo."""
    today = date(2026, 6, 7)
    scores = build_opportunity_score(
        n_contratos=0,
        total_valor=0,
        roles=set(),
        events=[],
        population=5_000,
        today=today,
    )
    assert scores["final_opportunity_score"] < 20


def test_municipio_com_historico_forte_score_medio_alto():
    """Município com bom histórico mas sem evento próximo deve ter score médio."""
    today = date(2026, 6, 7)
    from unittest.mock import MagicMock
    evento = MagicMock()
    evento.usual_month = 12  # 6 meses longe
    evento.recurrence_pattern = "anual"
    evento.event_type = "rodeio"

    scores = build_opportunity_score(
        n_contratos=5,
        total_valor=400_000,
        roles={"prefeito", "secretario_cultura"},
        events=[evento],
        population=50_000,
        today=today,
    )
    assert 30 < scores["final_opportunity_score"] < 75
```

- [ ] **Step 2: Rodar testes — esperar falha em `test_janela_e_peso_dominante`**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -m pytest tests/test_opportunity_engine.py -v 2>&1 | tail -20
```

Esperado: `test_janela_e_peso_dominante` falha (W_JANELA atual = 10, esperado >= 25).

- [ ] **Step 3: Atualizar os pesos em `analytics/opportunity_engine.py`**

Substituir as linhas 25–33:

```python
# Pesos do score (somam 100)
W_HISTORICO_CONTRATOS = 15   # qtd de contratos de show
W_HISTORICO_VALOR     = 20   # valor total gasto em shows
W_CONTATOS            =  8   # prefeito/secretários mapeados
W_RECORRENCIA         = 15   # eventos recorrentes identificados
W_JANELA              = 30   # urgência: evento previsto próximo
W_ANIVERSARIO         =  5   # proximidade do aniversário da cidade
W_POPULACAO           =  2   # tamanho do município
W_CREDENCIAMENTO      =  5   # edital de credenciamento ativo no PNCP
```

- [ ] **Step 4: Adicionar filtro de contratos estaduais em `run()`**

Em `analytics/opportunity_engine.py`, dentro da função `run()`, na linha que filtra `show_contracts_by_muni` (após o `for c in all_contracts:` loop, por volta da linha 295), adicionar o filtro de estaduais:

```python
    for c in all_contracts:
        if c.municipality_id:
            # Ignora contratos marcados como estaduais
            if (c.extracted_json or {}).get("source_type") == "estadual":
                continue
            contracts_by_muni[c.municipality_id].append(c)
            if c.contract_type == ContractType.show_artistico:
                show_contracts_by_muni[c.municipality_id].append(c)
```

- [ ] **Step 5: Rodar todos os testes**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -m pytest tests/test_opportunity_engine.py tests/test_relink_contracts.py -v 2>&1 | tail -25
```

Esperado: todos os testes passando.

- [ ] **Step 6: Commit**

```bash
cd C:/claude/sell-inteligencia
git add analytics/opportunity_engine.py tests/test_opportunity_engine.py
git commit -m "feat: ajusta pesos do scoring — W_JANELA=30 como fator dominante; filtra contratos estaduais"
```

---

## Task 5: Recalcular oportunidades e validar resultado

- [ ] **Step 1: Rodar o motor de oportunidades**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python scripts/run_opportunity_engine.py
```

Esperado: `80 oportunidades calculadas` (ou próximo disso).

- [ ] **Step 2: Verificar distribuição de scores**

```bash
cd C:/claude/sell-inteligencia
PYTHONPATH=C:/claude/sell-inteligencia .venv/Scripts/python -c "
import sys; sys.path.insert(0,'C:/claude/sell-inteligencia')
import logging; logging.disable(logging.CRITICAL)
from app.database import SessionLocal
from app.models.commercial_opportunity import CommercialOpportunity
from app.models.municipality import Municipality
db = SessionLocal()
opps = db.query(CommercialOpportunity).order_by(CommercialOpportunity.final_opportunity_score.desc()).all()
alto = sum(1 for o in opps if (o.final_opportunity_score or 0) >= 60)
medio = sum(1 for o in opps if 30 <= (o.final_opportunity_score or 0) < 60)
baixo = sum(1 for o in opps if (o.final_opportunity_score or 0) < 30)
print(f'Alto(>=60): {alto} | Medio(30-60): {medio} | Baixo(<30): {baixo}')
print('TOP 10:')
for o in opps[:10]:
    m = db.query(Municipality).filter(Municipality.id == o.municipality_id).first()
    print(f'  {o.final_opportunity_score:.0f} | {(m.name if m else \"?\"):<26} | {(o.suggested_next_action or \"\")[:55]}')
db.close()
"
```

Esperado: distribuição mais espalhada (não todos no intervalo 28–37). Municípios com eventos próximos devem aparecer no topo.

- [ ] **Step 3: Confirmar que Campo Grande não está mais inflado**

Campo Grande deve aparecer com score baseado apenas em contratos municipais genuínos (sem a Fundação de Cultura de MS).

- [ ] **Step 4: Acessar o dashboard e verificar a aba Oportunidades**

```bash
# Dashboard já deve estar rodando em localhost:8501
# Abrir http://localhost:8501 → aba Oportunidades
# Verificar: ranking mostra municípios diferentes no topo
# Verificar: mapa de calor tem distribuição mais variada
```

- [ ] **Step 5: Commit final**

```bash
cd C:/claude/sell-inteligencia
git add -A
git commit -m "chore: recalcula oportunidades após relink — 400+ contratos linkados, scoring revisado"
```

---

## Checklist de validação final

- [ ] `relink_contracts.py --dry-run` roda sem erros
- [ ] Todos os testes em `tests/test_relink_contracts.py` passam
- [ ] Todos os testes em `tests/test_opportunity_engine.py` passam
- [ ] Banco tem > 200 contratos com `municipality_id IS NOT NULL` (antes: 36)
- [ ] Contratos da Fundação de Cultura têm `source_type='estadual'` no `extracted_json`
- [ ] Distribuição de scores não é mais todos no intervalo 28–37
- [ ] Dashboard aba Oportunidades mostra ranking diferente do anterior
