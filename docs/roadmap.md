# Roadmap — SELL INTELIGÊNCIA

## Etapa 1 — Setup Inicial ✅
Estrutura de pastas, Docker Compose (PostgreSQL), FastAPI com health check, Streamlit inicial, documentação base e prompts internos.

---

## Etapa 2 — Modelo de Dados ✅
- Models SQLAlchemy: `prefeituras`, `contratos`, `eventos`, `artistas`, `fornecedores`, `oportunidades`, `coletas`
- Migrations Alembic
- Configuração do Alembic (`alembic.ini`, `env.py`)

---

## Etapa 3 — Seed das 79 Prefeituras do MS ✅
- Script de seed com dados públicos do IBGE (`scripts/seed_municipios.py`)
- Campos: nome, código IBGE, população, área km², mesorregião, microrregião
- 79 municípios do MS inseridos — 6 mesorregiões, população total ~2,7M hab
- Migration `b3c291f0` adicionou `ibge_code`, `area_km2`, `mesorregiao`, `microrregiao`

---

## Etapa 4 — Dashboard Inicial com Dados Reais ✅
- Streamlit conectado ao PostgreSQL com `st.cache_data`
- Mapa interativo do MS (scatter_mapbox open-street-map, bolhas proporcionais à população)
- KPIs em tempo real: municípios, população total, mesorregiões, maior município, área total
- Filtros sidebar: mesorregião (multiselect), porte, slider de população
- Aba Distribuição: gráficos população/contagem por mesorregião + top 15 por população
- Aba Municípios: tabela navegável com busca por nome + exportação CSV

---

## Etapa 5 — Coleta de Dados Públicos ✅
- Crawler PNCP: `crawlers/pncp/client.py`, `collector.py`, `keywords.py`
  - 4 modalidades: Pregão Eletrônico (6), Pregão Presencial (7), Dispensa (8), Inexigibilidade (9)
  - Paginação automática, rate limiting (1.2s), retry com backoff exponencial
  - Filtro por palavras-chave (som, luz, palco, show, rodeio, gerador, segurança, etc.)
  - Classificação automática por tipo (ContractType enum)
- ETL: `etl/loaders/contract_loader.py` — deduplicação por (process_number, source_name)
- Script: `scripts/run_pncp_crawler.py` — argparse, registro de runs, resumo por tipo
- Dados coletados: ~77 contratos (2023-2024), 79 municípios do MS
  - Distribuição: som_luz 18 · estrutura_evento 20 · gerador 5 · seguranca 3 · show_artistico 2 · producao 2 · rodeio_completo 1 · outro 8

---

## Etapa 6 — Extração de Contratos e PDFs ✅
- Busca de itens detalhados via PNCP `api/pncp/v1` (`crawlers/pncp/items_fetcher.py`)
- Extração LLM com Groq (Llama 3.3 70B): event_name, event_date, artist_name, services, notes
- 76 contratos enriquecidos — 30 eventos identificados, 10 datas preenchidas
- Script: `scripts/run_contract_extractor.py` (suporta --limit, --tipo, --reprocessar, --sem-itens)
- Resultados em `extracted_json["llm_extracted"]` + campos `event_date` e `confidence_score`

---

## Etapa 7 — Base de Artistas
- Catálogo inicial de artistas sertanejos e regionais
- Classificação por gênero, popularidade e faixa de cachê
- Cruzamento com histórico de contratos públicos

---

## Etapa 8 — Base de Rodeios e Fornecedores
- Cadastro de fornecedores de estrutura (arena, som, luz, etc.)
- Simulador de orçamento de rodeio completo
- Templates de proposta por porte de evento

---

## Etapa 9 — Motor de Oportunidades
- Scoring de prefeituras
- Scoring de artistas por compatibilidade municipal
- Ranking de oportunidades comerciais
- Alertas de contratos abertos e sazonalidade

---

## Etapa 10 — Relatórios Comerciais
- Relatório de oportunidades em PDF
- Exportação para Excel
- Dashboard executivo com KPIs da Sell
- Integração com CRM (a definir)
