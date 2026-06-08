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
