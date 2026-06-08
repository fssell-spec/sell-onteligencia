"""Coleta publicações do DIOGRANDE com keywords de shows/artistas."""
from dataclasses import dataclass
from datetime import date

from crawlers.diogrande.client import DioGrandeClient, DioGrandeEdicao
from crawlers.diogrande.keywords import BUSCAS_DG


@dataclass
class DGCollectedHit:
    edicao: DioGrandeEdicao
    keyword: str


class DioGrandeCollector:
    def __init__(self, client: DioGrandeClient | None = None) -> None:
        self._client = client or DioGrandeClient()

    def collect(
        self,
        data_inicial: date,
        data_final: date,
        buscas: list[str] | None = None,
    ) -> list[DGCollectedHit]:
        """Busca por todas as keywords no período. Dedup por (arquivo, keyword)."""
        terms = buscas or BUSCAS_DG
        de = data_inicial.strftime("%d/%m/%Y")
        ate = data_final.strftime("%d/%m/%Y")

        seen: set[tuple[str, str]] = set()
        results: list[DGCollectedHit] = []

        for kw in terms:
            print(f"  DG buscando: '{kw}' [{de} - {ate}]", end=" ", flush=True)
            edicoes = self._client.search_all(palavra=kw, de=de, ate=ate)
            novos = 0
            for ed in edicoes:
                key = (ed.arquivo, kw.lower())
                if key not in seen:
                    seen.add(key)
                    results.append(DGCollectedHit(edicao=ed, keyword=kw))
                    novos += 1
            print(f"-> {len(edicoes)} resultados, {novos} novos")

        return results
