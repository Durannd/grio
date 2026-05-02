

# Plano de Validação Científica e Eficácia – Griô MVP

## 1. Objetivo da Pesquisa
Comprovar, por meio de dados quantitativos e qualitativos, que a utilização de um Banco de Dados em Grafo (Neo4j) integrado à Inteligência Artificial atua de forma mais eficaz no diagnóstico e remediação de lacunas de aprendizado (modelo "Area-First") em comparação com a progressão linear tradicional de ensino.

## 2. Hipóteses Científicas
Para validar o projeto perante a banca avaliadora, o MVP testará duas hipóteses centrais:
*   **H1 (Eficácia do Grafo):** A identificação e remediação de "pré-requisitos fantasmas" através de travessia de grafos reduz a reincidência de erros em eixos cognitivos interdependentes.
*   **H2 (Engajamento Baseado em Hábito):** A fragmentação do estudo em micro-lições dinâmicas (gamificação visual do grafo) gera maior consistência diária de acessos em comparação com o modelo de aulas longas e estáticas.



## 3. Arquitetura de Telemetria (Como medir sem gargalar o app)
Para não prejudicar a performance mobile do SvelteKit nem o event loop do FastAPI, a coleta de dados será assíncrona. 

**Fluxo Técnico:**
1. O SvelteKit dispara eventos em _background_ para o endpoint `POST /v1/telemetry`.
2. O FastAPI recebe o payload e despacha para uma _Background Task_ (ou fila Redis).
3. Os dados são gravados em uma tabela simples e "flat" no PostgreSQL (`telemetry_events`), isolando a carga analítica do banco transacional e do Neo4j.

**Estrutura do Payload (JSON de Telemetria):**
```json
{
  "student_id": "uuid",
  "timestamp": "2026-05-10T14:30:00Z",
  "event_type": "DIAGNOSTIC_ACCEPTED",
  "metadata": {
    "failed_question_id": "q_123",
    "root_cause_concept_id": "math_rule_of_three",
    "current_mastery": 0.40
  }
}
```

## 4. Métricas Core de Eficácia Pedagógica (A "Ciência")

Para provar a **H1**, as seguintes métricas serão extraídas e plotadas no relatório final:

### 4.1. Taxa de Sucesso Pós-Remediação (TSPR)
A métrica mais importante do artigo. Mede se a intervenção do grafo realmente ensinou o aluno.
*   **Como calcular:**
    $$ TSPR = \left( \frac{\text{Acertos em questões do tipo } X \text{ após a micro-lição do conceito raiz } Y}{\text{Total de tentativas do tipo } X \text{ após intervenção}} \right) \times 100 $$
*   **O que prova:** Se o aluno erra Estequiometria, faz a micro-lição de Regra de Três sugerida pelo sistema, e depois volta a acertar Estequiometria, provamos matematicamente que o motor de diagnóstico funciona.

### 4.2. Delta de Proficiência ($\Delta M$)
Mede a velocidade de consolidação do conhecimento no grafo.
*   **Como calcular:** 
    $$ \Delta M = M_{final} - M_{inicial} $$
    *(Onde $M$ representa o Mastery Score, de 0.0 a 1.0, do nó conceitual no Neo4j, analisado em uma janela de 15 dias).*
*   **O que prova:** Valida que a navegação orientada a fenômenos e eixos cognitivos faz a árvore de habilidades do aluno "acender" de forma sustentável e interconectada.



## 5. Métricas de Engajamento e Produto (A "Tração")

Para provar a **H2**, utilizaremos dados de usabilidade:

### 5.1. Taxa de Aceitação do Diagnóstico (Opt-in Rate)
*   **O que é:** Percentual de vezes que o aluno clica em "Revisar Conceito Raiz" versus "Ignorar e ver a resolução da questão atual".
*   **O que prova:** Valida o valor percebido da interface (SvelteKit) e da abordagem socrática. Se o número for baixo, a interface precisa ser mais persuasiva; se for alto, os alunos confiam na inteligência do Griô.

### 5.2. Consistência de Hábito (Streaks) via Redis
*   **O que é:** Registro de dias consecutivos logados consumindo pelo menos um nó de conteúdo. Gerenciado via Redis Bitmaps (ex: `SETBIT student:123:streak 10 1`).
*   **O que prova:** Demonstra que o sistema "Habit over Intensity" é eficaz para manter o engajamento contínuo em estudantes do ensino médio.

## 6. Coleta de Dados Qualitativos (O Refino da IA)
O artigo acadêmico exige uma análise de impacto e percepção do usuário[cite: 2].
*   **Micro-NPS de Interação Socrática:** Após a IA (Gemini) explicar uma dúvida, capturar feedback binário (`Polegar Cima/Baixo`). 
*   **Entrevistas de Saída (Final de Junho):** Selecionar os 5 alunos mais engajados e os 5 menos engajados do grupo beta para entrevistas de 15 minutos, buscando entender o aspecto emocional (frustração vs. sensação de evolução) durante o uso da plataforma.

## 7. Cronograma de Execução Científica

*   **Maio (Semanas 1-2):** Lançamento do MVP (Matemática). Foco na estabilidade do banco de dados (Neo4j) e na garantia de que a tabela `telemetry_events` está gravando perfeitamente.
*   **Maio (Semanas 3-4):** Operação "Mãos Livres". Deixar os alunos usarem a plataforma livremente para acumular massa de dados orgânica.
*   **Junho (Semanas 1-3):** Extração SQL da telemetria e cálculos iniciais de TSPR e $\Delta M$. Início da redação do trabalho científico de 5 a 15 páginas exigido pelo edital[cite: 2].
*   **Junho (Semana 4):** Realização das entrevistas qualitativas e cruzamento com os dados dos gráficos.
*   **Julho:** Revisão final da pesquisa, formatação nas normas exigidas e submissão na plataforma do CNPq antes do prazo de encerramento[cite: 2].