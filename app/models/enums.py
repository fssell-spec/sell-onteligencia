import enum


class EventType(str, enum.Enum):
    aniversario_cidade = "aniversario_cidade"
    expoagro = "expoagro"
    festa_peao = "festa_peao"
    rodeio = "rodeio"
    carnaval = "carnaval"
    reveillon = "reveillon"
    festival_cultural = "festival_cultural"
    festa_tradicional = "festa_tradicional"
    outro = "outro"


class ContractType(str, enum.Enum):
    show_artistico = "show_artistico"
    rodeio_completo = "rodeio_completo"
    estrutura_evento = "estrutura_evento"
    som_luz = "som_luz"
    seguranca = "seguranca"
    banheiro_quimico = "banheiro_quimico"
    arquibancada = "arquibancada"
    arena = "arena"
    gerador = "gerador"
    portaria = "portaria"
    alimentacao = "alimentacao"
    limpeza = "limpeza"
    producao = "producao"
    outro = "outro"


class ProcurementModality(str, enum.Enum):
    inexigibilidade = "inexigibilidade"
    dispensa = "dispensa"
    pregao = "pregao"
    concorrencia = "concorrencia"
    credenciamento = "credenciamento"
    outro = "outro"
    desconhecido = "desconhecido"


class SupplierCategory(str, enum.Enum):
    arena = "arena"
    arquibancada = "arquibancada"
    banheiro_quimico = "banheiro_quimico"
    seguranca = "seguranca"
    brigadista = "brigadista"
    som = "som"
    luz = "luz"
    led = "led"
    gerador = "gerador"
    portaria = "portaria"
    alimentacao = "alimentacao"
    limpeza = "limpeza"
    producao = "producao"
    outro = "outro"


class OpportunityType(str, enum.Enum):
    venda_show = "venda_show"
    venda_rodeio = "venda_rodeio"
    evento_completo = "evento_completo"
    estrutura_evento = "estrutura_evento"


class OpportunityStatus(str, enum.Enum):
    novo = "novo"
    pesquisar = "pesquisar"
    abordar = "abordar"
    em_contato = "em_contato"
    proposta_enviada = "proposta_enviada"
    negociacao = "negociacao"
    ganho = "ganho"
    perdido = "perdido"
    suspenso = "suspenso"


class CrawlerStatus(str, enum.Enum):
    running = "running"
    success = "success"
    failed = "failed"
    partial = "partial"
