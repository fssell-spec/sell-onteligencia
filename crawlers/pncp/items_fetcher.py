"""Busca itens detalhados de contratos PNCP via api/pncp/v1."""
import re
import time

import requests

_PNCP_V1 = "https://pncp.gov.br/api/pncp/v1"
_SESSION = requests.Session()
_SESSION.headers.update({
    "Accept": "application/json",
    "User-Agent": "SELL-Inteligencia-Crawler/1.0",
})
_last_request: float = 0.0
_RATE_DELAY = 1.2


def _get(url: str) -> list | None:
    global _last_request
    elapsed = time.monotonic() - _last_request
    if elapsed < _RATE_DELAY:
        time.sleep(_RATE_DELAY - elapsed)
    _last_request = time.monotonic()
    try:
        resp = _SESSION.get(url, timeout=20)
    except requests.RequestException:
        return None
    if resp.status_code != 200 or not resp.content:
        return None
    try:
        data = resp.json()
        return data if isinstance(data, list) else None
    except ValueError:
        return None


def _parse_process_number(process_number: str) -> tuple[str, int, int] | None:
    """Extrai (cnpj, anoCompra, sequencialCompra) do numeroControlePNCP.
    Formato: {cnpj}-{seq_orgao}-{seq_compra}/{ano}  ex: 03330461000110-1-000031/2023
    """
    m = re.match(r"^(\d{14})-\d+-0*(\d+)/(\d{4})$", process_number.strip())
    if not m:
        return None
    return m.group(1), int(m.group(3)), int(m.group(2))


def fetch_items(process_number: str, extracted_json: dict | None = None) -> list[dict]:
    """Busca itens de um contrato PNCP.

    Usa extracted_json (cnpj, anoCompra, sequencialCompra) se disponivel;
    caso contrario faz parse do process_number.
    Retorna lista de dicts com descricao, quantidade, unidade, valor.
    """
    cnpj = ano = seq = None

    if extracted_json:
        orgao = extracted_json.get("orgaoEntidade") or {}
        cnpj = orgao.get("cnpj")
        ano = extracted_json.get("anoCompra")
        seq = extracted_json.get("sequencialCompra")

    if not (cnpj and ano and seq):
        parsed = _parse_process_number(process_number or "")
        if not parsed:
            return []
        cnpj, ano, seq = parsed

    url = f"{_PNCP_V1}/orgaos/{cnpj}/compras/{ano}/{seq}/itens"
    items = _get(url)
    if not items:
        return []

    result = []
    for it in items:
        desc = (it.get("descricao") or "").strip()
        if not desc:
            continue
        result.append({
            "descricao": desc,
            "quantidade": it.get("quantidade"),
            "unidade": it.get("unidadeMedida"),
            "valor_unitario": it.get("valorUnitarioEstimado"),
            "valor_total": it.get("valorTotal"),
            "tipo": it.get("materialOuServicoNome"),
            "info": (it.get("informacaoComplementar") or "").strip() or None,
        })
    return result
