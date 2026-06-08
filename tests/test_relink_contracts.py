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
