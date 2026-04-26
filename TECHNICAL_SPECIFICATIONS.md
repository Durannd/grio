# Especificações Técnicas: Ecossistema Griô

Este documento detalha a arquitetura, as escolhas tecnológicas e as implementações lógicas que compõem o sistema Griô, uma plataforma de diagnóstico educacional de alta precisão baseada em grafos de conhecimento e inteligência artificial generativa.

---

## 1. Stack Tecnológica Core

A arquitetura do Griô é dividida em três pilares fundamentais, selecionados para garantir escalabilidade horizontal e processamento de dados relacionais complexos:

- **Backend**: Python 3.12 com **FastAPI**. Camada de rede protegida por **Security Headers Middleware** (CSP, HSTS, X-Frame-Options) e **HttpOnly Cookies** para autenticação JWT, eliminando vulnerabilidades de XSS e mitigando riscos de CSRF.
- **Banco de Dados de Conhecimento (Graph DB)**: **Neo4j**. Utilizado para mapear as complexas relações entre questões, habilidades (BNCC/ENEM) e competências, permitindo a propagação de proficiência em tempo real.
- **Banco de Dados Relacional**: **PostgreSQL**. Armazena dados transacionais, perfis de usuários, histórico imutável de avaliações e streaks de atividade.
- **Inteligência Artificial**: **Google Gemini (Família 1.5 e 2.0)**.
    - `gemini-2.5-flash`: Utilizado para auditoria pedagógica, geração de micro-aulas via RAG e mentoria socrática.
    - `text-embedding-004`: Gerador de vetores de alta dimensionalidade (768d) para busca semântica e similaridade de questões.
- **Frontend**: **SvelteKit** com TypeScript. Focado em uma experiência de usuário (UX) fluida ("Warm Earthy Elegance"), utilizando store de estado para Toasts e animações reativas.

---

## 2. Arquitetura de Grafos (Knowledge Graph)

Diferente de sistemas de ensino tradicionais baseados em tabelas estáticas, o Griô modela o conhecimento como uma rede viva no Neo4j.

### Entidades (Nodes)
- **Question**: Item de avaliação com metadados, alternativas, explicação pedagógica e vetor de embedding.
- **Skill (Habilidade)**: Códigos oficiais do ENEM/BNCC. Contém o `content` (micro-aula) e `last_enriched_at`.
- **Competence (Competência)**: Estruturas macro de conhecimento.
- **Area (Área do Conhecimento)**: Matemática, Natureza, Humanas e Linguagens.
- **User**: Perfil do estudante com propriedades de gamificação (`current_streak`, `last_activity_date`).

### Relacionamentos (Edges)
- `(Question)-[:EVALUATES]->(Skill)`
- `(Skill)-[:PART_OF]->(Competence)`
- `(User)-[:HAS_PROFICIENCY {score: float}]->(Skill)`: Define o nível de domínio em tempo real.
- `(User)-[:ANSWERED {time_seconds: int, is_correct: bool}]->(Question)`

---

## 3. Motor de Conteúdo e RAG Pedagógico (Retrieval-Augmented Generation)

Para garantir máxima fidelidade pedagógica, o sistema utiliza RAG para gerar materiais de estudo:

1. **Recuperação de Contexto**: O sistema busca no Neo4j as 10 questões mais representativas da Habilidade solicitada.
2. **Injeção de Exemplos**: O Gemini analisa o enunciado e a explicação técnica destas questões reais antes de gerar o material teórico.
3. **Cache de Longo Prazo**: O conteúdo gerado é persistido no nó da Skill com validade de 5 anos, otimizando custos de API e garantindo baixa latência.

---

## 4. Ciclo de Aprendizado Adaptativo (Feedback Loop)

O sistema opera em um ciclo fechado de evolução de proficiência:
1. **Diagnóstico**: Mapeamento inicial de lacunas em todas as áreas.
2. **Estudo**: Micro-aulas técnicas geradas via IA com base em dados reais.
3. **Prática Direcionada**: Micro-simulados de 10 questões inéditas sobre o tema estudado.
4. **Propagação Neural**: Resultados da prática atualizam a Skill e propagam um bônus de 20% de conhecimento para habilidades irmãs dentro da mesma competência.

---

## 5. Mecanismo de Diagnóstico e Auditoria (Engine Logic)

### Auditoria Pedagógica via IA
Cada submissão de prova passa por uma auditoria em tempo real para detectar comportamentos anômalos (chutes ou automação):
1. **Temporal Audit**: Respostas com tempo inferior a 5 segundos são penalizadas automaticamente com um `confidence_score` de 0.1.
2. **AI Pattern Detection**: O Gemini analisa a correlação entre a dificuldade da questão e o tempo de resposta, ajustando o peso do acerto no cálculo final de proficiência.

---

## 6. Segurança e Autenticação

- **Auth**: Tokens JWT trafegados exclusivamente via **HttpOnly Cookies** com flags `Secure` e `SameSite="Lax"`.
- **Cabeçalhos**: Implementação rigorosa de CSP (`default-src 'none'`), HSTS e proteção contra sniffing de MIME types no middleware do FastAPI.
- **Ambientes**: Flags de segurança dinâmicas baseadas na variável de ambiente `ENV` (production vs development).

---

> **Nota**: Este sistema foi projetado para ser agnóstico ao conteúdo, podendo ser adaptado para OAB, Concursos ou Treinamentos Corporativos apenas alterando a Matriz de Referência no grafo.
