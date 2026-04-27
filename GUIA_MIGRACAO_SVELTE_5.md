# Guia de Migração Estratégica: Projeto Griô para Svelte 5

## 1. Introdução e Filosofia

Este documento serve como um guia mestre para a migração do frontend do Projeto Griô para o Svelte 5. O objetivo principal é resolver vulnerabilidades de segurança críticas, modernizar a base de código e posicionar o projeto para o futuro, mantendo a estabilidade como prioridade máxima.

**Para a IA implementadora:** Este não é um script para ser seguido cegamente. É um mapa estratégico. A sua principal diretiva é **segurança e incrementalismo**. Cada passo deve ser pequeno, verificável e reversível. A fonte da verdade final para sintaxe e padrões de código deve ser sempre a **documentação oficial do Svelte 5**. Em caso de ambiguidade, questione e peça clarificação antes de prosseguir com uma suposição.

---

## 2. Fase de Preparação: O Alicerce da Segurança

Antes de alterar qualquer linha de código da aplicação, as seguintes etapas são mandatórias:

**a. Isolamento Total com Git:**
- **Ação:** Crie um novo branch a partir da `main` para todo o trabalho de migração.
- **Sugestão de Nome:** `feature/svelte-5-migration`
- **Justificativa:** Isso garante que a versão estável do projeto permaneça intocada. Podemos experimentar livremente neste branch e, se algo der catastroficamente errado, podemos descartá-lo sem perdas.

**b. Estudo e "Internalização" dos Conceitos do Svelte 5:**
- **Ação:** Antes de codificar, revise os conceitos fundamentais do Svelte 5, com foco especial nas **Runes**.
- **Recursos Chave:**
    - [Blog de Anúncio do Svelte 5](https://svelte.dev/blog/runes)
    - [Documentação Oficial sobre Runes](https://svelte.dev/docs/runes)
    - [Guia Oficial de Migração (se disponível)]
- **Justificativa:** A IA precisa entender a *lógica* por trás das "Runes" (`$state`, `$derived`, `$effect`) para traduzir os padrões do Svelte 4 (`let`, `$:`, `onMount`) de forma idiomática, e não apenas fazer uma substituição mecânica de sintaxe.

**c. Definição de um "Smoke Test" Manual:**
- **Ação:** Crie uma checklist de testes manuais rápidos para verificar as funcionalidades críticas após cada mudança.
- **Sugestão de Checklist para o Griô:**
    - [ ] A página inicial carrega sem erros no console?
    - [ ] O formulário de login funciona?
    - [ ] O formulário de cadastro funciona?
    - [ ] Após o login, o dashboard carrega os dados do usuário corretamente?
    - [ ] O dropdown do perfil no header abre, fecha e os links funcionam?
    - [ ] É possível iniciar e submeter uma "prova" (diagnóstico)?
    - [ ] A página de resultado da prova carrega?
- **Justificativa:** Como o projeto não possui um conjunto de testes automatizados, esta checklist é nossa rede de segurança para detectar quebras de funcionalidade o mais cedo possível.

---

## 3. Fase de Migração: Passos Incrementais e Atômicos

A migração deve ser feita em etapas lógicas, com verificação constante. **Não tente atualizar tudo de uma vez.**

**Passo 1: Atualizar Apenas a Dependência do Svelte**
- **Ação:** No `package.json`, atualize apenas a versão do `svelte`.
- **Comando Sugerido:** `npm install svelte@latest`
- **Verificação:** Após a instalação, rode `npm run dev`. É esperado que a aplicação quebre. O objetivo deste passo é apenas atualizar o pacote isoladamente.

**Passo 2: Refatoração Gradual para Runes (Componente por Componente)**
- **Ação:** Comece a refatorar os componentes `.svelte` para usar Runes. A sugestão é começar pelos mais simples e ir para os mais complexos.
- **Ordem Sugerida:**
    1. `LoadingSpinner.svelte` (mais simples)
    2. `LoginForm.svelte`, `CadastroForm.svelte`
    3. Componentes de página (`+page.svelte`), começando pelos mais simples (ex: `/login`) e indo para os mais complexos (ex: `/prova`).
    4. O layout principal: `+layout.svelte`.
- **Padrões de Tradução (Sugestões Profundas):**
    - **Props:** `export let prop;` torna-se `let { prop } = $props();`.
    - **Estado Reativo:** `let count = 0;` torna-se `let count = $state(0);`.
    - **Computações Derivadas:** `$: doubled = count * 2;` torna-se `let doubled = $derived(count * 2);`.
    - **Efeitos Colaterais (Side Effects):** `onMount(async () => { ... });` ou `$: if (prop) { ... }` geralmente se traduzem para `$effect(() => { ... });`. **Cuidado:** `$effect` roda imediatamente e sempre que suas dependências mudam. Para código que *só* deve rodar uma vez na montagem, o uso de `onMount` ainda pode ser apropriado. Analise a intenção do código original.

**Passo 3: Atualizar o SvelteKit e o Vite**
- **Ação:** Depois que a maioria dos componentes estiver refatorada, atualize o meta-framework e o build tool.
- **Comando Sugerido:** `npm install @sveltejs/kit@latest vite@latest @sveltejs/vite-plugin-svelte@latest`
- **Verificação:** Este é um ponto crítico. Após esta atualização, rode `npm run dev` e execute a checklist de "smoke test" completa. Corrija quaisquer problemas de build ou de configuração que surgirem.

**Passo 4: Commits Atômicos e Verificação Constante**
- **Diretiva para a IA:** Após refatorar CADA componente (ou um pequeno grupo de componentes relacionados) com sucesso, **faça um commit**.
- **Formato de Mensagem Sugerido:** `refactor(Componente): migra para runes do Svelte 5`
- **Ação Obrigatória após cada commit:** Rode `npm run dev` e faça um "smoke test" rápido.
- **Justificativa:** Commits pequenos e frequentes permitem usar `git bisect` ou `git revert` para encontrar a origem de um bug de forma trivial. É a nossa ferramenta mais poderosa contra regressões.

---

## 4. Fase Final: Limpeza e Validação

**a. Validação Final da Auditoria:**
- **Ação:** Com a migração concluída e a aplicação estável, rode `npm audit` novamente.
- **Objetivo:** O resultado deve ser "0 vulnerabilities". Se alguma vulnerabilidade persistir, investigue e corrija.

**b. Revisão de Código Legado:**
- **Ação:** Procure por quaisquer padrões do Svelte 4 que possam ter sido esquecidos. Garanta que a base de código esteja consistente com os padrões do Svelte 5.

**c. Formatação de Código:**
- **Ação:** Rode o formatador de código (ex: Prettier) em todo o projeto para garantir consistência estilística.

Este guia fornece uma estrutura para uma migração segura e eficaz. A chave para o sucesso é a disciplina de seguir os passos de forma incremental, com verificação constante e commits atômicos.
