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

---

## 📈 Próximos Passos (Backlog de Maturidade)

### Fase B: Expansão de Base
- [ ] **Ingestão em Larga Escala**: Scripts para importar Natureza e Humanas (ENEM 2020-2024).
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
