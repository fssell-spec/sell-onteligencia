# Projeto Sell Intelligence Platform

## Visão Geral

A Sell Intelligence Platform é uma plataforma de inteligência comercial voltada para a venda de shows, rodeios e eventos públicos para prefeituras.

O foco inicial é o estado de Mato Grosso do Sul (79 municípios).

O objetivo principal não é apenas identificar artistas em alta, mas prever oportunidades comerciais e auxiliar a equipe da Sell Produtora a vender:

- Shows
- Rodeios completos
- Estruturas para eventos
- Projetos completos de entretenimento para prefeituras

A plataforma deve transformar o processo comercial em uma operação orientada por dados.

---

# Objetivos do Negócio

A plataforma deve responder perguntas como:

- Quais prefeituras possuem eventos nos próximos meses?
- Quais ainda não anunciaram atrações?
- Qual o orçamento provável?
- Quem são os decisores?
- Quais artistas possuem maior aderência para aquele município?
- Quais eventos possuem maior potencial de fechamento?
- Qual proposta gera maior margem para a Sell?
- Qual modelo de rodeio faz mais sentido para cada cidade?

---

# Escopo Inicial

## Região

Estado do Mato Grosso do Sul.

79 municípios.

---

# Módulos do Sistema

## Módulo 1 - Inteligência de Prefeituras

Responsável por entender o comportamento de compra das prefeituras.

### Dados

- Prefeitura
- Prefeito
- Secretário de Cultura
- Secretário de Turismo
- Contatos
- Telefones
- E-mails
- Redes sociais
- Sites oficiais
- Portal da Transparência
- Diário Oficial

## Módulo 2 - Inteligência de Artistas

### Dados

- Nome
- Estilo
- Subestilo
- Escritório
- Contatos comerciais

### Dados de Mercado

- Popularidade Spotify
- Popularidade YouTube
- Google Trends
- Histórico de shows
- Histórico em eventos públicos

## Módulo 3 - Inteligência de Rodeios

### Estruturas

- Arena
- Arquibancada
- Camarotes
- Banheiros químicos
- Geradores
- Sonorização
- Iluminação
- Praça de alimentação
- Segurança
- Portaria

---

# Arquitetura Técnica

## Banco
PostgreSQL

## Linguagem
Python

## Automação
n8n

## Crawlers
Playwright

## Extração de PDFs
- pdfplumber
- pymupdf
- OCR

---

# Agentes

## Prefeitura Scanner
Monitora sites, portais e diários oficiais.

## Eventos Scanner
Detecta eventos futuros.

## Contratações Scanner
Monitora PNCP, transparência e diários oficiais.

## Artistas Scanner
Atualiza Spotify, YouTube e Trends.

## Fornecedores Scanner
Atualiza preços e disponibilidade.

## Opportunity Finder
Gera oportunidades comerciais.

---

# Filosofia do Projeto

O foco principal não é monitorar artistas.

O foco principal é prever compras de eventos públicos e ajudar a Sell Produtora a vender shows, rodeios e estruturas completas com maior previsibilidade e margem.
