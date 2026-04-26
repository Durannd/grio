# 📜 Griô Evolution Plan (Documento Vivo)

Este documento registra a evolução do projeto, decisões estratégicas e o status de implementação de novas features para evitar regressões e manter o alinhamento pedagógico/tecnológico.

---

## 🎯 Visão Atualizada (MVP Multi-disciplinar)
O Griô evoluiu de um MVP de Matemática para uma plataforma multi-disciplinar (Linguagens, Humanas, Natureza e Matemática), utilizando IA de ponta para criar um ciclo de aprendizado adaptativo baseado em dados reais do ENEM.

---

## 🛠 Conquistas da Sessão (25/04/2026)

### 1. Segurança de Elite (Auth)
- **Implementado**: Migração total de localStorage para **HttpOnly Cookies**.
- **Segurança**: Proteção contra XSS ativa e flags de segurança dinâmicas (`Secure` em produção).
- **Status**: ✅ Concluído.

### 2. Módulo de Estudo RAG (P0)
- **O que é**: Micro-aulas baseadas em **exemplos reais do ENEM**.
- **Lógica**: O sistema injeta 10 questões da Habilidade no prompt do Gemini para garantir fidelidade técnica.
- **Cache**: Conteúdo persistido no Neo4j com validade de 5 anos.
- **Status**: ✅ Concluído.

### 3. Micro-Simulado Direcionado (Prática)
- **O que é**: O ciclo se fecha com uma mini-prova de até 10 questões específicas da Skill estudada.
- **Integração**: Resultados alimentam a rede neural de proficiência no Grafo e são auditados por IA (detecção de chutes).
- **Status**: ✅ Concluído.

### 4. Gamificação do Hábito (Streaks)
- **O que é**: Sistema de consistência diária (Streaks) visível no Dashboard.
- **Mecânica**: Recompensa o aluno por diagnósticos ou estudos diários.
- **Status**: ✅ Concluído.

### 5. Auditoria & UX
- **Feedback**: Sistema de **Toasts** sutil para alertas pedagógicos e sistêmicos.
- **Tom de IA**: Prompts 100% neutralizados e profissionalizados (sem personas ou informalidades).
- **Status**: ✅ Concluído.

### 6. Diagnóstico Equilibrado (Top-Down)
- **O que é**: Algoritmo de seleção de questões que força a diversidade por **Área do Conhecimento**.
- **Mecânica**: Seleciona até 4 questões de competências diferentes para cada uma das 4 áreas (Mat, Nat, Hum, Lin).
- **Status**: ✅ Concluído.

### 7. Visibilidade Total de Lacunas (0%)
- **O que é**: Fim da supressão de habilidades com score zerado no pipeline de dados.
- **Impacto**: O Gemini agora prioriza "buracos negros" de conhecimento no Plano de Estudos e o Dashboard exibe barras vermelhas (0%) para incentivar a recuperação imediata.
- **Status**: ✅ Concluído.

### 8. Proficiência Inferida (Grafo Transparente)
- **O que é**: Distinção técnica entre proficiência real (questão feita) e inferida (propagada por proximidade).
- **Mecânica**: Adição da flag `is_inferred` no Neo4j e UI dedicada no Dashboard ("Selos de Potencial").
- **Impacto**: Elimina falsos negativos no dashboard e permite que a IA diferencie "Oportunidade" de "Deficiência".
- **Status**: ✅ Concluído.

---

### Fase Pivot: Experiência Area-First (Griô 2.0)
- [x] **Interface Monumental**: Implementar os 4 cards de Área com estética Liquid Glass 2.0 e isolamento de Dados Técnicos em rota de Perfil.
- [x] **Tradução Pedagógica**: Criar camada de tradução em memória para eliminar siglas técnicas (ex: CN_C1_H1) da visão do aluno e da LLM.
- [x] **Filtro de Contexto LLM**: Refatorar payload do diagnóstico para enviar apenas interações reais, ocultando dados inferidos (Context Hygiene e Mentor Socrático robusto).
- [x] **Refinamento de UI/UX (V1-V4)**: Layout "Warm Earthy Elegance" erradicado, grids responsivos implementados e fluxo de navegação unificado por Área.

### Fase B: Expansão de Base
- [ ] **Simulados Customizados**: Gerar provas baseadas apenas nas "feridas" (lacunas) transversais do aluno.

### Fase C: Refinamento Pedagógico
- [ ] **Explicação Pós-Prática**: Integrar o Mentor Socrático para explicar as questões erradas no Micro-Simulado.
- [ ] **Modo Offline (PWA)**: Implementar service workers para estudo em trânsito com dados limitados.

---

## 🛡 Verificações de Integridade
- [x] Autenticação via HttpOnly Cookies.
- [x] Suíte de testes backend (5/5 passando).
- [x] Validação de carga de tokens (Sumário Técnico de Questões).
- [x] Lógica de atualização de Streaks validada.
