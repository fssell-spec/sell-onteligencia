# Arquitetura — SELL INTELIGÊNCIA

## Visão Geral

O sistema é composto por quatro módulos principais que trabalham em conjunto para identificar e priorizar oportunidades comerciais para a Sell Produtora.

---

## Módulo 1 — Inteligência de Prefeituras

Mapeia as 79 prefeituras do Mato Grosso do Sul com dados públicos:

- Cadastro básico (IBGE, população, área, IDH)
- Estimativa de orçamento municipal (LOA, execução orçamentária)
- Histórico de contratos de shows, rodeios e estruturas (PNCP, portais de transparência)
- Perfil de eventos realizados (diários oficiais, notícias)
- Perfil digital (redes sociais das prefeituras)

**Saída:** Score de oportunidade por município.

---

## Módulo 2 — Inteligência de Artistas

Cataloga artistas compatíveis com o perfil dos municípios do interior do MS:

- Gênero musical e popularidade regional
- Faixa de cachê estimado
- Disponibilidade e agenda
- Histórico de contratações públicas no estado

**Saída:** Ranking de artistas por compatibilidade com cada município.

---

## Módulo 3 — Inteligência de Rodeios e Estruturas

Base de dados de fornecedores e simulador de orçamento:

- Fornecedores de arena, arquibancada, banheiros, som, luz, gerador
- Simulador de composição de rodeio completo
- Estimativa de custos por porte de evento
- Cruzamento com capacidade orçamentária municipal

**Saída:** Simulação de proposta de rodeio completo por município.

---

## Módulo 4 — Motor de Oportunidades

Consolida os três módulos anteriores e gera inteligência comercial acionável:

- Ranking de oportunidades por prioridade
- Tipo de proposta recomendada (show, rodeio, estrutura, pacote completo)
- Timing ideal de abordagem (sazonalidade, calendário festivo)
- Alertas de contratos abertos ou vencendo
- Histórico de relacionamento da Sell com cada município

**Saída:** Painel de oportunidades e relatórios para a equipe comercial.

---

## Status do Banco de Dados

A Etapa 2 implementou o esquema relacional completo com 12 tabelas:

| Tabela | Módulo |
|--------|--------|
| `municipalities` | Prefeituras |
| `public_contacts` | Prefeituras |
| `municipal_events` | Prefeituras |
| `public_contracts` | Prefeituras + Artistas |
| `artists` | Artistas |
| `artist_fees` | Artistas |
| `artist_regional_strength` | Artistas |
| `suppliers` | Rodeios e Estruturas |
| `supplier_prices` | Rodeios e Estruturas |
| `rodeo_budget_templates` | Rodeios e Estruturas |
| `commercial_opportunities` | Motor de Oportunidades |
| `crawler_runs` | Infraestrutura (log de coleta) |

Migration: `6a150368_create_initial_schema` — aplicar com `alembic upgrade head`.

---

## Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI + Uvicorn |
| Banco | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x + Alembic |
| Dashboard | Streamlit |
| Scraping | Playwright + BeautifulSoup4 |
| PDF | pdfplumber + PyMuPDF |
| Infraestrutura | Docker Compose |
| Testes | pytest |
