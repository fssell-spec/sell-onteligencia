"""Termos de busca para o Diário Oficial do MS (contratos de shows/artistas).

Estratégia:
- Termos específicos primeiro (menos ruído) → termos genéricos por último (LLM filtra)
- "inexigibilidade" captura contratações diretas antes de aparecerem no PNCP
- "forro" removido — gera falsos positivos com forro de roupa/sapato
"""
from crawlers.diarios_oficiais.client import TIPO_AO_MENOS_UMA, TIPO_EXATO

# (termo, tipo_busca)
BUSCAS: list[tuple[str, int]] = [
    # Contratações diretas de artistas (inexigibilidade)
    ("notoria especializacao", TIPO_EXATO),       # art. 74 I — artista exclusivo
    ("artista exclusivo", TIPO_EXATO),
    ("empresario exclusivo", TIPO_EXATO),
    ("cachê artístico", TIPO_EXATO),
    # Gêneros musicais específicos
    ("dupla sertaneja", TIPO_EXATO),
    ("cantor sertanejo", TIPO_EXATO),
    ("banda musical", TIPO_EXATO),
    ("artista musical", TIPO_EXATO),
    ("pagode", TIPO_EXATO),
    ("samba", TIPO_EXATO),
    # Genéricos — LLM filtra o ruído
    ("apresentacao artistica", TIPO_EXATO),
    ("show musical", TIPO_EXATO),
    ("show artístico", TIPO_EXATO),
]
