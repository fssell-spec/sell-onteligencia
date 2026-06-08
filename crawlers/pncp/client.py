"""Cliente HTTP para a API pública de consultas do PNCP."""
import time
from dataclasses import dataclass, field
from datetime import date

import requests

PNCP_BASE = "https://pncp.gov.br/api/consulta/v1"
_RATE_DELAY = 1.2   # segundos entre requisições (API rate-limita abaixo de ~1s)
_PAGE_SIZE = 50     # limite real da API (docs dizem 500, mas retorna 400 acima de 50)
_MAX_RETRIES = 3

# Modalidades mais relevantes para shows e eventos
MODALIDADES = {
    6: "Pregão Eletrônico",
    7: "Pregão Presencial",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade",
    12: "Credenciamento",
}


@dataclass
class PNCPItem:
    numero_controle: str
    objeto: str
    valor_estimado: float | None
    data_publicacao: str | None        # AAAA-MM-DD
    orgao_cnpj: str | None
    orgao_nome: str | None
    ibge_code: str | None              # 7 dígitos (str)
    municipio_nome: str | None
    uf: str | None
    modalidade_id: int
    modalidade_nome: str
    raw: dict = field(repr=False, default_factory=dict)


def _parse_item(item: dict, modalidade_id: int, modalidade_nome: str) -> PNCPItem:
    unidade = item.get("unidadeOrgao") or {}
    orgao = item.get("orgaoEntidade") or {}
    ibge_raw = unidade.get("codigoIbge")
    return PNCPItem(
        numero_controle=item.get("numeroControlePNCP", ""),
        objeto=item.get("objetoCompra", "") or "",
        valor_estimado=item.get("valorTotalEstimado"),
        data_publicacao=item.get("dataPublicacaoPncp"),
        orgao_cnpj=orgao.get("cnpj"),
        orgao_nome=orgao.get("razaoSocial") or orgao.get("razaosocial"),
        ibge_code=str(ibge_raw) if ibge_raw else None,
        municipio_nome=unidade.get("municipioNome"),
        uf=unidade.get("ufSigla"),
        modalidade_id=modalidade_id,
        modalidade_nome=modalidade_nome,
        raw=item,
    )


class PNCPClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": "SELL-Inteligencia-Crawler/1.0",
        })
        self._last_request: float = 0.0

    def _get(self, path: str, params: dict) -> dict | list | None:
        url = f"{PNCP_BASE}{path}"
        for attempt in range(_MAX_RETRIES):
            elapsed = time.monotonic() - self._last_request
            wait = _RATE_DELAY * (2 ** attempt)
            if elapsed < wait:
                time.sleep(wait - elapsed)
            self._last_request = time.monotonic()
            try:
                resp = self._session.get(url, params=params, timeout=30)
            except requests.RequestException as exc:
                print(f"  [ERRO HTTP tentativa {attempt+1}] {exc}")
                continue
            if resp.status_code == 204 or not resp.content:
                return None
            if resp.status_code == 429:
                print(f"  [429 rate limit] aguardando...")
                time.sleep(5 * (attempt + 1))
                continue
            if resp.status_code != 200:
                if attempt < _MAX_RETRIES - 1:
                    continue
                print(f"  [HTTP {resp.status_code}] params={params}")
                return None
            try:
                return resp.json()
            except ValueError:
                return None
        return None

    def fetch_contratacoes(
        self,
        modalidade_id: int,
        data_inicial: date,
        data_final: date,
        uf: str = "MS",
        ibge_code: str | None = None,
    ) -> list[PNCPItem]:
        """Busca todas as contratações para uma modalidade no período.
        Pagina automaticamente até esgotar os resultados.
        """
        modalidade_nome = MODALIDADES.get(modalidade_id, str(modalidade_id))
        items: list[PNCPItem] = []
        pagina = 1
        while True:
            params: dict = {
                "dataInicial": data_inicial.strftime("%Y%m%d"),
                "dataFinal": data_final.strftime("%Y%m%d"),
                "codigoModalidadeContratacao": modalidade_id,
                "uf": uf,
                "pagina": pagina,
                "tamanhoPagina": _PAGE_SIZE,
            }
            if ibge_code:
                params["codigoMunicipioIbge"] = ibge_code
            data = self._get("/contratacoes/publicacao", params)
            if not data:
                break
            records = data.get("data", []) if isinstance(data, dict) else data
            if not records:
                break
            for item in records:
                items.append(_parse_item(item, modalidade_id, modalidade_nome))
            total_paginas = (
                data.get("totalPaginas", 1) if isinstance(data, dict) else 1
            )
            if pagina >= total_paginas:
                break
            pagina += 1
        return items
