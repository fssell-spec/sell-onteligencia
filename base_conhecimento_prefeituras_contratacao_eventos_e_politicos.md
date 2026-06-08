# Base de Conhecimento — Vendas de Artistas, Produtoras e Eventos para Prefeituras

Arquivo criado para servir como contexto operacional em projeto no Claude Code.

Objetivo: consolidar conhecimento sobre:
1. onde encontrar dados oficiais de prefeitos, vice-prefeitos, vereadores, secretários e decisores municipais;
2. como funciona o fluxo de aprovação de orçamento e contratação de festas/eventos públicos;
3. quais são as melhores janelas comerciais para vender artistas, shows, produtoras e estruturas para prefeituras;
4. como diferenciar a venda política/estratégica da contratação formal;
5. quais cuidados legais e documentais reduzem risco e aumentam chance de fechamento.

---

## 1. Tese central

Vender artistas, shows, produção e eventos para prefeituras não é igual vender para empresa privada.

Na iniciativa privada, o decisor pode gostar, aprovar e contratar rapidamente.

Na prefeitura, o “sim” verbal do prefeito, secretário ou assessor não fecha negócio. O que fecha negócio é a existência de:

- interesse público justificado;
- dotação orçamentária;
- processo administrativo formal;
- documentação correta;
- parecer jurídico favorável;
- autorização do ordenador de despesa;
- empenho;
- contrato, ordem de serviço ou instrumento equivalente;
- publicação obrigatória, especialmente no PNCP quando aplicável;
- execução;
- liquidação;
- pagamento.

Regra prática:

> Sem empenho e instrumento formal, não execute evento.

---

## 2. Onde encontrar dados oficiais de políticos e decisores municipais

### 2.1. Prefeito e vice-prefeito

Fonte principal: TSE — Tribunal Superior Eleitoral.

O TSE é a melhor fonte oficial nacional para identificar prefeitos e vice-prefeitos eleitos.

Fontes úteis:

- Portal de Dados Abertos do TSE;
- base de Resultados Eleitorais 2024;
- base de Candidatos 2024;
- DivulgaCandContas.

Informações que podem ser obtidas:

- município;
- UF;
- cargo;
- nome do candidato;
- nome de urna;
- partido;
- situação eleitoral;
- resultado;
- coligação/federação, quando aplicável;
- dados cadastrais eleitorais disponíveis;
- vice vinculado à chapa, conforme estrutura da base.

Estratégia recomendada:

1. Baixar base de municípios do IBGE.
2. Baixar base de resultados do TSE.
3. Filtrar eleição municipal mais recente.
4. Filtrar cargos de prefeito e vice-prefeito.
5. Cruzar pelo código do município, UF e nome do município.
6. Gerar uma base única por município.

Campos sugeridos:

| Campo | Fonte sugerida |
|---|---|
| codigo_ibge | IBGE |
| municipio | IBGE/TSE |
| uf | IBGE/TSE |
| prefeito_nome | TSE |
| prefeito_nome_urna | TSE |
| prefeito_partido | TSE |
| prefeito_status | TSE |
| vice_nome | TSE |
| vice_partido | TSE |
| ano_eleicao | TSE |
| mandato | derivado |
| fonte_prefeito | TSE |
| data_coleta | sistema interno |

---

### 2.2. Vereadores

Fonte principal: TSE.

Os vereadores também são eleitos. Portanto, a base mais confiável é o TSE.

Fontes úteis:

- Portal de Dados Abertos do TSE;
- Resultados 2024;
- Candidatos 2024;
- DivulgaCandContas;
- site da Câmara Municipal, para mandato, mesa diretora, comissões e contatos.

Atenção:

A base do TSE mostra quem foi eleito ou suplente, mas a composição real da Câmara pode mudar durante o mandato por:

- licença;
- cassação;
- morte;
- posse de suplente;
- mudança para cargo no Executivo;
- decisão judicial;
- afastamento.

Por isso, para contato comercial ou político, o ideal é combinar:

1. TSE para base eleitoral oficial;
2. site da Câmara para composição atual;
3. Diário Oficial ou portal da Câmara para mesa diretora e atualizações.

Campos sugeridos:

| Campo | Fonte |
|---|---|
| codigo_ibge | IBGE |
| municipio | IBGE/TSE |
| uf | IBGE/TSE |
| vereador_nome | TSE/Câmara |
| partido | TSE/Câmara |
| situacao | TSE/Câmara |
| cargo_na_camara | Câmara |
| telefone | Câmara |
| email | Câmara |
| gabinete | Câmara |
| fonte | TSE/Câmara |
| data_coleta | sistema interno |

---

### 2.3. Secretários municipais

Secretários não são eleitos. Eles são nomeados pelo prefeito.

Portanto, não existe uma base nacional única, completa e padronizada para secretários de cultura, eventos, turismo, esporte ou comunicação.

Fontes oficiais possíveis:

1. Site da prefeitura:
   - página “Secretarias”;
   - página “Equipe de Governo”;
   - página “Estrutura Administrativa”;
   - organograma;
   - gabinete;
   - contatos institucionais.

2. Portal da Transparência municipal:
   - servidores;
   - cargos comissionados;
   - agentes políticos;
   - remuneração;
   - lotação;
   - vínculo;
   - unidade administrativa.

3. Diário Oficial do Município:
   - decretos de nomeação;
   - portarias de nomeação;
   - exonerações;
   - alterações de estrutura administrativa.

4. Leis municipais:
   - lei de estrutura administrativa;
   - criação/extinção de secretarias;
   - cargos e competências.

5. Tribunal de Contas do Estado:
   - dados de pessoal;
   - prestação de contas;
   - portais específicos por UF.

6. Redes e canais oficiais:
   - Instagram da prefeitura;
   - Facebook oficial;
   - LinkedIn institucional;
   - releases da assessoria de comunicação.

Atenção:

Secretários podem mudar durante o mandato. Por isso, sempre registrar:

- fonte;
- URL;
- data da coleta;
- data de atualização, se houver;
- nível de confiança.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| codigo_ibge | código oficial do município |
| municipio | nome do município |
| uf | estado |
| secretaria | Cultura, Turismo, Eventos, Esporte, Comunicação etc. |
| secretario_nome | nome do titular |
| cargo_exato | Secretário, Diretor, Coordenador, Assessor etc. |
| email | contato institucional |
| telefone | contato institucional |
| url_fonte | site/diário/transparência |
| tipo_fonte | prefeitura, transparência, diário oficial, câmara etc. |
| data_coleta | data da captura |
| confiabilidade | alta, média ou baixa |
| observacoes | mudanças, dúvidas, mandato etc. |

---

### 2.4. Secretário de cultura

É um dos principais contatos para venda de:

- shows;
- festivais culturais;
- editais de cultura;
- artistas locais;
- programação cultural;
- festas tradicionais;
- eventos de calendário cultural;
- projetos com recursos da cultura.

Onde procurar:

- Secretaria Municipal de Cultura;
- Fundação Municipal de Cultura;
- Diretoria de Cultura;
- Departamento de Cultura;
- Conselho Municipal de Cultura;
- Fundo Municipal de Cultura;
- Plano Municipal de Cultura.

Em municípios pequenos, pode não existir uma secretaria exclusiva. A cultura pode estar dentro de:

- Educação e Cultura;
- Turismo e Cultura;
- Esporte, Lazer e Cultura;
- Desenvolvimento Econômico, Turismo e Cultura.

---

### 2.5. Secretário de eventos

Nem todo município possui Secretaria de Eventos.

Possíveis nomes equivalentes:

- Secretaria de Eventos;
- Secretaria de Cultura e Eventos;
- Secretaria de Turismo e Eventos;
- Diretoria de Eventos;
- Departamento de Eventos;
- Coordenadoria de Eventos;
- Assessoria de Eventos;
- Secretaria de Governo;
- Gabinete do Prefeito.

Em municípios menores, eventos grandes costumam ser decididos por:

- prefeito;
- chefe de gabinete;
- secretário de governo;
- secretário de cultura;
- secretário de turismo;
- secretário de comunicação;
- comissão organizadora da festa.

---

### 2.6. Secretário de turismo

Muito relevante quando o evento tem justificativa de:

- atração turística;
- movimentação econômica;
- ocupação hoteleira;
- comércio local;
- exposição da cidade;
- festas tradicionais;
- calendário regional.

Para festas de grande porte, turismo pode ser mais decisivo que cultura.

---

### 2.7. Chefe de gabinete

Contato estratégico, principalmente em cidades pequenas e médias.

Função comercial:

- controla agenda do prefeito;
- filtra demandas;
- influencia prioridades;
- acompanha eventos importantes;
- pode direcionar para o secretário correto;
- pode destravar conversas internas.

---

### 2.8. Compras, licitações, jurídico e finanças

Esses setores geralmente não decidem qual artista contratar, mas podem travar ou viabilizar a contratação.

Papéis:

| Área | Papel |
|---|---|
| Compras/Licitações | orienta modalidade e documentação |
| Jurídico/Procuradoria | valida legalidade da contratação |
| Controle Interno | analisa conformidade e risco |
| Finanças/Fazenda | confirma dotação, empenho e pagamento |
| Contabilidade | classifica despesa e fonte de recurso |
| Ordenador de despesa | autoriza formalmente a despesa |

---

## 3. Fontes oficiais recomendadas para montar a base

### 3.1. IBGE

Uso:

- lista oficial de municípios;
- código IBGE de 7 dígitos;
- UF;
- dados populacionais;
- indicadores municipais.

Importância:

O código IBGE deve ser a chave principal para cruzar bases.

---

### 3.2. TSE

Uso:

- prefeito;
- vice-prefeito;
- vereadores;
- partidos;
- eleições municipais;
- candidatos;
- resultados.

Bases principais:

- Resultados;
- Candidatos;
- DivulgaCandContas.

---

### 3.3. Sites das prefeituras

Uso:

- secretários atuais;
- estrutura administrativa;
- contatos;
- calendário de eventos;
- notícias oficiais;
- organograma;
- gabinete.

Problema:

Não há padronização. Cada prefeitura publica de um jeito.

---

### 3.4. Portais da Transparência

Uso:

- agentes políticos;
- secretários;
- cargos comissionados;
- remuneração;
- vínculos;
- lotação;
- pagamentos;
- empenhos;
- contratos;
- despesas com eventos.

Busca recomendada:

- “secretário de cultura”;
- “secretaria de cultura”;
- “eventos”;
- “turismo”;
- “show”;
- “sonorização”;
- “palco”;
- “iluminação”;
- “inexigibilidade”;
- “artista”;
- “contratação artística”.

---

### 3.5. Diários oficiais

Uso:

- nomeação e exoneração de secretários;
- publicação de contratos;
- extratos de inexigibilidade;
- editais de credenciamento;
- chamamentos públicos;
- portarias de comissão organizadora;
- termos de ratificação;
- homologação;
- empenhos, quando publicados.

Busca recomendada:

- “inexigibilidade”;
- “art. 74”;
- “profissional do setor artístico”;
- “empresário exclusivo”;
- “festa”;
- “aniversário do município”;
- “são joão”;
- “réveillon”;
- “natal”;
- “carnaval”;
- “rodeio”;
- “exposição”;
- “festival”.

---

### 3.6. PNCP — Portal Nacional de Contratações Públicas

Uso:

- contratos;
- editais;
- dispensas;
- inexigibilidades;
- atas;
- compras públicas;
- publicações obrigatórias da Lei 14.133/2021.

Importância:

Na Lei 14.133/2021, a divulgação no PNCP é condição indispensável para eficácia do contrato e aditamentos, ressalvadas hipóteses legais específicas.

---

### 3.7. Câmaras municipais

Uso:

- vereadores atuais;
- mesa diretora;
- comissões;
- leis orçamentárias;
- LOA;
- LDO;
- PPA;
- emendas;
- audiências públicas;
- requerimentos sobre eventos;
- indicações de festas e programações.

A Câmara é relevante porque vereadores podem influenciar eventos locais, emendas, pressão política e prioridades da comunidade.

---

## 4. Como funciona o fluxo de aprovação e orçamento para eventos públicos

### 4.1. Fluxo macro

O fluxo típico é:

1. planejamento do calendário municipal;
2. definição da prioridade política;
3. previsão orçamentária ou identificação de dotação;
4. Documento de Formalização de Demanda;
5. Estudo Técnico Preliminar, quando aplicável;
6. Termo de Referência ou documento equivalente;
7. pesquisa/justificativa de preço;
8. definição da modalidade de contratação;
9. conferência documental;
10. parecer jurídico;
11. controle interno, quando aplicável;
12. autorização da autoridade competente;
13. empenho;
14. contrato, ordem de serviço ou instrumento equivalente;
15. publicação;
16. execução do evento;
17. liquidação;
18. pagamento;
19. prestação de contas e arquivo do processo.

---

### 4.2. Fase 0 — Venda política e entrada no calendário

Antes do processo formal, existe a decisão política e estratégica.

Perguntas internas da prefeitura:

- O evento é prioridade?
- Existe interesse público?
- A população valoriza esse evento?
- Gera turismo?
- Movimenta comércio?
- É tradição da cidade?
- Cabe no orçamento?
- O prefeito quer bancar politicamente?
- A secretaria consegue executar?
- Há risco de crítica pública?

Decisores/influenciadores:

- prefeito;
- vice-prefeito;
- secretário de cultura;
- secretário de turismo;
- secretário de eventos;
- chefe de gabinete;
- secretário de governo;
- vereadores influentes;
- associação comercial;
- lideranças comunitárias;
- comunicação;
- comissão organizadora.

Estratégia comercial:

> Entrar antes do DFD é melhor do que disputar quando o edital já foi publicado.

---

### 4.3. Fase 1 — Planejamento do calendário municipal

A prefeitura define eventos do ano:

- carnaval;
- aniversário da cidade;
- festa junina;
- São João;
- São Pedro;
- festa do padroeiro;
- rodeio;
- exposição agropecuária;
- festival gastronômico;
- festival cultural;
- eventos esportivos;
- feiras;
- natal;
- réveillon;
- eventos turísticos;
- eventos de verão.

Custos normalmente planejados:

- artistas;
- cachês;
- palco;
- som;
- iluminação;
- geradores;
- tendas;
- banheiro químico;
- grades;
- segurança;
- brigadistas;
- limpeza;
- ambulância;
- ECAD;
- comunicação;
- decoração;
- equipe de produção;
- alimentação e hospedagem;
- transporte;
- camarim;
- seguros, quando aplicável.

---

### 4.4. Fase 2 — Compatibilidade orçamentária

A prefeitura precisa demonstrar que há dotação orçamentária.

Possíveis fontes:

- LOA;
- Secretaria de Cultura;
- Secretaria de Turismo;
- Secretaria de Eventos;
- Gabinete;
- Fundo Municipal de Cultura;
- convênios;
- emendas parlamentares;
- Política Nacional Aldir Blanc;
- recursos estaduais/federais;
- patrocínios públicos/privados, quando estruturados.

Sem dotação, a contratação não deve avançar.

---

### 4.5. Fase 3 — Documento de Formalização de Demanda

O DFD é a formalização da necessidade.

Normalmente contém:

- unidade requisitante;
- descrição da necessidade;
- justificativa de interesse público;
- data prevista;
- local;
- público estimado;
- objetivo do evento;
- alinhamento com plano anual ou calendário;
- estimativa preliminar de valor;
- indicação de urgência, se houver;
- responsáveis.

Para produtoras e artistas, é útil entregar material que ajude a secretaria a justificar:

- impacto cultural;
- impacto turístico;
- impacto econômico;
- tradição local;
- atendimento à população;
- valorização de artistas;
- geração de fluxo para comércio;
- fortalecimento da imagem da cidade.

---

### 4.6. Fase 4 — ETP e Termo de Referência

O Estudo Técnico Preliminar pode ser usado para demonstrar a melhor solução para a necessidade pública.

O Termo de Referência detalha a contratação.

Itens comuns no TR:

- objeto;
- justificativa;
- especificações técnicas;
- data e horário;
- local;
- obrigações da contratada;
- obrigações da prefeitura;
- forma de execução;
- critérios de medição;
- condições de pagamento;
- documentação exigida;
- estimativa de preço;
- fiscalização do contrato;
- sanções;
- vigência.

Em contratação artística por inexigibilidade, pode haver documento equivalente ao TR, mas a lógica de instrução processual permanece.

---

### 4.7. Fase 5 — Justificativa de preço

Mesmo quando não há licitação, o preço precisa ser justificado.

Documentos úteis:

- notas fiscais de shows anteriores;
- contratos anteriores;
- empenhos de outras prefeituras;
- publicações no PNCP;
- extratos de inexigibilidade;
- tabela de cachê praticada;
- histórico de apresentações;
- declaração de que o valor é compatível com mercado;
- composição do valor, quando fizer sentido;
- custos de logística;
- rider técnico;
- equipe envolvida;
- deslocamento;
- hospedagem.

A justificativa de preço não deve ser “achismo”. Precisa demonstrar compatibilidade com o mercado.

---

### 4.8. Fase 6 — Definição da modalidade de contratação

Principais caminhos:

#### 4.8.1. Inexigibilidade de licitação

Usada quando a competição é inviável.

Para artistas, a Lei 14.133/2021 prevê inexigibilidade para contratação de profissional do setor artístico, diretamente ou por empresário exclusivo, desde que consagrado pela crítica especializada ou pela opinião pública.

Requisitos práticos:

- artista profissional;
- consagração pela crítica especializada ou opinião pública;
- inviabilidade de competição;
- contratação direta ou via empresário exclusivo;
- justificativa de preço;
- documentação regular;
- parecer jurídico;
- publicação.

Uso típico:

- artista nacional;
- artista regional reconhecido;
- atração específica desejada pela prefeitura;
- show principal de evento oficial.

#### 4.8.2. Credenciamento

Usado para formar banco de artistas, produtores ou serviços.

A prefeitura define:

- regras de habilitação;
- categorias;
- valores;
- documentação;
- critérios de chamada;
- rodízio ou ordem de contratação.

Uso típico:

- artistas locais;
- apresentações culturais;
- grupos regionais;
- oficinas;
- pequenas atrações;
- programação contínua.

#### 4.8.3. Chamamento público

Usado para seleção de projetos, artistas, organizações ou propostas culturais.

Pode aparecer em:

- editais culturais;
- fundos municipais;
- Política Nacional Aldir Blanc;
- festivais;
- programação cultural específica.

#### 4.8.4. Pregão, concorrência ou contratação competitiva

Mais comum para:

- palco;
- som;
- iluminação;
- tendas;
- banheiros químicos;
- geradores;
- gradis;
- segurança;
- brigadistas;
- limpeza;
- comunicação visual;
- decoração;
- produção operacional;
- locação de estruturas.

#### 4.8.5. Registro de preços e ata

A prefeitura pode contratar serviços ou estruturas por ata.

Oportunidade comercial:

- monitorar atas vigentes;
- participar de licitações;
- oferecer adesão quando juridicamente possível;
- cadastrar-se como fornecedor.

#### 4.8.6. Dispensa

Pode ocorrer em hipóteses específicas previstas em lei, especialmente por valor ou circunstância.

Deve ser analisada caso a caso.

---

### 4.9. Fase 7 — Parecer jurídico

O jurídico valida se o processo está regular.

Principais pontos analisados:

- interesse público;
- modalidade correta;
- justificativa do preço;
- documentação da empresa;
- certidões negativas;
- contrato de exclusividade;
- consagração do artista;
- objeto claro;
- ausência de fracionamento indevido;
- compatibilidade orçamentária;
- minuta contratual;
- risco de direcionamento irregular;
- publicação.

Se faltar documento, o processo trava.

---

### 4.10. Fase 8 — Aprovação, empenho e publicação

Após parecer e autorização, a prefeitura emite o empenho.

Empenho:

- reserva o valor da despesa;
- vincula orçamento à contratação;
- é etapa essencial da despesa pública.

Depois vem:

- contrato;
- ordem de serviço;
- autorização de fornecimento;
- publicação no PNCP e/ou Diário Oficial, conforme aplicável.

Regra prática:

> O empenho é o sinal de que existe orçamento reservado. Antes dele, existe intenção. Depois dele, existe compromisso administrativo mais concreto.

---

### 4.11. Fase 9 — Execução, liquidação e pagamento

Após o evento:

1. a prefeitura fiscaliza a execução;
2. comprova que o serviço foi prestado;
3. recebe nota fiscal;
4. faz liquidação;
5. libera pagamento.

Cuidados:

- registrar fotos e vídeos do evento;
- guardar ordem de serviço;
- coletar atesto do fiscal;
- emitir nota fiscal corretamente;
- manter certidões válidas;
- confirmar dados bancários;
- documentar qualquer alteração de escopo.

---

## 5. Diferença entre vender artista, produção e estrutura

### 5.1. Venda de artista específico

Caminho mais provável:

- inexigibilidade, se cumprir requisitos.

Risco principal:

- não comprovar consagração;
- exclusividade fraca;
- preço sem justificativa;
- artista sem notoriedade suficiente.

Documentos-chave:

- release;
- clipping;
- números de público e mídia;
- redes sociais;
- notícias;
- histórico de shows;
- notas fiscais;
- contratos anteriores;
- contrato de exclusividade;
- proposta formal;
- certidões.

---

### 5.2. Venda de estrutura

Caminho mais provável:

- pregão;
- concorrência;
- registro de preços;
- dispensa em hipóteses específicas;
- ata.

Objetos comuns:

- palco;
- som;
- iluminação;
- LED;
- tendas;
- geradores;
- banheiros químicos;
- gradis;
- camarins;
- segurança;
- brigadistas;
- ambulância;
- limpeza.

Risco principal:

- tentar vender estrutura como se fosse inexigibilidade artística.

---

### 5.3. Venda de produção completa

É a mais estratégica, mas juridicamente mais sensível.

Pode incluir:

- curadoria artística;
- coordenação geral;
- estrutura;
- logística;
- fornecedores;
- programação;
- operação de palco;
- comunicação;
- bastidores.

Risco:

Se misturar artista exclusivo com serviços comuns, o jurídico pode questionar por que tudo foi contratado sem competição.

Estratégia mais segura:

- separar contratação artística da estrutura;
- separar o que é inexigível do que é competitivo;
- deixar escopos claros;
- evitar pacote genérico sem justificativa;
- alinhar antes com compras/jurídico.

---

## 6. Exclusividade artística

Para contratação por empresário exclusivo, o ideal é comprovar representação exclusiva real e contínua.

Evitar depender apenas de:

- carta de exclusividade para um único dia;
- carta restrita a uma cidade;
- autorização pontual;
- documento genérico sem vínculo real.

Mais seguro:

- contrato de exclusividade;
- representação contínua;
- prazo definido;
- abrangência clara;
- poderes para negociar;
- assinatura válida;
- documentação da empresa representante.

Redação recomendada:

> Cartas ou declarações de exclusividade pontuais, restritas ao dia ou à localidade do evento, tendem a ser insuficientes. O caminho mais seguro é comprovar representação exclusiva contínua por contrato formal.

---

## 7. Kit documental ideal da produtora/artista

### 7.1. Kit comercial

- apresentação da produtora;
- portfólio de eventos;
- fotos;
- vídeos;
- cases com prefeituras;
- lista de artistas;
- faixas de investimento;
- formatos de evento;
- diferenciais;
- regiões atendidas;
- contatos.

### 7.2. Kit jurídico/fiscal

- CNPJ;
- contrato social;
- documento dos sócios;
- certidões negativas;
- inscrição municipal/estadual, quando aplicável;
- dados bancários;
- comprovante de endereço;
- procurações, se houver;
- CNAE compatível;
- regularidade trabalhista;
- regularidade fiscal.

### 7.3. Kit artístico

- release do artista;
- fotos oficiais;
- vídeos;
- links de mídia;
- clipping;
- histórico de apresentações;
- números de redes sociais;
- matérias na imprensa;
- comprovação de notoriedade;
- rider técnico;
- mapa de palco;
- equipe;
- repertório/estilo;
- notas fiscais de shows anteriores;
- contratos anteriores;
- contrato de exclusividade, se houver.

### 7.4. Kit processual

- proposta formal;
- escopo do objeto;
- justificativa de interesse público sugerida;
- justificativa de preço;
- minuta de descrição técnica;
- documentos de habilitação;
- validade da proposta;
- condições de pagamento;
- obrigações da contratada;
- exigências técnicas;
- cronograma de execução.

Diferencial competitivo:

> A produtora que entrega o processo praticamente pronto reduz o trabalho da prefeitura e aumenta a chance de contratação.

---

## 8. Janelas comerciais para vender para prefeituras

### 8.1. Regra de antecedência

Prazos recomendados:

| Tipo de contratação | Prazo mínimo recomendado |
|---|---:|
| Artista local com documentação pronta | 30 a 60 dias |
| Artista regional por inexigibilidade | 60 a 90 dias |
| Artista nacional | 90 a 180 dias |
| Produção completa | 90 a 180 dias |
| Evento novo que precisa entrar no orçamento | 6 a 12 meses |
| Influenciar LOA do ano seguinte | junho a setembro do ano anterior |

Regra prática:

> Para eventos importantes, abordar 90 a 180 dias antes. Para influenciar orçamento, abordar 6 a 12 meses antes.

---

### 8.2. Calendário comercial anual

| Mês de abordagem | Foco principal |
|---|---|
| Janeiro | últimos ajustes de Carnaval, eventos de verão, aniversário da cidade no 1º semestre |
| Fevereiro | aniversário da cidade, Páscoa, eventos de abril/maio, início de São João |
| Março | festa junina, São João, São Pedro, padroeiro, rodeios, exposições |
| Abril | festas juninas, eventos de julho/agosto, festivais de inverno |
| Maio | segundo semestre, turismo, festas tradicionais, rodeios |
| Junho | Natal, réveillon, verão, LOA do ano seguinte |
| Julho | Natal, réveillon, calendário cultural do próximo ano |
| Agosto | verão, réveillon, Natal, festivais de primavera, orçamento do próximo ano |
| Setembro | Natal, réveillon, eventos de encerramento, Carnaval do próximo ano |
| Outubro | Carnaval, verão, réveillon, oportunidades de fim de ano |
| Novembro | oportunidades pontuais, reforços, substituições, relacionamento para o ano seguinte |
| Dezembro | pós-venda, relacionamento, Carnaval, calendário do ano seguinte |

---

### 8.3. Janelas por evento

| Evento | Melhor janela de venda |
|---|---|
| Carnaval | outubro a dezembro do ano anterior; janeiro só ajustes |
| Festa junina/São João | fevereiro a abril |
| Aniversário da cidade | 4 a 6 meses antes |
| Padroeiro | 3 a 6 meses antes |
| Rodeio/exposição | 5 a 8 meses antes |
| Festival de inverno | março a maio |
| Semana da Pátria | abril a junho |
| Dia das Crianças | junho a agosto |
| Natal | junho a setembro |
| Réveillon | julho a outubro |
| Verão | julho a outubro |
| Calendário do ano seguinte | junho a setembro do ano anterior |

---

## 9. Estratégia comercial recomendada

### 9.1. Não vender só artista; vender solução pública

Argumentos que funcionam melhor:

- movimenta comércio local;
- atrai turistas;
- valoriza cultura local;
- fortalece calendário oficial;
- gera experiência para a população;
- aumenta visibilidade da gestão;
- organiza evento com segurança;
- reduz risco operacional;
- facilita processo documental;
- adequa opções ao orçamento do município.

Evitar abordagem genérica:

> Tenho artista X disponível.

Preferir abordagem consultiva:

> Estou montando uma agenda regional de artistas e formatos de evento para prefeituras. Queria entender se o município já fechou o calendário de festas oficiais ou se ainda está avaliando atrações e produção para os próximos eventos.

---

### 9.2. Mapear municípios prioritários

Critérios:

- população;
- orçamento de cultura/turismo;
- histórico de eventos;
- proximidade logística;
- aniversário da cidade;
- eventos tradicionais;
- partido/grupo político, quando relevante;
- presença de turismo;
- tamanho do comércio local;
- existência de secretaria de cultura/turismo/eventos;
- histórico de contratação de shows;
- valores já pagos em anos anteriores;
- risco de inadimplência;
- qualidade do portal de transparência;
- maturidade administrativa.

---

### 9.3. Mapear decisores por município

Para cada município, buscar:

- prefeito;
- vice-prefeito;
- chefe de gabinete;
- secretário de cultura;
- secretário de turismo;
- secretário de eventos;
- secretário de governo;
- secretário de comunicação;
- diretor de cultura;
- diretor de eventos;
- responsável por compras/licitações;
- procurador/jurídico;
- vereadores influentes;
- presidente da Câmara;
- associação comercial;
- comissão de festas.

---

### 9.4. Classificar contatos por influência

| Perfil | Influência |
|---|---|
| Prefeito | alta em eventos grandes |
| Chefe de gabinete | alta em acesso e agenda |
| Secretário de cultura | alta em programação cultural |
| Secretário de turismo | alta em eventos turísticos |
| Secretário de eventos | alta em execução |
| Secretário de finanças | alta em orçamento e pagamento |
| Compras/licitações | média/alta em viabilidade formal |
| Jurídico | alta em risco/legalidade |
| Vereador | média em indicação e pressão local |
| Comunicação | média em imagem e divulgação |

---

### 9.5. Roteiro de abordagem inicial

Mensagem para secretário:

> Secretário, tudo bem? Trabalho com artistas e produção de eventos para prefeituras. Estou mapeando o calendário de eventos oficiais da região e queria entender se vocês já estão com a programação fechada para os próximos eventos do município ou se ainda estão avaliando atrações e formatos de produção.

Mensagem para prefeito/chefe de gabinete:

> Prefeito, tudo bem? Sei que eventos oficiais movimentam a cidade, fortalecem o comércio local e têm impacto direto na população. Estou com algumas opções de programação artística e produção que podem se adaptar ao porte do município. Vocês já estão com o calendário deste ano fechado?

Mensagem para cultura/turismo:

> Secretário, estou organizando algumas possibilidades de artistas e formatos de evento para festas municipais, turismo e calendário cultural. Posso te apresentar opções por faixa de investimento para vocês avaliarem no planejamento?

---

## 10. Como usar dados públicos para vender melhor

### 10.1. Pesquisar histórico de contratação

Antes de abordar, pesquisar:

- quanto a prefeitura pagou em shows no ano anterior;
- quais artistas contratou;
- qual modalidade usou;
- qual secretaria contratou;
- qual empresa representou;
- valor do cachê;
- data do contrato;
- prazo de pagamento;
- publicação no PNCP;
- diário oficial;
- portal da transparência.

Com isso, a abordagem fica mais inteligente.

Exemplo:

> Vi que no ano passado o município realizou a Festa de São João com atrações regionais e investimento na faixa de R$ X. Estamos com opções semelhantes e também formatos mais completos para este ano.

---

### 10.2. Identificar padrões de evento

Buscar no histórico:

- evento anual recorrente;
- mês em que acontece;
- secretaria responsável;
- valores praticados;
- fornecedores recorrentes;
- modalidade de contratação;
- antecedência da contratação;
- artistas contratados.

Com isso, dá para prever a janela de venda.

---

### 10.3. Criar score comercial de município

Campos sugeridos:

| Campo | Peso sugerido |
|---|---:|
| população | médio |
| histórico de eventos | alto |
| valor já gasto com shows | alto |
| existência de secretaria de turismo/cultura | médio |
| proximidade logística | médio |
| portal de transparência organizado | médio |
| aniversário da cidade próximo | alto |
| evento tradicional próximo | alto |
| contato identificado | alto |
| decisor validado | alto |
| orçamento cultural/turístico | alto |
| risco de pagamento | alto negativo |

---

## 11. Principais riscos

### 11.1. Riscos jurídicos

- inexigibilidade mal justificada;
- artista sem notoriedade suficiente;
- exclusividade fraca;
- preço sem lastro;
- objeto amplo demais;
- mistura indevida de artista e estrutura;
- fracionamento de despesa;
- ausência de dotação;
- documentação vencida;
- ausência de publicação;
- contratação verbal;
- execução antes do empenho.

---

### 11.2. Riscos comerciais

- falar com pessoa sem poder;
- entrar tarde demais;
- competir quando o fornecedor já está escolhido;
- vender artista sem documentação;
- não entender o orçamento do município;
- depender apenas de “amizade política”;
- não acompanhar jurídico/compras;
- não registrar follow-up;
- prometer agenda sem reserva real;
- não calcular logística.

---

### 11.3. Riscos financeiros

- pagamento demorado;
- retenções tributárias;
- nota fiscal incorreta;
- exigência de certidões;
- custo de logística subestimado;
- rider técnico não previsto;
- hospedagem/transporte não negociados;
- alteração de data por clima ou decisão política;
- cancelamento ou adiamento.

---

## 12. Boas práticas

1. Entrar 90 a 180 dias antes do evento.
2. Entrar 6 a 12 meses antes para eventos novos ou grandes.
3. Mapear prefeito, secretário, gabinete e compras.
4. Ter documentação pronta.
5. Ter proposta por faixa de investimento.
6. Separar artista de estrutura quando necessário.
7. Justificar preço com notas e contratos anteriores.
8. Comprovar notoriedade do artista.
9. Usar contrato de exclusividade robusto.
10. Nunca executar sem empenho/contrato/ordem formal.
11. Registrar fonte e data de todo contato público coletado.
12. Monitorar PNCP, Diário Oficial e transparência.
13. Criar histórico por município.
14. Acompanhar LOA e calendário oficial.
15. Tratar secretário como influenciador técnico e prefeito como decisor político em eventos grandes.

---

## 13. Conhecimento comparado: versão consolidada

O conhecimento anterior estava correto principalmente na parte jurídica e processual:

- antecedência é essencial;
- Lei 14.133/2021 precisa ser dominada;
- DFD é a origem formal da demanda;
- precisa haver compatibilidade orçamentária;
- TR e justificativa de preço são centrais;
- jurídico pode travar o processo;
- empenho é etapa crítica;
- publicação é obrigatória;
- inexigibilidade é o caminho para artistas consagrados;
- credenciamento é forte para artistas locais;
- janelas comerciais precisam respeitar o ciclo público.

O complemento estratégico é:

- antes do DFD existe a venda política;
- entrar no calendário é mais valioso do que disputar edital;
- secretário não é sempre decisor final;
- prefeito e gabinete pesam muito em eventos grandes;
- compras e jurídico não escolhem artista, mas podem inviabilizar a contratação;
- vender processo pronto é vantagem competitiva;
- artista, estrutura e produção completa têm tratamentos jurídicos diferentes;
- a melhor operação comercial combina base de dados, calendário, documentação e relacionamento.

Conclusão consolidada:

> Para vender artistas e eventos para prefeituras, a produtora precisa operar como uma combinação de comercial, consultoria pública e backoffice documental. O fechamento não acontece apenas pela força do artista, mas pela capacidade de entrar cedo no calendário, mapear os decisores certos, comprovar interesse público, demonstrar preço compatível, apresentar documentação completa, respeitar o rito da Lei 14.133/2021 e reduzir o trabalho/riscos da prefeitura.

---

## 14. Estrutura de dados recomendada para o projeto

### 14.1. Tabela municipios

```sql
municipios (
  codigo_ibge,
  municipio,
  uf,
  populacao,
  regiao,
  aniversario_cidade,
  site_prefeitura,
  portal_transparencia,
  diario_oficial,
  camara_municipal,
  pncp_orgao_id,
  data_atualizacao
)
```

### 14.2. Tabela agentes_publicos

```sql
agentes_publicos (
  id,
  codigo_ibge,
  municipio,
  uf,
  nome,
  cargo,
  tipo_cargo,
  orgao,
  partido,
  email,
  telefone,
  fonte_url,
  tipo_fonte,
  data_coleta,
  confiabilidade,
  observacoes
)
```

Tipos de cargo:

- prefeito;
- vice_prefeito;
- vereador;
- secretario_cultura;
- secretario_turismo;
- secretario_eventos;
- secretario_governo;
- chefe_gabinete;
- diretor_cultura;
- diretor_eventos;
- compras_licitacoes;
- juridico;
- comunicacao.

### 14.3. Tabela eventos_municipais

```sql
eventos_municipais (
  id,
  codigo_ibge,
  municipio,
  uf,
  nome_evento,
  tipo_evento,
  mes_estimado,
  data_estimativa,
  secretaria_responsavel,
  historico_valor,
  publico_estimado,
  recorrente,
  fonte_url,
  data_coleta,
  observacoes
)
```

Tipos de evento:

- carnaval;
- aniversario_cidade;
- festa_junina;
- sao_joao;
- padroeiro;
- rodeio;
- exposicao;
- festival_cultural;
- festival_gastronomico;
- natal;
- reveillon;
- verao;
- outro.

### 14.4. Tabela contratacoes_historicas

```sql
contratacoes_historicas (
  id,
  codigo_ibge,
  municipio,
  uf,
  ano,
  evento,
  objeto,
  artista_ou_fornecedor,
  empresa_contratada,
  valor,
  modalidade,
  fundamento_legal,
  numero_processo,
  numero_empenho,
  data_contrato,
  data_publicacao,
  fonte_url,
  origem_fonte,
  observacoes
)
```

### 14.5. Tabela oportunidades

```sql
oportunidades (
  id,
  codigo_ibge,
  municipio,
  uf,
  evento_alvo,
  data_evento_estimado,
  janela_ideal_inicio,
  janela_ideal_fim,
  decisor_principal,
  status_contato,
  score_prioridade,
  valor_estimado,
  produto_ofertado,
  proximo_passo,
  responsavel_comercial,
  observacoes
)
```

---

## 15. Prompt-base para agente de pesquisa no Claude Code

Use este prompt para orientar um agente de pesquisa:

```text
Você é um agente de pesquisa especializado em mapear oportunidades de venda de artistas, produtoras e eventos para prefeituras brasileiras.

Sua missão é construir uma base por município contendo:
1. prefeito;
2. vice-prefeito;
3. vereadores relevantes;
4. secretário de cultura;
5. secretário de turismo;
6. secretário de eventos, se houver;
7. chefe de gabinete;
8. contatos de compras/licitações;
9. contatos oficiais da prefeitura;
10. calendário de eventos municipais;
11. histórico de contratações de shows, artistas, estrutura e produção;
12. fontes oficiais e data de coleta.

Priorize fontes oficiais:
- TSE para prefeitos, vice-prefeitos e vereadores eleitos;
- IBGE para identificação oficial do município;
- site da prefeitura para secretários e estrutura administrativa;
- portal da transparência para cargos, contratos, empenhos e pagamentos;
- diário oficial para nomeações, exonerações, editais, inexigibilidades e contratos;
- PNCP para contratações públicas;
- Câmara Municipal para vereadores, leis orçamentárias e contatos.

Para cada informação coletada, registre:
- fonte_url;
- tipo_fonte;
- data_coleta;
- confiabilidade;
- observações.

Nunca trate dado sem fonte como definitivo.
Nunca misture prefeito eleito com prefeito em exercício sem verificar.
Nunca trate secretário como informação permanente; secretários podem mudar durante o mandato.
Sempre que possível, cruze pelo código IBGE do município.

Classifique oportunidades com base em:
- proximidade do evento;
- histórico de gastos com eventos;
- existência de calendário tradicional;
- orçamento cultural/turístico;
- facilidade de encontrar decisores;
- distância logística;
- antecedência disponível;
- compatibilidade com artistas/produtoras disponíveis.

O objetivo final é gerar uma base comercial acionável para abordagem de prefeituras com antecedência de 90 a 180 dias antes dos eventos e de 6 a 12 meses antes quando o objetivo for influenciar orçamento do ano seguinte.
```

---

## 16. Fontes oficiais e referências úteis

- TSE — Portal de Dados Abertos: https://dadosabertos.tse.jus.br/
- TSE — Resultados 2024: https://dadosabertos.tse.jus.br/dataset/resultados-2024
- TSE — Candidatos 2024: https://dadosabertos.tse.jus.br/dataset/candidatos-2024
- TSE — DivulgaCandContas: https://divulgacandcontas.tse.jus.br/
- IBGE — Códigos dos Municípios: https://www.ibge.gov.br/explica/codigos-dos-municipios.php
- Lei 14.133/2021 — Planalto: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm
- TCU — Licitações e Contratos: https://licitacoesecontratos.tcu.gov.br/
- PNCP: https://pncp.gov.br/

---

## 17. Frase final de posicionamento

A melhor produtora para vender para prefeitura não é apenas a que tem o melhor artista.

É a que chega antes, entende o calendário público, conhece os decisores, reduz risco jurídico, entrega documentação pronta, comprova preço, respeita a Lei 14.133/2021 e facilita a vida da secretaria para transformar uma intenção política em contratação pública regular.
