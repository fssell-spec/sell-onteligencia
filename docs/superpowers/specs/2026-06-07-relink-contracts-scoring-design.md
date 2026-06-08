# Design: Relinking de Contratos + Revisão do Scoring

**Data:** 2026-06-07  
**Status:** Aprovado  
**Contexto:** Sistema SELL Inteligência — motor de oportunidades comerciais para 79 municípios do MS

---

## Problema

Dois bugs críticos tornam o scoring inutilizável:

1. **466 de 502 contratos (93%) sem `municipality_id`** — o `contract_loader` só conseguiu linkar 36 contratos ao criar, deixando quase todo o histórico invisível para o motor de scoring.

2. **Campo Grande inflado por contratos estaduais** — os 8 contratos linkados a Campo Grande pertencem à Fundação de Cultura de Mato Grosso do Sul (CNPJ 15579196000198), órgão estadual sediado na capital. Os shows eram em outros municípios mas estavam sendo contabilizados para Campo Grande.

**Impacto:** todos os 79 municípios aparecem com score 28–37, sem discriminação útil. A dimensão de histórico (peso ~31) retorna zero para quase todos, fazendo o score refletir apenas aniversário + população + prefeito mapeado.

---

## Escopo

Duas entregas encadeadas:

1. `scripts/relink_contracts.py` — re-processa contratos sem município
2. Revisão dos pesos em `analytics/opportunity_engine.py` — urgência temporal como fator dominante

Sem migrations. Sem alteração de schema. Idempotente.

---

## Entrega 1 — `scripts/relink_contracts.py`

### Algoritmo: 3 passes sequenciais

```
DB: contratos com municipality_id = NULL
        │
        ▼ Pass 1 — raw_json ibge_code (sem LLM)
        │  lê raw_json['unidadeOrgao']['codigoIbge']
        │  se ibge_code ∈ ibge_map → atualiza municipality_id
        │  estimativa: resolve ~200–250 contratos
        │
        ▼ Pass 2 — regex no objeto_descricao (sem LLM)
        │  padrões: "município de X", "cidade de X", "X/MS", "X-MS"
        │  normaliza nome (remove acentos, lowercase) → busca em name_map
        │  estimativa: resolve ~100–150 contratos
        │
        ▼ Pass 3 — Groq batch (llama-3.1-8b-instant)
        │  prompt: "Qual município do MS este show/evento vai acontecer? Responda só o nome do município."
        │  batch de 10 requisições, delay 1s entre batches
        │  resposta normalizada → busca em name_map
        │  estimativa: resolve ~50–80 contratos
        │
        ▼ Contratos sem link após 3 passes
           supplier = Fundação de Cultura MS → extracted_json['source_type'] = 'estadual'
           demais → municipality_id permanece NULL
```

### Interface de linha de comando

```bash
python scripts/relink_contracts.py            # execução completa
python scripts/relink_contracts.py --dry-run  # simula sem gravar
python scripts/relink_contracts.py --pass 1   # roda só o pass especificado
```

### Tratamento de erros

- **Groq 429:** retry com backoff 5s, até 3 tentativas; se persistir, contrato fica sem link e script continua
- **Nome ambíguo do LLM:** só aceita match exato após normalização — sem match parcial para evitar falsos positivos
- **Idempotência:** filtra por `municipality_id IS NULL`; pode ser re-executado sem efeito colateral

### Log esperado

```
Pass 1 (raw_json ibge): 234 resolvidos
Pass 2 (regex texto):   118 resolvidos  
Pass 3 (Groq LLM):       62 resolvidos
Estadual (sem link):      8 marcados
Sem link restantes:      44
Total linkados: 414 / 466
```

---

## Entrega 2 — Revisão dos pesos do scoring

### Motivação

Com o linking corrigido, o histórico de contratos passa a ter dados reais. A urgência temporal (janela de evento próximo) deve ser dominante para que o ranking reflita quem contratar *agora*.

### Novos pesos (soma = 100)

| Dimensão | Peso atual | Peso novo | Razão |
|----------|-----------|-----------|-------|
| Janela temporal (evento < 60 dias) | 10 | **30** | Urgência é o critério primário de priorização comercial |
| Histórico valor gasto | 18 | 20 | Indica capacidade de pagamento real |
| Histórico qtd contratos | 13 | 15 | Indica frequência de compra |
| Recorrência de eventos | 18 | 15 | Útil mas secundário à urgência |
| Contatos mapeados | 13 | 8 | Dado incompleto (0 secretários); peso reduzido |
| Aniversário do município | 10 | 5 | Sinal fraco |
| Credenciamento ativo | 10 | 5 | Poucos editais ativos atualmente |
| População | 8 | 2 | Correlação fraca com oportunidade real |

### Exclusão de contratos estaduais do scoring

Contratos com `extracted_json.source_type = 'estadual'` são ignorados ao calcular `score_historico_contratos` e `score_historico_valor`.

---

## Fluxo de execução pós-implementação

```bash
# 1. Re-linkar contratos (único run necessário)
python scripts/relink_contracts.py

# 2. Recalcular scores com novos dados
python scripts/run_opportunity_engine.py
```

Tempo estimado: ~20 minutos (dominado pelo batch Groq no Pass 3).

---

## Impacto esperado no dashboard

| Aba | Antes | Depois |
|-----|-------|--------|
| Oportunidades — scores | 78 municípios com 28–37 | Distribuição real; top municípios com 60–85 |
| Oportunidades — ranking | Campo Grande no topo (inflado) | Municípios com histórico real e janela aberta no topo |
| Contratos — tabela | 36 com município vinculado | ~400+ com município |
| Radar de Oportunidades | Orçamento histórico impreciso | Baseado no histórico completo |

---

## O que não está no escopo

- Nova migration ou alteração de schema
- Recoleta de contratos do PNCP
- Correção do scanner de secretários (problema separado)
- Pipeline CRM (próxima iniciativa)
