# Modelo de Dados — SELL INTELIGÊNCIA

Modelo implementado na Etapa 2. Banco: `sell_inteligencia` (PostgreSQL 16).

---

## Tabelas

### `municipalities`
Cadastro das 79 prefeituras do Mato Grosso do Sul. Entidade central do sistema — todas as oportunidades, eventos e contratos partem daqui.

**Campos-chave:** `name`, `normalized_name`, `state`, `population`, `region`, URLs institucionais.
**Constraint:** `UNIQUE(normalized_name, state)` — evita duplicatas por estado.

---

### `public_contacts`
Contatos públicos identificados nas prefeituras: prefeito, secretário de cultura, assessores. Coletados de sites oficiais e diários.

**Campos-chave:** `role`, `department`, `email`, `phone`, `whatsapp`, `confidence_score`.
**FK:** `municipality_id → municipalities`.

---

### `municipal_events`
Eventos municipais recorrentes ou identificados: festas do peão, aniversários de cidade, rodeios, carnavais.

**Campos-chave:** `name`, `event_type` (enum), `usual_month`, `estimated_start_date`, `confidence_score`.
**FK:** `municipality_id → municipalities`.

---

### `public_contracts`
Contratos públicos coletados de PNCP, portais de transparência e diários oficiais. Coração da inteligência comercial.

**Campos-chave:** `contract_type` (enum), `contract_value`, `supplier_name`, `supplier_document`, `process_number`, `procurement_modality` (enum), `extracted_json` (JSONB), `confidence_score`.
**FK:** `municipality_id`, `event_id`, `artist_id`.
**Nota:** `raw_text` preserva o texto original; `extracted_json` é o dado estruturado extraído por LLM.

---

### `artists`
Catálogo de artistas. Identificados via contratos públicos e bases externas (Spotify, YouTube).

**Campos-chave:** `name`, `normalized_name` (UNIQUE), `main_style`, `sub_style`, `booking_office`.

---

### `artist_fees`
Histórico de cachês identificados por artista, com rastreabilidade de fonte e confiança.

**Campos-chave:** `value`, `date`, `source_type`, `confidence_score`.
**FK:** `artist_id`, `municipality_id`, `contract_id`.

---

### `artist_regional_strength`
Scores de popularidade do artista por estado/cidade, calculados a partir de Spotify, YouTube, Google Trends e contratos históricos.

**Campos-chave:** `spotify_score`, `youtube_score`, `google_trends_score`, `public_contracts_score`, `final_score`.
**FK:** `artist_id`.

---

### `suppliers`
Fornecedores de estrutura para eventos: arena, som, luz, arquibancada, banheiros, segurança, etc.

**Campos-chave:** `name`, `category` (enum), `city`, `state`, `service_region`.

---

### `supplier_prices`
Tabela de preços por fornecedor, com faixas mínima/média/máxima para uso no simulador de rodeio.

**Campos-chave:** `unit_type`, `min_price`, `avg_price`, `max_price`, `confidence_score`.
**FK:** `supplier_id → suppliers`.

---

### `rodeo_budget_templates`
Templates de orçamento de rodeio completo por porte (pequeno/médio/grande). Base para o simulador.

**Campos-chave:** `event_size`, `expected_audience`, `duration_days`, `required_items_json` (JSONB).

---

### `commercial_opportunities`
Oportunidades comerciais geradas pelo motor de inteligência. Cada linha representa uma oportunidade de venda identificada para uma prefeitura.

**Campos-chave:** `opportunity_type` (enum), `status` (enum), `final_opportunity_score`, `estimated_budget`, `recommended_artists_json` (JSONB), `suggested_next_action`, `next_action_at`.
**FK:** `municipality_id`, `event_id`.

---

### `crawler_runs`
Log de execução de cada crawler: rastreabilidade completa de quando coletou, quantos registros processou e se houve erros.

**Campos-chave:** `crawler_name`, `status` (enum), `records_found`, `records_created`, `records_updated`, `error_message`, `metadata_json` (JSONB).

---

## Relacionamentos principais

```
Municipality ──< PublicContact
Municipality ──< MunicipalEvent ──< PublicContract
Municipality ──< PublicContract
Municipality ──< CommercialOpportunity
Artist ──< PublicContract
Artist ──< ArtistFee
Artist ──< ArtistRegionalStrength
Supplier ──< SupplierPrice
```

---

## Enums

| Enum | Tabela | Valores |
|------|--------|---------|
| `EventType` | municipal_events | aniversario_cidade, expoagro, festa_peao, rodeio, carnaval, reveillon, festival_cultural, festa_tradicional, outro |
| `ContractType` | public_contracts | show_artistico, rodeio_completo, estrutura_evento, som_luz, seguranca, banheiro_quimico, arquibancada, arena, gerador, portaria, alimentacao, limpeza, producao, outro |
| `ProcurementModality` | public_contracts | inexigibilidade, dispensa, pregao, concorrencia, credenciamento, outro, desconhecido |
| `SupplierCategory` | suppliers | arena, arquibancada, banheiro_quimico, seguranca, brigadista, som, luz, led, gerador, portaria, alimentacao, limpeza, producao, outro |
| `OpportunityType` | commercial_opportunities | venda_show, venda_rodeio, evento_completo, estrutura_evento |
| `OpportunityStatus` | commercial_opportunities | novo, pesquisar, abordar, em_contato, proposta_enviada, negociacao, ganho, perdido, suspenso |
| `CrawlerStatus` | crawler_runs | running, success, failed, partial |

---

## Princípio de rastreabilidade

Todo dado coletado de fonte externa deve ter:
- `source_url` — URL de origem
- `confidence_score` — grau de confiança (0.0 a 1.0)
- `created_at` — quando foi inserido

Dados críticos (contratos, cachês) preservam também `raw_text` e `extracted_json` para auditoria.
