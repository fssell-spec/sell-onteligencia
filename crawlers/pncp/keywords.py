"""Classificação de contratos PNCP por palavras-chave."""
import re

from app.models.enums import ContractType

# Termos por tipo — verificados em lowercase sem acentos
_SHOW = [
    "show artis", "show musical", "apresentacao artis", "apresentacao musical",
    "contratacao artis", "contratacao de artis", "cachê", "cache artis",
    "show de forró", "show de forro", "show sertanejo", "show gospel",
    "espetaculo musical", "espetaculo artis", "atracao musical",
    "atracoes musicais", "evento artistico", "show band",
    "dupla sertaneja", "cantor", "cantora", "banda musical",
    "pagode", "show de pagode", "grupo de pagode",
    "samba", "show de samba", "escola de samba",
    "forro", "forró", "show de forro", "show de forró",
    "axe", "axé", "show de axe", "show de axé",
]
_RODEIO = [
    "rodeio", "festa do peao", "festa do piao", "cavalgada",
    "vaquejada", "prova de laço", "prova de laco", "montaria",
    "tourada", "corrida de cavalos",
]
_ESTRUTURA = [
    "estrutura para evento", "estrutura de evento", "palco", "tenda",
    "arquibancada", "gradil", "grades de segurança", "grades de seguranca",
    "container", "banheiro quimico", "sanitario quimico",
    "tablado", "piso elevado",
]
_SOM_LUZ = [
    "sonorizacao", "sonorização", "sistema de som", "equipamento de som",
    "iluminacao de palco", "iluminação de palco", "sistema de iluminacao",
    "led screen", "painel de led", "projetor",
]
_SEGURANCA = [
    "seguranca para evento", "segurança para evento",
    "seguranca privada", "agente de segurança", "agente de seguranca",
    "brigadista", "policiamento evento",
]
_GERADORES = [
    "locacao de gerador", "locação de gerador", "aluguel de gerador",
    "gerador de energia", "grupo gerador",
]
_PRODUCAO = [
    "producao de evento", "produção de evento",
    "organizacao de evento", "organização de evento",
    "assessoria de evento", "empresa de eventos",
]

# Mapeamento tipo → lista de termos
_TIPO_TERMOS: list[tuple[ContractType, list[str]]] = [
    (ContractType.show_artistico,   _SHOW),
    (ContractType.rodeio_completo,  _RODEIO),
    (ContractType.estrutura_evento, _ESTRUTURA),
    (ContractType.som_luz,          _SOM_LUZ),
    (ContractType.seguranca,        _SEGURANCA),
    (ContractType.gerador,          _GERADORES),
    (ContractType.producao,         _PRODUCAO),
]

# Termos que indicam "é sobre eventos públicos" mas não se enquadram acima
_EVENTO_GERAL = [
    "festa municipal", "aniversario da cidade", "aniversário da cidade",
    "festa de aniversario", "exposicao agropecuaria", "exposição agropecuária",
    "parque de vaquejada", "arena de rodeio", "arraial", "festa junina",
    "carnaval", "reveillon", "virada do ano", "folia de reis",
]


def _normalize(text: str) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return nfkd.encode("ascii", "ignore").decode("ascii")


def classify(objeto: str) -> ContractType:
    """Retorna o ContractType mais provável para o objeto do contrato."""
    norm = _normalize(objeto)
    for contract_type, termos in _TIPO_TERMOS:
        for t in termos:
            if re.search(re.escape(_normalize(t)), norm):
                return contract_type
    return ContractType.outro


def is_relevant(objeto: str) -> bool:
    """True se o contrato é relacionado a shows, rodeios ou eventos públicos."""
    norm = _normalize(objeto)
    all_terms = (
        _SHOW + _RODEIO + _ESTRUTURA + _SOM_LUZ
        + _SEGURANCA + _GERADORES + _PRODUCAO + _EVENTO_GERAL
    )
    return any(re.search(re.escape(_normalize(t)), norm) for t in all_terms)
