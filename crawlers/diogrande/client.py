"""Cliente HTTP para a API de busca do DIOGRANDE (Diário Oficial de Campo Grande - PMCG)."""
import time
from dataclasses import dataclass, field

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIOGRANDE_BASE = "https://diogrande.campogrande.ms.gov.br"
_SEARCH_URL = f"{DIOGRANDE_BASE}/wp-admin/admin-ajax.php"
_RATE_DELAY = 1.5
_MAX_RETRIES = 3

# Colunas que o DataTable do DIOGRANDE espera
_DT_COLUMNS = [
    ("numero",    True,  False),
    ("desctpd",   True,  False),
    ("dia",       True,  False),
    ("codigodia", False, False),
]


@dataclass
class DioGrandeEdicao:
    numero: str
    dia: str       # YYYY-MM-DD
    arquivo: str   # nome do arquivo PDF
    desctpd: str   # OFICIAL | EDIÇÃO EXTRA | SUPLEMENTO I
    codigodia: str
    raw: dict = field(repr=False, default_factory=dict)


class DioGrandeClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"{DIOGRANDE_BASE}/edicoes/",
            "X-Requested-With": "XMLHttpRequest",
        })
        self._last_request: float = 0.0

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < _RATE_DELAY:
            time.sleep(_RATE_DELAY - elapsed)
        self._last_request = time.monotonic()

    def _dt_params(self, palavra: str, de: str, ate: str, start: int, length: int) -> dict:
        p: dict = {
            "action": "edicoes_json",
            "palavra": palavra.upper(),
            "numero": "",
            "de": de,
            "ate": ate,
            "draw": 1,
            "start": start,
            "length": length,
            "order[0][column]": 0,
            "order[0][dir]": "desc",
            "search[value]": "",
            "search[regex]": "false",
        }
        for i, (col, searchable, orderable) in enumerate(_DT_COLUMNS):
            p[f"columns[{i}][data]"] = col
            p[f"columns[{i}][name]"] = ""
            p[f"columns[{i}][searchable]"] = "true" if searchable else "false"
            p[f"columns[{i}][orderable]"] = "true" if orderable else "false"
            p[f"columns[{i}][search][value]"] = ""
            p[f"columns[{i}][search][regex]"] = "false"
        return p

    def search(
        self,
        palavra: str,
        de: str = "",
        ate: str = "",
        start: int = 0,
        length: int = 100,
    ) -> dict:
        self._wait()
        params = self._dt_params(palavra, de, ate, start, length)
        for attempt in range(_MAX_RETRIES):
            try:
                r = self._session.get(_SEARCH_URL, params=params, timeout=30, verify=False)
                if r.status_code == 200:
                    return r.json()
                if r.status_code == 429:
                    time.sleep(5 * (attempt + 1))
                    continue
                print(f"  [HTTP {r.status_code}] {palavra[:40]}")
                return {}
            except Exception as exc:
                print(f"  [ERRO tentativa {attempt+1}] {exc}")
                time.sleep(2 * (attempt + 1))
        return {}

    def search_all(
        self,
        palavra: str,
        de: str = "",
        ate: str = "",
        page_size: int = 100,
    ) -> list[DioGrandeEdicao]:
        """Pagina por todos os resultados de uma busca."""
        edicoes: list[DioGrandeEdicao] = []
        start = 0
        while True:
            data = self.search(palavra=palavra, de=de, ate=ate, start=start, length=page_size)
            records = data.get("data") or []
            for rec in records:
                edicoes.append(DioGrandeEdicao(
                    numero=str(rec.get("numero", "")),
                    dia=(rec.get("dia") or "")[:10],
                    arquivo=rec.get("arquivo", ""),
                    desctpd=rec.get("desctpd", ""),
                    codigodia=str(rec.get("codigodia", "")),
                    raw=rec,
                ))
            total = int(data.get("recordsFiltered") or 0)
            start += page_size
            if start >= total or not records:
                break
        return edicoes
