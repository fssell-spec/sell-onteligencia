# Compliance e Boas Práticas de Scraping — SELL INTELIGÊNCIA

Este documento define as diretrizes obrigatórias para coleta de dados no sistema.

---

## Princípios Fundamentais

### 1. Apenas Fontes Públicas
Coletar somente dados disponíveis publicamente, sem necessidade de autenticação ou cadastro. Nunca acessar áreas protegidas por login.

### 2. Respeitar robots.txt
Antes de iniciar qualquer crawler, verificar e respeitar o arquivo `robots.txt` do domínio alvo. Registrar no log de coleta se o acesso foi permitido ou restringido.

### 3. Não Burlar Sistemas de Login
Proibido contornar autenticações, CAPTCHAs ou qualquer mecanismo de controle de acesso. Se uma fonte exige login, utilizá-la apenas via API oficial ou descartá-la.

### 4. Não Coletar Dados Privados
Proibido coletar CPF, dados pessoais de pessoas físicas, dados bancários ou qualquer informação classificada como sensível pela LGPD. O foco é exclusivamente em dados de entes públicos (prefeituras, contratos, licitações).

### 5. Registrar a Fonte de Cada Dado
Todo dado inserido no banco deve ter o campo `fonte` preenchido com a URL ou identificador da origem. Manter rastreabilidade completa para auditoria.

### 6. Usar Delays Entre Requisições
Configurar intervalos mínimos entre requisições para não sobrecarregar servidores públicos:
- Mínimo 1 segundo entre requisições ao mesmo domínio
- Mínimo 3 segundos para portais de prefeituras pequenas
- User-agent identificável (não ocultar a origem do crawler)

### 7. Manter Rastreabilidade
Registrar em log: URL acessada, data/hora, status HTTP, volume de dados coletados e versão do crawler. Armazenar os dados brutos em `data/raw/` antes de processar.

### 8. Revisão Humana para Dados Críticos
Dados utilizados em propostas comerciais devem passar por revisão humana antes de serem apresentados ao cliente. O sistema é de apoio à decisão, não de automação de propostas sem validação.

---

## Checklist por Crawler

Antes de ativar qualquer crawler em produção:

- [ ] Verificar robots.txt do domínio
- [ ] Confirmar que a fonte é pública e não requer login
- [ ] Configurar delay mínimo entre requisições
- [ ] Implementar campo `fonte` e `coletado_em` nos dados
- [ ] Salvar dados brutos em `data/raw/` com timestamp
- [ ] Documentar a fonte em `docs/fontes_de_dados.md`
- [ ] Testar com volume pequeno antes de coleta em escala

---

## Referências Legais

- Lei Geral de Proteção de Dados (LGPD) — Lei nº 13.709/2018
- Lei de Acesso à Informação (LAI) — Lei nº 12.527/2011
- Decreto nº 10.046/2019 — Governo Digital e dados abertos
