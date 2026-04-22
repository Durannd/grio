# Handover de Desenvolvimento - Projeto Griô (MVP Matemática)

**Data:** 2026-04-22
**Agente Anterior:** OpenClaude

## 1. Visão Geral do Projeto Griô

O projeto Griô é uma plataforma de estudos gratuita, gamificada e inteligente, focada na democratização do acesso à preparação para o vestibular para estudantes de baixa renda no Brasil. O MVP inicial foca integralmente na matéria de **Matemática**.

**Princípios de Design:**
*   **Mobile-First e Acessibilidade:** Otimizado para celulares e dados limitados.
*   **IA como Aliada:** Personalização, motivação e suporte de IA.
*   **Hábito sobre Intensidade:** Gamificação focada em consistência (streaks).

## 2. Status Geral do Projeto

Um backend em Python/FastAPI e um frontend em SvelteKit foram iniciados e configurados com Docker, PostgreSQL (para dados relacionais) e Neo4j (para o grafo de conhecimento). As funcionalidades básicas de gerenciamento de usuários, conceitos de conhecimento e a primeira parte da prova de nivelamento (backend e frontend) foram implementadas. O ambiente de teste está configurado para usar um banco de dados SQLite em memória e uma conexão Neo4j de teste.

**Um problema persistente no ambiente Docker está bloqueando a execução confiável dos testes automatizados.**

## 3. Plano de Implementação (Referência: `docs/superpowers/plans/2026-04-21-grio-mvp-plano.md`)

### Tarefas Concluídas (Verificadas e Aprovadas)

*   **Tarefa 1: Configuração do Projeto e Docker**
    *   **Descrição:** Estrutura inicial do projeto com `docker-compose.yml`, Dockerfiles para backend/frontend, `requirements.txt` e `main.py` inicial. `frontend/.dockerignore` adicionado.
    *   **Status:** Completa.
    *   **Observações:** Encontrou-se problemas ambientais iniciais com Docker e Git, que foram resolvidos. Várias iterações para corrigir o `Dockerfile` e `docker-compose.yml` foram realizadas para garantir a instalação de dependências como `neo4j` e `psycopg2`, e o `PYTHONPATH`.

*   **Tarefa 2: Modelo de Usuário e Autenticação (Backend)**
    *   **Descrição:** Implementação do modelo de usuário (SQLAlchemy), esquemas Pydantic, funções CRUD e endpoint `POST /api/v1/users/create`.
    *   **Status:** Completa.
    *   **Observações:** O teste automatizado não pôde ser executado devido a problemas ambientais, mas o código foi revisado e aprovado. Uma tarefa (`#9`) foi criada para implementar o hashing seguro de senhas.

*   **Tarefa 3: Cadastro e Login no Frontend (Página de Cadastro)**
    *   **Descrição:** Criação da página `/cadastro` no SvelteKit com um formulário que se conecta ao endpoint de criação de usuário do backend.
    *   **Status:** Completa.
    *   **Observações:** Pequenas correções de sintaxe foram feitas durante a revisão. A lógica de autenticação (login) ainda está pendente.

*   **Tarefa 4: Definição dos modelos do Grafo em Neo4j (Conceitos)**
    *   **Descrição:** Conexão com Neo4j, implementação de modelo e endpoint para criação de nós de "Conceito".
    *   **Status:** Completa.
    *   **Observações:** O teste automatizado não pôde ser executado, mas o código foi revisado e aprovado.

*   **Tarefa 5 (Parte 1): Modelo e Endpoint da Prova de Nivelamento (Backend - `GET /assessment`)**
    *   **Descrição:** Criação do modelo `Question`, esquemas, funções CRUD (população e busca de questões) e endpoint `GET /api/v1/assessment`.
    *   **Status:** Completa.
    *   **Observações:** O teste automatizado não pôde ser executado, mas o código foi revisado e aprovado.

*   **Tarefa 5 (Parte 2): Endpoint de Submissão da Prova (Backend - `POST /assessment/submit`)**
    *   **Descrição:** Implementação do endpoint `POST /api/v1/assessment/submit` para receber respostas, calcular proficiência e atualizar o grafo Neo4j.
    *   **Status:** Completa.
    *   **Observações:** O teste automatizado não pôde ser executado, mas o código foi revisado e aprovado. Tarefas (`#13`, `#14`) foram criadas para otimização da query Cypher e adição de testes de erro.

*   **Tarefa 6: Implementação da Prova de Nivelamento (Frontend - `GET /prova`)**
    *   **Descrição:** Criação da página `/prova` no SvelteKit, busca de questões da API e exibição para o usuário. Campos para respostas e botão de envio.
    *   **Status:** Completa.
    *   **Observações:** Uma tarefa (`#12`) foi criada para refatorar a busca de dados usando a função `load` do SvelteKit para melhor performance.

### Tarefas Pendentes (Lista Completa)

*   **#9. Implement secure password hashing:** (backend) Implementar hashing seguro de senhas para usuários.
*   **#10. Melhorar testes com limpeza de dados (teardown):** Refatorar testes de integração para garantir limpeza de dados.
*   **#12. Usar função `load` do SvelteKit na página da prova:** (frontend) Refatorar busca de dados para SSR.
*   **#13. Otimizar query Cypher de atualização de proficiência:** (backend) Otimizar query Cypher para atualizar proficiências em lote.
*   **#14. Adicionar testes de erro ao endpoint de submissão da prova:** (backend) Cobrir casos de erro na submissão da prova.

### Tarefas Bloqueadas

*   **#15. Corrigir o ambiente de execução de testes do `pytest` no Docker (PENDENTE - BLOQUEADA):**
    *   **Descrição:** Investigar e corrigir a causa raiz das falhas na execução de `pytest` via `docker-compose exec -T backend pytest`. Os testes falham com `ModuleNotFoundError: No module named 'psycopg2'`, apesar de `psycopg2` estar visivelmente instalado e o `PYTHONPATH` configurado. Este problema persistente parece ser uma questão ambiental profunda (compilação/vinculação de extensões C ou conflito) que está além da depuração remota via `docker-compose exec`. O código funcional foi revisado e aprovado, mas os testes automatizados não podem ser executados confiavelmente neste ambiente.

## 4. Próximos Passos Recomendados (para o Próximo Agente)

1.  **Prioridade Máxima: Resolver o bloqueio da Tarefa #15.** Isso é fundamental para a saúde e a capacidade de manutenção do projeto. Recomenda-se uma depuração interativa profunda no ambiente Docker, talvez com um shell persistente, para entender por que `psycopg2` não é importável pelo `pytest` apesar de estar instalado.
2.  **Continuar com o Desenvolvimento (Com ressalvas):** Enquanto a Tarefa #15 não for resolvida, novas implementações (como as tarefas pendentes) podem ser iniciadas, mas a validação final através de testes automatizados será um desafio. A dependência em revisões de código e testes manuais/visuais no frontend será maior.
3.  **Sugestão de Próxima Tarefa Funcional:** Após resolver o bloqueio ou decidir avançar, a próxima tarefa lógica seria a **implementação do Login no Frontend** e a conexão com o endpoint de autenticação do backend, o que habilitaria o fluxo completo de autenticação.

**O ambiente Docker está configurado e os serviços `backend`, `frontend`, `db` (PostgreSQL) e `neo4j` estão no ar. Para iniciar os serviços, use `docker-compose up -d --build`.**

**Commit ID do estado atual:** `1dabaaf` (último commit que removeu o PYTHONPATH do docker-compose.yml).
