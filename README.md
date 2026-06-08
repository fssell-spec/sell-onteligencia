# SELL INTELIGÊNCIA

Sistema de Inteligência Comercial para Shows, Rodeios e Eventos Públicos.

Desenvolvido para a **Sell Produtora**, com foco inicial nas **79 prefeituras do Mato Grosso do Sul**.

---

## O que é este sistema?

A Sell Produtora vende shows de artistas, rodeios completos e estruturas físicas para prefeituras. Este sistema identifica oportunidades comerciais cruzando dados públicos de contratos, eventos, orçamentos municipais e artistas compatíveis.

**Status atual:** Etapa 1 — Setup inicial. Nenhum dado real coletado ainda.

---

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Git

---

## Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd sell-inteligencia
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` se necessário (a senha padrão funciona para desenvolvimento local).

---

## Banco de Dados

### 5. Subir o PostgreSQL via Docker Compose

```bash
docker compose up -d
```

Aguarde o banco iniciar (verificar com `docker compose ps`). O banco `sell_inteligencia` será criado automaticamente.

Para parar:

```bash
docker compose down
```

Para destruir os dados:

```bash
docker compose down -v
```

---

## Rodar a API

### 6. Iniciar o FastAPI

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

### 7. Testar o health check

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"status": "ok", "app": "SELL INTELIGÊNCIA"}
```

---

## Dashboard

### 8. Rodar o Streamlit

```bash
streamlit run dashboard/streamlit_app.py
```

O dashboard abrirá automaticamente em: `http://localhost:8501`

---

## Testes

### 9. Rodar os testes com pytest

```bash
pytest tests/ -v
```

---

## Estrutura do Projeto

```
sell-inteligencia/
├── app/            # FastAPI — API e configurações
├── crawlers/       # Coletores de dados públicos (a implementar)
├── etl/            # Extração, normalização e carga (a implementar)
├── agents/         # Agentes de análise (a implementar)
├── analytics/      # Scoring e simulações (a implementar)
├── dashboard/      # Interface Streamlit
├── data/           # Dados brutos, processados e exports
├── prompts/        # Prompts internos para extração com LLM
├── tests/          # Testes automatizados
└── docs/           # Documentação técnica
```

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| `docs/arquitetura.md` | Visão geral dos módulos do sistema |
| `docs/fontes_de_dados.md` | Fontes públicas planejadas |
| `docs/modelo_de_dados.md` | Entidades do banco de dados |
| `docs/compliance_scraping.md` | Boas práticas de coleta |
| `docs/roadmap.md` | Etapas de desenvolvimento |

---

## Próxima Etapa

**Etapa 2 — Modelo de Dados**

- Models SQLAlchemy para as entidades principais
- Migrations Alembic
- Seed com as 79 prefeituras do MS (dados IBGE)
