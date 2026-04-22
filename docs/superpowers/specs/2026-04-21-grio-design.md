# Design Spec: Plataforma de Estudos para Vestibular
**Versão:** 3.0 (Pré-Implementação)
**Autor:** OpenClaude & Usuário
**Data:** 2026-04-21
**Status:** Aprovado para Planejamento

## 1. Visão e Princípios
*   **Visão:** Democratizar o acesso à preparação para o vestibular para estudantes de baixa renda no Brasil através de uma plataforma gratuita, gamificada e inteligente.
*   **Princípios de Design:** Mobile-First e Acessibilidade; IA como Aliada; Hábito sobre Intensidade.

## 2. Abordagem Estratégica: MVP Vertical (Foco em Matemática)
Construir todas as funcionalidades para a matéria de Matemática para validar o modelo completo em uma escala controlada.

## 3. Detalhamento do Design Funcional

### 3.1. Onboarding
*   **Prova de Nivelamento (MVP):** A abordagem inicial não será um sistema adaptativo complexo (IRT). Será um **banco de questões pré-categorizadas por dificuldade (fácil, médio, difícil)** para os principais eixos da matemática. O resultado gerará um "scoring inteligente" que mapeia a proficiência inicial do aluno nos conceitos do grafo.

### 3.2. Trilha de Aprendizado
*   **Conteúdo da Etapa "Aprenda" (MVP):** A curadoria de conteúdo será composta por **links diretos para vídeos e materiais de canais educacionais de alta reputação** (ex: Khan Academy em Português, Ferretto Matemática, etc.). A plataforma organizará esses links na sequência pedagógica correta. Não haverá conteúdo de vídeo/texto hospedado ou criado pela plataforma no MVP.

### 3.3. Gamificação
*   Foco em **Streaks (Sequências)** para criar o hábito diário de estudo, complementado por um sistema de **Conquistas** por marcos alcançados.

### 3.4. O Cérebro: Banco de Dados em Grafo
*   O grafo modelará o conhecimento (conceitos, dependências), o conteúdo (exercícios, links externos) e o **perfil do aluno** (nós de proficiência conectando o aluno a cada conceito).

## 4. Arquitetura Técnica

*   **Frontend:** **Svelte (com SvelteKit)** - Foco em performance mobile.
*   **Backend:** **Python (com FastAPI)** - Foco em integração com IA.
*   **Banco de Dados Primário:** **PostgreSQL** - Para dados relacionais como usuários, autenticação, configurações e logs.
*   **Banco de Dados de Conhecimento:** **Neo4j** - Para o grafo de conhecimento, conteúdo e proficiência do aluno.
*   **Cache:** **Redis** - Para otimizar a performance, armazenando em cache sessões de usuário e consultas frequentes.
*   **Inteligência Artificial (MVP):** Todas as funcionalidades de IA (chat, resumos, análise de respostas) serão implementadas utilizando a **API oficial do Gemini**. A migração para modelos open-source (ex: Llama, Mistral) rodando em infraestrutura própria será explorada no futuro como uma estratégia de otimização de custos.

## 5. Viabilidade e Sustentabilidade

*   **Fonte das Questões:** Banco de questões de vestibulares anteriores (ENEM, etc.) de domínio público.
*   **Sustentabilidade Financeira:** Modelo "Freemium para Sempre", com o núcleo de aprendizado sempre gratuito, suportado por doações e serviços premium opcionais não-essenciais no futuro.

## 6. Roadmap com Estimativas

*   **Fase 1 (MVP de Matemática - Beta Fechado):** Desenvolvimento e lançamento para um grupo restrito de estudantes para feedback.
    *   *Estimativa de Tempo: 3-4 meses.*
*   **Fase 2 (Beta Aberto):** Lançamento público da plataforma de Matemática, com foco em estabilidade e coleta de dados de uso.
    *   *Estimativa de Tempo: 2-3 meses após a Fase 1.*
*   **Fase 3 (Expansão V1):** Iniciar desenvolvimento da próxima matéria (ex: Física) e da correção de redação por IA.
    *   *Estimativa de Tempo: Início 6 meses após o lançamento inicial.*
