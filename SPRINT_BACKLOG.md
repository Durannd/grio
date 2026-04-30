# Sprint Backlog - MVP Griô (1 Semana)

*Este documento deve ser obrigatoriamente atualizado pelo agente responsável pela execução das tarefas. O status de uma tarefa só pode ser movido para "Concluído" após a execução e passagem bem-sucedida dos testes correspondentes.*

---

## Visão do Produto (Contexto Estratégico)

### 1. Análise de Lacunas (Gap Analysis): A Falha Linear vs. O Aprendizado em Grafo

**A Falha Metodológica da Concorrência:**
As plataformas atuais (Descomplica, Ferretto, Aprova Total) constroem "Cronogramas de Estudo" lineares. O aluno estuda Cinemática na segunda-feira, Função de 1º Grau na terça, e Revolução Industrial na quarta. Essas áreas nunca se conversam na plataforma. Se o aluno erra uma questão de Física por deficiência em Matemática Básica, o sistema da concorrência manda ele "assistir à aula de Física de novo" ou recorrer a um "Tutor de IA" para explicar a questão isoladamente.

**Como isso gera as dores relatadas:**
1.  **Frustração Invisível e Abandono:** A inteligência da concorrência (como o Personal Prof ou a metodologia EMORA) trata o sintoma, não a doença. O aluno estuda, mas a nota no simulado não sobe, gerando o sentimento de "isso não é pra mim". O resultado é a evasão, que leva à avalanche de atritos de cancelamento e cobrança no ReclameAqui.
2.  **Desalinhamento com o ENEM:** O ENEM não testa disciplinas, testa Competências e Habilidades (Eixos Cognitivos). Ao separar as matérias rigidamente, a concorrência obriga o aluno a fazer o esforço cognitivo de cruzar os dados sozinho na hora da prova.

**Nossa Vantagem "Area-First":**
Nosso banco em grafo entende que o conhecimento não é uma escada, é uma teia. Ao invés de estruturar dados em tabelas relacionais (curso -> módulo -> aula), nós modelamos `Conceito -> Requer -> Conceito` e `Fenômeno -> Engloba -> Habilidade`.

---

### 2. Solução via Grafos: A Arquitetura da Interdependência

Estrategicamente, nossa arquitetura Neo4j nos permite fazer **Diagnóstico de Raiz (Root-Cause Analysis)** em tempo real. Quando o nó "Aluno" se conecta ao nó "Erro na Questão", o grafo rastreia recursivamente as arestas `[DEPENDS_ON]` até encontrar o nó conceitual exato que está deficitário, independentemente da matéria de origem.

**Exemplo Prático 1: O Eixo da Energia (Ciências da Natureza + Matemática)**
*   **O Cenário Tradicional:** O aluno erra uma questão sobre cálculo de conta de luz. O sistema tradicional prescreve "Revisar Eletrodinâmica".
*   **A Topologia do nosso Grafo:** A questão de conta de luz está ligada a dois nós principais:
    *   Nó A (Natureza - H5): "Dimensionar circuitos ou dispositivos elétricos de uso cotidiano."
    *   Nó B (Matemática - H15 / H16): "Identificar a relação de dependência entre grandezas" e "Resolver situação-problema envolvendo a variação de grandezas (direta/inversa)".
*   **A Solução:** Se o grafo detecta que o aluno acerta questões teóricas de Física, mas erra cálculos, ele não receita Física. Ele ativa uma micro-lição de Proporção e Grandezas (Matemática) aplicada ao contexto de consumo elétrico. O aluno conserta a base matemática e, por tabela, destrava a habilidade em Física.

**Exemplo Prático 2: O Eixo da Sustentabilidade (Ciências Humanas + Ciências da Natureza + Linguagens)**
*   **O Cenário Tradicional:** Meio Ambiente é ensinado em Biologia e Geografia, em meses diferentes do ano.
*   **A Topologia do nosso Grafo:** Criamos um "Cluster Area-First" chamado `Crise Climática`, conectando:
    *   Nó A (Humanas - H28): "Relacionar o uso das tecnologias com os impactos socioambientais."
    *   Nó B (Natureza - H10): "Analisar perturbações ambientais... prevendo efeitos em sistemas naturais, produtivos ou sociais."
    *   Nó C (Linguagens - H21): "Reconhecer em textos... recursos verbais utilizados com a finalidade de criar/mudar comportamentos." (ex: campanhas de conscientização ecológica).
*   **A Solução:** Entregamos ao aluno uma Trilha de Área. Ele estuda o fenômeno do desmatamento e, em uma mesma sessão dinâmica, o grafo garante que as habilidades de interpretar o impacto social (Humanas), os ciclos biogeoquímicos (Natureza) e o discurso da campanha ambiental (Linguagens) sejam validadas. Treinamos o cérebro exatamente como o ENEM cobra: via Eixo Cognitivo II (Compreender fenômenos).

---

### 3. Feature Mapping: Mínimo Produto Viável (MVP) Core

Para atacar as fraquezas sistêmicas do Stoodi, Descomplica e Ferretto (suporte lento, plataformas estáticas, aprendizagem mecânica), focaremos nessas 3 funcionalidades exclusivas baseadas em grafos:

**Feature 1: "Mapa de Conhecimento Dinâmico" (Knowledge Skill-Tree)**
*   **O que é:** Uma visualização interativa do grafo do próprio aluno (estilo árvore de habilidades de um RPG). Em vez de uma barra de progresso linear aborrecida ("Você completou 15% do curso"), o aluno vê constelações de conhecimento se acendendo. Ao dominar "Porcentagem", ele vê as linhas brilharem e destravarem conexões para "Juros" (Matemática), "Demografia" (Humanas) e "Genética" (Natureza).
*   **Ataque ao Concorrente:** Destrói a sensação de estagnação. Traz gamificação visual real (superior ao painel estático do Aprova Total), aumentando a retenção e derrubando as taxas de cancelamento prematuro.

**Feature 2: "Motor de Diagnóstico de Raiz" (Root-Cause Recommender)**
*   **O que é:** Quando o aluno erra um exercício ou simulado, não mostramos apenas a resolução em vídeo. O backend em Neo4j roda uma query de travessia de grafo (`MATCH (student)-[:FAILED]->(question)-[:REQUIRES]->(concept)`) e identifica o "pré-requisito fantasma" que o aluno não sabe. O sistema gera um pop-up: "Você errou a questão de Química não por causa da Química, mas porque sua base em Regra de Três está em 40%. Quer focar 5 minutos nisso para nunca mais errar estequiometria?"
*   **Ataque ao Concorrente:** Torna obsoleto o modelo de "Tutoria IA / Personal Prof" do Descomplica e Ferretto, que apenas regurgita explicações de texto generativo da mesma questão. Entregamos remediação precisa, de altíssimo impacto e valor percebido imediato.

**Feature 3: "Trilhas de Fenômenos" (Interdisciplinary Playlists)**
*   **O que é:** Abolimos os módulos tradicionais. Substituímos por trilhas baseadas nos Eixos Cognitivos da Matriz. O aluno escolhe estudar o fenômeno "A Construção da Argumentação (Eixo IV)". A plataforma utiliza o grafo para puxar dinamicamente pílulas e exercícios que misturam: H24 de Linguagens (estratégias argumentativas) + H22 de Matemática (conhecimento algébrico como argumento) + H14 de Natureza (padrões vitais).
*   **Ataque ao Concorrente:** Entrega uma preparação 100% voltada à Teoria de Resposta ao Item (TRI) e ao formato estrutural do ENEM, algo que a concorrência tenta fazer apenas superficialmente em "lives de véspera". Isso nos posiciona não como um cursinho online, mas como a única plataforma de engenharia reversa do ENEM.

---
---

### **Épico 1: [Backend] Fundação da API e Conexão com o Grafo**

*Objetivo: Estabelecer a base da aplicação FastAPI, conectar com Neo4j/Redis e expor um endpoint de saúde.*

- [ ] **[Task 1.1] Configurar Estrutura de Camadas (DDD)**
  - **Descrição:** Criar a estrutura de diretórios para `api` (controladores), `domain` (regras de negócio/serviços), `infrastructure` (acesso a dados) e `core` (configurações).
  - **Critério de Aceite:** A estrutura de pastas está criada e os arquivos `__init__.py` estão posicionados para definir os módulos.
  - **Stack/Arquivo:** `backend/api/`, `backend/domain/`, `backend/infrastructure/`

- [ ] **[Task 1.2] Implementar Conexão com Neo4j e Redis**
  - **Descrição:** Desenvolver singletons ou injetores de dependência para gerenciar as conexões com o Neo4j e o Redis, lendo as credenciais de variáveis de ambiente.
  - **Critério de Aceite:** Funções `get_neo4j_session()` e `get_redis_client()` estão disponíveis e funcionando na camada de infraestrutura.
  - **Stack/Arquivo:** `backend/infrastructure/database.py`, `backend/core/env.py`

- [ ] **[Task 1.3] Criar Endpoint de Health Check**
  - **Descrição:** Implementar um endpoint `GET /health` que verifica a conexão com o banco de dados principal (Neo4j) e o cache (Redis).
  - **Critério de Aceite:** Ao acessar `GET /health`, a API retorna `{"status": "ok", "neo4j": "connected", "redis": "connected"}`.
  - **Stack/Arquivo:** `backend/api/health_check.py`, `backend/main.py`

---

### **Épico 2: [Backend] Implementação do "Motor de Diagnóstico de Raiz"**

*Objetivo: Entregar a lógica de negócio que identifica a causa raiz dos erros do aluno.*

- [ ] **[Task 2.1] Endpoint de Submissão de Tentativa**
  - **Descrição:** Criar o endpoint `POST /v1/students/{id}/attempts` para registrar a tentativa de um aluno em uma questão e disparar o cálculo de domínio.
  - **Critério de Aceite:** O endpoint aceita um payload com `question_id` e `is_correct`, e retorna `202 Accepted`. A lógica de cálculo pode ser um `pass` por enquanto.
  - **Stack/Arquivo:** `backend/api/v1/assessment.py`

- [ ] **[Task 2.2] Serviço de Domínio (Use Case)**
  - **Descrição:** Implementar a lógica de negócio (`RootCauseService`) que recebe o ID do aluno e da questão, executa a query Cypher otimizada para encontrar o pré-requisito fantasma.
  - **Critério de Aceite:** O serviço possui um método que retorna os 3 conceitos de pré-requisito com menor domínio, conforme a query definida na arquitetura.
  - **Stack/Arquivo:** `backend/domain/services/root_cause_service.py`

- [ ] **[Task 2.3] Repositório de Diagnóstico (Infra)**
  - **Descrição:** Criar a classe `Neo4jDiagnosticRepository` que abstrai a execução da query Cypher no Neo4j, recebendo os parâmetros e tratando a resposta do banco.
  - **Critério de Aceite:** O repositório executa a query e mapeia o resultado para um DTO (Data Transfer Object) Python.
  - **Stack/Arquivo:** `backend/infrastructure/repositories/diagnostic_repository.py`

- [ ] **[Task 2.4] Expor Endpoint do Diagnóstico de Raiz**
  - **Descrição:** Criar o endpoint `GET /v1/students/{id}/root-cause?question_id=` que utiliza o `RootCauseService` para retornar o diagnóstico ao cliente.
  - **Critério de Aceite:** O endpoint retorna o JSON com os conceitos de pré-requisito e seus respectivos domínios.
  - **Stack/Arquivo:** `backend/api/v1/diagnostic.py`

---

### **Épico 3: [Frontend] Setup e Componentes Atômicos do Mapa de Conhecimento**

*Objetivo: Configurar o ambiente SvelteKit e criar os blocos de construção reutilizáveis para a visualização do grafo.*

- [ ] **[Task 3.1] Setup do SvelteKit 5 e Estrutura de Rotas**
  - **Descrição:** Inicializar o projeto SvelteKit, definir a estrutura de pastas (`/routes/(app)/mapa/[area]`) e configurar o layout principal (`+layout.svelte`) com o shell da aplicação (header, navegação, etc).
  - **Critério de Aceite:** A rota `/mapa/natureza` carrega o layout da aplicação sem dados.
  - **Stack/Arquivo:** `frontend/src/routes/(app)/+layout.svelte`, `frontend/src/routes/(app)/mapa/[area]/+page.svelte`

- [ ] **[Task 3.2] Componente Atômico: `ConceptNode.svelte`**
  - **Descrição:** Criar o componente que renderiza um único nó do grafo. Ele deve aceitar propriedades como `name`, `mastery` e `selected`.
  - **Critério de Aceite:** O componente renderiza um círculo cujo preenchimento é derivado do `mastery` e exibe o nome do conceito.
  - **Stack/Arquivo:** `frontend/src/lib/components/knowledge-map/ConceptNode.svelte`

- [ ] **[Task 3.3] Componente Atômico: `EdgeLayer.svelte`**
  - **Descrição:** Criar o componente que renderiza as arestas (linhas) entre os nós, com base em um array de `edges`.
  - **Critério de Aceite:** O componente desenha linhas SVG conectando os `ConceptNode`s.
  - **Stack/Arquivo:** `frontend/src/lib/components/knowledge-map/EdgeLayer.svelte`

---

### **Épico 4: [Frontend] Orquestração e Interatividade do Mapa de Conhecimento**

*Objetivo: Juntar os componentes atômicos, buscar dados do backend e tornar o mapa interativo.*

- [ ] **[Task 4.1] Carregamento de Dados (SSR)**
  - **Descrição:** Implementar a função `load` no `+page.server.ts` para buscar os dados do mapa de conhecimento a partir do endpoint `dashboard-bootstrap` do FastAPI.
  - **Critério de Aceite:** Os dados dos nós e arestas são carregados no servidor e passados para o componente de página.
  - **Stack/Arquivo:** `frontend/src/routes/(app)/mapa/[area]/+page.server.ts`

- [ ] **[Task 4.2] Componente de Orquestração: `GraphViewport.svelte`**
  - **Descrição:** Montar o viewport principal do grafo, combinando `ConceptNode` e `EdgeLayer`. Utilizar Runes (`$state`, `$derived`) para gerenciar o estado de nós/arestas e o nó selecionado.
  - **Critério de Aceite:** O mapa de conhecimento é renderizado estaticamente com os dados vindos do SSR.
  - **Stack/Arquivo:** `frontend/src/lib/components/knowledge-map/GraphViewport.svelte`

- [ ] **[Task 4.3] Implementar Interatividade de Seleção**
  - **Descrição:** Adicionar a lógica de clique nos `ConceptNode`s para atualizar o estado `selectedId` no `GraphViewport`.
  - **Critério de Aceite:** Ao clicar em um nó, seu estado muda para "selecionado" e um painel de detalhes (`RootCauseSheet.svelte`) é exibido com as informações do nó.
  - **Stack/Arquivo:** `frontend/src/lib/components/knowledge-map/GraphViewport.svelte`, `frontend/src/lib/components/knowledge-map/RootCauseSheet.svelte`

- [ ] **[Task 4.4] Conectar Diagnóstico de Raiz (Client-Side)**
  - **Descrição:** No painel de detalhes (`RootCauseSheet`), ao clicar em um botão "Analisar Ponto Fraco", fazer uma chamada `fetch` no lado do cliente para o endpoint `GET /v1/students/{id}/root-cause` e exibir a recomendação.
  - **Critério de Aceite:** O painel exibe a mensagem de diagnóstico com o pré-requisito fantasma retornado pela API.
  - **Stack/Arquivo:** `frontend/src/lib/components/knowledge-map/RootCauseSheet.svelte`
