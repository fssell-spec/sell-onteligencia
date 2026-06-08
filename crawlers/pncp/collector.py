"""Orquestra a coleta do PNCP para os municípios do MS."""
from dataclasses import dataclass
from datetime import date, timedelta

from crawlers.pncp.client import MODALIDADES, PNCPClient, PNCPItem
from crawlers.pncp.keywords import classify, is_relevant


@dataclass
class CollectedContract:
    item: PNCPItem
    contract_type_value: str   # valor do enum ContractType


def _quarters(data_inicial: date, data_final: date) -> list[tuple[date, date]]:
    """Divide o período em janelas trimestrais."""
    windows = []
    start = data_inicial
    while start <= data_final:
        end_month = start.month + 2
        end_year = start.year + (end_month - 1) // 12
        end_month = ((end_month - 1) % 12) + 1
        last_day = (date(end_year, end_month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        end = min(last_day, data_final)
        windows.append((start, end))
        start = end + timedelta(days=1)
    return windows


class PNCPCollector:
    def __init__(self, ibge_codes: list[str]) -> None:
        self._client = PNCPClient()
        self._ibge_set = set(ibge_codes)

    def collect(
        self,
        data_inicial: date,
        data_final: date,
        modalidades: list[int] | None = None,
        verbose: bool = True,
    ) -> list[CollectedContract]:
        if modalidades is None:
            modalidades = list(MODALIDADES.keys())

        results: list[CollectedContract] = []
        quarters = _quarters(data_inicial, data_final)

        for mod_id in modalidades:
            mod_nome = MODALIDADES.get(mod_id, str(mod_id))
            for q_start, q_end in quarters:
                if verbose:
                    print(f"  [{mod_nome}] {q_start} a {q_end} ...", end=" ", flush=True)
                items = self._client.fetch_contratacoes(
                    modalidade_id=mod_id,
                    data_inicial=q_start,
                    data_final=q_end,
                    uf="MS",
                )
                # Filtra para municípios do MS conhecidos e relevantes para eventos
                filtered = [
                    i for i in items
                    if i.ibge_code in self._ibge_set and is_relevant(i.objeto)
                ]
                if verbose:
                    print(f"{len(items)} brutos, {len(filtered)} relevantes")
                for item in filtered:
                    ct = classify(item.objeto)
                    results.append(CollectedContract(item=item, contract_type_value=ct.value))

        return results
