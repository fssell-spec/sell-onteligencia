"""Cliente HTTP para a API do Diario Oficial do MS."""
import time
from dataclasses import dataclass, field

import requests

DO_BASE = "https://www.diariooficial.ms.gov.br"
_RATE_DELAY = 1.2
_MAX_RETRIES = 3

TIPO_EXATO = 1
TIPO_AO_MENOS_UMA = 2


@dataclass
class DiarioHit:
    numero: int
    descricao: str
    pagina: int
    nome_arquivo: str
    caminho_arquivo: str
    data_publicacao: str
    ocorrencias: int
    highlight: str = ""
    raw: dict = field(repr=False, default_factory=dict)


class DiarioOficialClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": "SELL-Inteligencia-Crawler/1.0",
            "Referer": "https://www.diariooficial.ms.gov.br/",
        })
        self._last_request: float = 0.0

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < _RATE_DELAY:
            time.sleep(_RATE_DELAY - elapsed)
        self._last_request = time.monotonic()

    def search(
        self,
        texto: str,
        tipo: int = TIPO_EXATO,
        data_inicial: str | None = None,
        data_final: str | None = None,
        pagina: int = 1,
        registros_por_pagina: int = 50,
    ) -> dict:
        self._wait()
        params: dict = {
            "tipo": tipo,
            "texto": texto,
            "pagina": pagina,
            "registrosPorPagina": registros_por_pagina,
        }
        if data_inicial:
            params["dataInicial"] = data_inicial
        if data_final:
            params["dataFinal"] = data_final
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._session.get(
                    f"{DO_BASE}/api/diarios/busca-diarios",
                    params=params,
                    timeout=30,
                )
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 400:
                    return {}  # API retorna 400 quando nao ha resultados
                if resp.status_code == 429:
                    time.sleep(5 * (attempt + 1))
                    continue
                print(f"  [HTTP {resp.status_code}] {texto[:40]}")
                return {}
            except requests.RequestException as exc:
                print(f"  [ERRO tentativa {attempt+1}] {exc}")
                time.sleep(2 * (attempt + 1))
        return {}

    def download_page_bytes(self, nome_arquivo: str, pagina: int) -> bytes | None:
        self._wait()
        url = f"{DO_BASE}/api/diarios/baixar-pagina"
        params = {"nomeArquivo": nome_arquivo, "pagina": pagina}
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._session.get(url, params=params, timeout=60)
                if resp.status_code == 200:
                    return resp.content
                if resp.status_code == 429:
                    time.sleep(5 * (attempt + 1))
                    continue
                print(f"  [HTTP {resp.status_code}] {nome_arquivo} p.{pagina}")
                return None
            except requests.RequestException as exc:
                print(f"  [ERRO download tentativa {attempt+1}] {exc}")
                time.sleep(2 * (attempt + 1))
        return None

    def search_all_pages(
        self,
        texto: str,
        tipo: int = TIPO_EXATO,
        data_inicial: str | None = None,
        data_final: str | None = None,
        registros_por_pagina: int = 50,
    ) -> list[DiarioHit]:
        hits: list[DiarioHit] = []
        pagina = 1
        while True:
            data = self.search(
                texto=texto,
                tipo=tipo,
                data_inicial=data_inicial,
                data_final=data_final,
                pagina=pagina,
                registros_por_pagina=registros_por_pagina,
            )
            if not data:
                break
            for item in data.get("paginasDiario") or []:
                hl_list = (item.get("hiHighlight") or {}).get("texto") or []
                hits.append(DiarioHit(
                    numero=item.get("numero", 0),
                    descricao=item.get("descricao", ""),
                    pagina=item.get("pagina", 1),
                    nome_arquivo=item.get("nomeArquivo", ""),
                    caminho_arquivo=item.get("caminhoArquivo", ""),
                    data_publicacao=(item.get("dataPublicacao") or "")[:10],
                    ocorrencias=item.get("ocorrenciasPorPagina", 1),
                    highlight=" | ".join(hl_list),
                    raw=item,
                ))
            total_paginas = data.get("totalDePaginas", 1)
            if pagina >= total_paginas:
                break
            pagina += 1
        return hits
