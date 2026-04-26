# 🚀 Griô 2.0: Pivot Estratégico de Experiência "Area-First"

Este documento serve como a **Bússola de Implementação** para a evolução do Griô. Ele detalha a transição de uma interface orientada a dados técnicos para uma jornada de aprendizado monumental, humanizada e visualmente espetacular.

---

## 🎯 1. Filosofia de Mudança: O "Filtro Humano"

### O Problema Atual
- Interface granular demais (focada em códigos de competências como `CN_C1_H1`).
- Relatórios frios e técnicos ("nível de domínio baixo", "maturidade incipiente").
- Sobrecarga de dados para a LLM (inclusão de módulos vizinhos/inferidos no diagnóstico).

### A Nova Visão
- **Foco do Aluno:** Áreas do Conhecimento (Linguagens, Natureza, Humanas, Matemática).
- **Background (Motor):** Habilidades e Competências continuam no Grafo (Neo4j), mas a UI é orientada a temas reais (ex: "Genética" em vez de "H14").
- **Pedagogia de Sucesso:** Feedback motivacional focado no que o aluno *fez*, não no que ele *não sabe* de forma genérica.

---

## 🎨 2. Design Commitment: "Liquid Glass 2.0"

Para atingir o efeito "Wow", a interface deve fugir de templates comuns (Bento Grids padrão).

- **Geometria:** Bordas ultra-afiadas (**0px - 2px**) para cards de ação, transmitindo precisão e sofisticação tech.
- **Topologia Assimétrica:** Os 4 cards de área devem flutuar com profundidade (Z-axis) e entrada escalonada (*staggered reveal*).
- **Paleta Cromática (Identidade de Área):**
  - **Matemática:** Azul Elétrico (#00D1FF) - Precisão.
  - **Natureza:** Verde Ácido (#BFFF00) - Energia.
  - **Linguagens:** Laranja Sunset (#FF4D00) - Comunicação.
  - **Humanas:** Ouro Profundo (#FFD700) - História.
  - **Fundo:** Deep Charcoal/Navy (#0A0A0B) para contraste máximo.
- **Micro-interações:**
  - **Hover Aura:** Ao passar o mouse, o card emite uma aura na cor da área que ilumina os elementos adjacentes.
  - **Orbes de Proficiência:** Elementos orgânicos dentro dos cards que pulsam conforme o domínio do aluno.

---

## 🧪 3. Fluxo de Diagnóstico e Progresso

### A. Diagnóstico por Área (Endpoint-driven)
- **Seleção de Questões:** 20 questões por área, seguindo os **pesos históricos do ENEM** para cada competência.
- **Context Hygiene (P0):** O payload enviado para a LLM deve conter **apenas** o que o aluno respondeu. **Proibido** enviar módulos vizinhos ou inferidos para o contexto de chat do diagnóstico.

### B. Métrica de Dashboard (Misto)
- **Macro:** Domínio percentual da Área.
- **Ação:** Card de "Próximo Passo" que converte a lacuna técnica em uma missão prática e amigável.

---

## 🧠 4. Camada de Tradução e Tom de Voz

### Tradução Técnica (Middleware)
A IA de implementação deve garantir que siglas técnicas sejam traduzidas antes de chegarem à UI ou à LLM:
- **Lookup Table:** `CN_C1_H1` ➔ "Fenômenos Ondulatórios".
- **Regra:** Nunca mencionar códigos alfa-numéricos para o aluno.

### Tom de Voz do Mentor Socrático
- Substituir termos clínicos por termos de crescimento.
- Ex: *"Seu desempenho é baixo"* ➔ *"Este é o seu ponto de partida em Natureza. Temos uma grande oportunidade de crescer em Fenômenos Físicos!"*

---

## 🛠 5. Guia de Implementação (Para a IA Futura)

| Componente | Requisito Técnico | Impacto de UX |
| :--- | :--- | :--- |
| **LLM Context** | Filtrar `proficiencies` removendo `is_inferred: true` antes do resumo. | Evita alucinações e mantém foco na experiência real. |
| **Motion** | Usar `framer-motion` com `layoutId` para transições de "explosão" de cards. | Efeito monumental e fluido. |
| **Data Logic** | Criar endpoint `/api/diagnostico/[area]` com lógica de pesos ENEM. | Fidelidade máxima ao exame real. |
| **Deep Dive** | Esconder dados granulares em uma aba secundária (ex: "Dados Técnicos" no Perfil). | Mantém a UI principal limpa e menos ansiosa. |


---
*Documento gerado para guiar o Pivot Estratégico 2026.*
