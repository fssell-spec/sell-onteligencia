"""Simulador de orcamento para rodeios e eventos municipais no MS.

Compoe itens de custo com base no porte do evento:
  estrutura (arena + arquibancada + palco), som, luz, led,
  seguranca, brigadista, banheiros, gerador, portaria, producao.

Uso:
  from analytics.simulador_rodeio import SimuladorRodeio
  sim = SimuladorRodeio(event_size="medio", dias=2, publico=4000)
  orcamento = sim.calcular()
"""
from dataclasses import dataclass, field
from typing import Literal


EventSize = Literal["pequeno", "medio", "grande", "mega"]


# Multipliers por porte — aplicados sobre precos base
_SIZE_FACTOR = {
    "pequeno": 1.0,
    "medio":   2.2,
    "grande":  5.0,
    "mega":   12.0,
}

# Precos base (1 dia, porte pequeno ~1500 pessoas)
_BASE_PRICES: dict[str, dict] = {
    "arena": {
        "descricao": "Arena desmontavel + currais",
        "min": 8_000, "avg": 15_000, "max": 28_000,
    },
    "arquibancada": {
        "descricao": "Arquibancada metalica + palco",
        "min": 5_000, "avg":  9_000, "max": 16_000,
    },
    "som": {
        "descricao": "PA line array + monitor + backline",
        "min": 4_000, "avg":  8_000, "max": 15_000,
    },
    "luz": {
        "descricao": "Iluminacao conica + moving heads",
        "min": 3_000, "avg":  6_000, "max": 12_000,
    },
    "led": {
        "descricao": "Painel LED backdrop + telas laterais",
        "min": 4_000, "avg":  8_000, "max": 15_000,
    },
    "seguranca": {
        "descricao": "Seguranca patrimonial + controle de acesso",
        "min": 1_500, "avg":  3_000, "max":  5_500,
    },
    "brigadista": {
        "descricao": "Brigada de incendio certificada",
        "min": 1_200, "avg":  2_200, "max":  4_000,
    },
    "banheiro_quimico": {
        "descricao": "Kit banheiros quimicos + PCD",
        "min": 1_500, "avg":  2_800, "max":  5_000,
    },
    "gerador": {
        "descricao": "Gerador diesel redundante",
        "min": 3_500, "avg":  6_500, "max": 11_000,
    },
    "portaria": {
        "descricao": "Portaria + catracas + credenciamento",
        "min": 2_000, "avg":  4_000, "max":  7_000,
    },
    "producao": {
        "descricao": "Producao executiva + rider tecnico",
        "min": 5_000, "avg": 10_000, "max": 20_000,
    },
}

# Itens obrigatorios por porte
_REQUIRED_ITEMS: dict[str, list[str]] = {
    "pequeno": ["som", "luz", "seguranca", "brigadista", "banheiro_quimico",
                "portaria", "producao"],
    "medio":   ["arena", "arquibancada", "som", "luz", "led", "seguranca",
                "brigadista", "banheiro_quimico", "gerador", "portaria", "producao"],
    "grande":  list(_BASE_PRICES.keys()),
    "mega":    list(_BASE_PRICES.keys()),
}


@dataclass
class ItemOrcamento:
    categoria: str
    descricao: str
    dias: int
    min_total: float
    avg_total: float
    max_total: float


@dataclass
class Orcamento:
    event_size: str
    dias: int
    publico_estimado: int
    margem_percentual: float = 0.0   # % de margem da Sell sobre o custo total
    cachê_artista: float = 0.0       # cachê do artista (nao entra no custo de estrutura)
    itens: list[ItemOrcamento] = field(default_factory=list)

    @property
    def total_min(self) -> float:
        return sum(i.min_total for i in self.itens)

    @property
    def total_avg(self) -> float:
        return sum(i.avg_total for i in self.itens)

    @property
    def total_max(self) -> float:
        return sum(i.max_total for i in self.itens)

    @property
    def margem_valor_avg(self) -> float:
        """Valor da margem da Sell sobre o custo médio de estrutura."""
        return self.total_avg * (self.margem_percentual / 100)

    @property
    def proposta_avg(self) -> float:
        """Valor total a cobrar da prefeitura (estrutura + margem + cachê)."""
        return self.total_avg + self.margem_valor_avg + self.cachê_artista

    @property
    def proposta_min(self) -> float:
        margem = self.total_min * (self.margem_percentual / 100)
        return self.total_min + margem + self.cachê_artista

    @property
    def proposta_max(self) -> float:
        margem = self.total_max * (self.margem_percentual / 100)
        return self.total_max + margem + self.cachê_artista

    def resumo(self) -> dict:
        return {
            "event_size": self.event_size,
            "dias": self.dias,
            "publico_estimado": self.publico_estimado,
            "margem_percentual": self.margem_percentual,
            "cache_artista": round(self.cachê_artista, 2),
            "total_min": round(self.total_min, 2),
            "total_avg": round(self.total_avg, 2),
            "total_max": round(self.total_max, 2),
            "margem_valor_avg": round(self.margem_valor_avg, 2),
            "proposta_min": round(self.proposta_min, 2),
            "proposta_avg": round(self.proposta_avg, 2),
            "proposta_max": round(self.proposta_max, 2),
            "itens": [
                {
                    "categoria": i.categoria,
                    "descricao": i.descricao,
                    "dias": i.dias,
                    "min": round(i.min_total, 2),
                    "avg": round(i.avg_total, 2),
                    "max": round(i.max_total, 2),
                }
                for i in self.itens
            ],
        }


class SimuladorRodeio:
    def __init__(
        self,
        event_size: EventSize,
        dias: int = 1,
        publico: int = 1500,
        margem_percentual: float = 20.0,
        cache_artista: float = 0.0,
    ):
        if event_size not in _SIZE_FACTOR:
            raise ValueError(f"event_size invalido: {event_size}")
        if dias < 1:
            raise ValueError("dias deve ser >= 1")
        if not (0 <= margem_percentual <= 100):
            raise ValueError("margem_percentual deve estar entre 0 e 100")
        self.event_size = event_size
        self.dias = dias
        self.publico = publico
        self.margem_percentual = margem_percentual
        self.cache_artista = cache_artista
        self._fator = _SIZE_FACTOR[event_size]

    def calcular(self, itens_extras: list[str] | None = None) -> Orcamento:
        itens_necessarios = list(_REQUIRED_ITEMS[self.event_size])
        if itens_extras:
            for extra in itens_extras:
                if extra in _BASE_PRICES and extra not in itens_necessarios:
                    itens_necessarios.append(extra)

        orcamento = Orcamento(
            event_size=self.event_size,
            dias=self.dias,
            publico_estimado=self.publico,
            margem_percentual=self.margem_percentual,
            cachê_artista=self.cache_artista,
        )

        for cat in itens_necessarios:
            base = _BASE_PRICES[cat]
            # Som, luz, producao nao escalam linearmente com dias (setup fixo)
            multiplicador_dias = self.dias if cat in ("seguranca", "brigadista", "banheiro_quimico") else 1

            item = ItemOrcamento(
                categoria=cat,
                descricao=base["descricao"],
                dias=multiplicador_dias,
                min_total=base["min"] * self._fator * multiplicador_dias,
                avg_total=base["avg"] * self._fator * multiplicador_dias,
                max_total=base["max"] * self._fator * multiplicador_dias,
            )
            orcamento.itens.append(item)

        return orcamento

    @staticmethod
    def portes_disponiveis() -> dict[str, dict]:
        return {
            "pequeno": {"publico": "ate 2.000", "dias": "1 dia",   "descricao": "Show simples, festa de bairro"},
            "medio":   {"publico": "2.000-8.000",  "dias": "2-3 dias", "descricao": "Festa do peao, aniversario de cidade"},
            "grande":  {"publico": "8.000-20.000", "dias": "3-5 dias", "descricao": "Rodeio regional, expofeira"},
            "mega":    {"publico": "20.000+",       "dias": "4-7 dias", "descricao": "Expoagro estadual, rodeio nacional"},
        }
