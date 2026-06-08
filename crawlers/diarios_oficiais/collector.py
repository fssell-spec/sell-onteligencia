"""Coleta publicacoes do Diario Oficial do MS relacionadas a shows e artistas."""
from dataclasses import dataclass
from datetime import date

from crawlers.diarios_oficiais.client import DiarioHit, DiarioOficialClient
from crawlers.diarios_oficiais.keywords import BUSCAS


@dataclass
class DOCollectedHit:
    hit: DiarioHit
    keyword: str


class DiarioOficialCollector:
    def __init__(self, client: DiarioOficialClient | None = None) -> None:
        self._client = client or DiarioOficialClient()

    def collect(
        self,
        data_inicial: date,
        data_final: date,
        buscas: list[tuple[str, int]] | None = None,
    ) -> list[DOCollectedHit]:
        """Busca no DO por todas as keywords no periodo. Dedup por (arquivo, pagina)."""
        terms = buscas or BUSCAS
        seen: set[tuple[str, int]] = set()
        results: list[DOCollectedHit] = []

        inicio_str = data_inicial.strftime("%Y-%m-%d")
        fim_str = data_final.strftime("%Y-%m-%d")

        for kw, tipo in terms:
            print(f"  Buscando: '{kw}' [{inicio_str} - {fim_str}]", end=" ", flush=True)
            hits = self._client.search_all_pages(
                texto=kw,
                tipo=tipo,
                data_inicial=inicio_str,
                data_final=fim_str,
            )
            novos = 0
            for hit in hits:
                key = (hit.nome_arquivo, hit.pagina)
                if key not in seen:
                    seen.add(key)
                    results.append(DOCollectedHit(hit=hit, keyword=kw))
                    novos += 1
            print(f"-> {len(hits)} resultados, {novos} novos")

        return results
