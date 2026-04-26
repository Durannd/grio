# Especificações Técnicas: Ecossistema Griô

Este documento detalha a arquitetura, as escolhas tecnológicas e as implementações lógicas que compõem o sistema Griô, uma plataforma de diagnóstico educacional de alta precisão baseada em grafos de conhecimento e inteligência artificial generativa.

---

## 1. Stack Tecnológica Core

A arquitetura do Griô é dividida em três pilares fundamentais, selecionados para garantir escalabilidade horizontal e processamento de dados relacionais complexos:

- **Backend**: Python 3.12 com **FastAPI**. Escolhido pela alta performance assíncrona (ASGI) e integração nativa com ecossistemas de IA. A camada de rede conta com **Security Headers Middleware** (CSP, HSTS, XSS Protection, X-Frame-Options) para proteção nativa contra vulnerabilidades de injeção em navegadores e sniffers.
- **Banco de Dados de Conhecimento (Graph DB)**: **Neo4j**. Utilizado para mapear as complexas relações entre questões, habilidades (BNCC/ENEM) e competências.
- **Banco de Dados Relacional**: **PostgreSQL**. Armazena dados transacionais, perfis de usuários e logs de acesso.
- **Inteligência Artificial**: **Google Gemini (Família 1.5 e 2.0)**.
    - `gemini-2.5-flash`: Utilizado para enriquecimento pedagógico e rotulagem de dados em larga escala.
    - `text-embedding-004`: Gerador de vetores de alta dimensionalidade (768d) para busca semântica.
- **Frontend**: **SvelteKit** com TypeScript. Focado em uma experiência de usuário (UX) fluida e visualização de dados reativa.

---

## 2. Arquitetura de Grafos (Knowledge Graph)

Diferente de sistemas de ensino tradicionais baseados em tabelas estáticas, o Griô modela o conhecimento como uma rede viva no Neo4j.

### Entidades (Nodes)
- **Question**: Representa o item de avaliação. Contém metadados como texto, alternativas, explicação pedagógica e o vetor de embedding.
- **Subtopic**: Granularidade fina do conhecimento (ex: "Equação de 2º Grau").
- **Skill (Habilidade)**: Códigos oficiais do ENEM/BNCC (ex: "H1", "H2").
- **Competence (Competência)**: Estruturas macro de conhecimento (ex: "Linguagens e suas Tecnologias").
- **User**: Representa o estudante e sua evolução temporal.

### Relacionamentos (Edges)
- `(Question)-[:COVERS_TOPIC]->(Subtopic)`
- `(Question)-[:EVALUATES]->(Skill)`
- `(Question)-[:REQUIRES_COMPETENCE]->(Competence)`
- `(User)-[:HAS_PROFICIENCY {score: float}]->(Skill|Subtopic)`: A aresta que define o nível de domínio do aluno em tempo real.
- `(User)-[:ANSWERED {time_seconds: int, is_correct: bool}]->(Question)`

---

## 3. Vetores e Busca Semântica (Vector Search)

O Griô utiliza **Neo4j Vector Index** para realizar operações de similaridade em nível de banco de dados.

### Inteligência Artificial e Vetores
Para cada questão ingerida, o sistema concatena o enunciado com a explicação pedagógica gerada pela IA e gera um vetor de 768 dimensões.
- **SDK**: `google.genai` (Migrado do obsoleto `google.generativeai`).
- **Modelo de Geração**: `gemini-2.5-flash`.
- **Modelo de Embedding**: `text-embedding-004`.
- **Métrica de Similaridade**: Coseno (`cosine`).
- **Uso**: Permite que o sistema encontre questões "irmãs" ou identifique lacunas de conhecimento correlatas mesmo que não compartilhem a mesma etiqueta (tag) manual.

---

## 4. Mecanismo de Diagnóstico e Auditoria (Engine Logic)

O "coração" do Griô é o seu motor de diagnóstico, que vai além da contagem de acertos e erros.

### Auditoria Pedagógica via IA
Cada submissão de prova passa por uma auditoria em tempo real para detectar comportamentos anômalos (chutes ou automação):
1. **Temporal Audit**: Respostas com tempo inferior a 5 segundos são penalizadas automaticamente com um `confidence_score` de 0.1, independentemente do acerto.
2. **AI Pattern Detection**: O Gemini analisa a correlação entre a dificuldade da questão e o tempo de resposta. Um acerto em uma questão "Difícil" em 8 segundos é marcado como "Baixa Confiança".

### Cálculo de Proficiência e Persistência Híbrida
A proficiência é o núcleo do sistema e segue um modelo de **Estado Híbrido**:

- **Grafo Cumulativo (Neo4j)**: O grafo de `(User)-[:HAS_PROFICIENCY]->(Skill)` atua como a **memória de longo prazo** do estudante. A cada nova avaliação, o grafo é atualizado via `MERGE`, garantindo que o conhecimento é cumulativo. Habilidades de avaliações anteriores são preservadas, e o `score` é atualizado para refletir o estado mais recente, mas nunca apagado.
- **Snapshot Histórico (PostgreSQL)**: Para cada avaliação submetida (`AssessmentAttempt`), o sistema salva um "snapshot" (JSON) dos resultados daquela sessão específica. Isso cria um **registro histórico imutável**, permitindo que o usuário (e o sistema) analisem o desempenho em um ponto específico no tempo, sem interferência de avaliações futuras.
- **Propagação Lateral**: Se o aluno domina uma Skill, o sistema atribui um "crédito de confiança" inicial para Skills correlatas, assumindo que conhecimentos são parcialmente compartilhados.
- **Auditoria de Confiança**: Respostas muito rápidas são penalizadas para garantir a integridade dos dados de proficiência.

---

## 5. Pipeline de Ingestão e Enriquecimento

O processo de entrada de dados é 100% automatizado via scripts de `Enrichment`:
1. **Ingestão**: Leitura de JSONs brutos do ENEM.
2. **Análise Pedagógica**: O Gemini atua como um consultor educacional, identificando quais habilidades aquela questão realmente testa.
3. **Classificação Diagnóstica**: A IA marca questões como `is_diagnostic` (questões estruturantes) para compor a prova inicial de novos usuários.
4. **Indexação**: Persistência no Neo4j e criação automática de restrições de integridade.

---

## 6. Interfaces e Visualização (UX/UI)

O frontend utiliza um sistema de **Glassmorphism** e animações de estado para transformar dados técnicos de grafos em uma experiência compreensível:
- **Mapa de Calor de Proficiência**: Traduz os pesos das arestas do Neo4j em cores e gradientes.
- **AI Mentor Insights**: Uma camada de síntese que lê o estado do grafo do usuário e gera um resumo executivo em linguagem natural sobre onde o estudante deve focar.

---

> **Nota**: Este sistema foi projetado para ser agnóstico ao conteúdo, podendo ser adaptado para OAB, Concursos ou Treinamentos Corporativos apenas alterando a Matriz de Referência no grafo.
