<script lang="ts">
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { api } from "$lib/api";
  import LoadingSpinner from "$lib/components/LoadingSpinner.svelte";
  import { toasts } from "$lib/stores/toast";

  interface Option {
    id: number;
    text: string;
  }

  interface Question {
    id: string;
    text: string;
    difficulty: string;
    concept_name: string;
    options: Option[];
  }

  let skill_id = $page.params.id;
  let friendly_name = "";
  let questions: Question[] = [];
  let currentQuestionIndex = 0;
  let loading = true;
  let submitting = false;
  let selectedAnswers: Record<string, number> = {};
  let answersTime: Record<string, number> = {};
  let startTime = Date.now();
  let progress = 0;

  onMount(async () => {
    try {
      const data = await api.get(`/assessment/practice/${skill_id}`);
      questions = data.questions;
      friendly_name = data.friendly_name;

      if (questions.length === 0) {
          toasts.info("Você já resolveu todas as questões disponíveis para este conceito no momento!");
          goto("/dashboard");
          return;
      }
    } catch (error) {
      // O serviço de API já exibe o toast de erro
    } finally {
      loading = false;
    }
  });

  $: currentQuestion = questions[currentQuestionIndex];
  $: progress =
    questions.length > 0
      ? ((currentQuestionIndex + 1) / questions.length) * 100
      : 0;

  function selectOption(questionId: string, optionId: number) {
    const timeSpent = (Date.now() - startTime) / 1000;
    selectedAnswers[questionId] = optionId;
    answersTime[questionId] = (answersTime[questionId] || 0) + timeSpent;
    startTime = Date.now();
  }

  function nextQuestion() {
    if (currentQuestionIndex < questions.length - 1) {
      currentQuestionIndex++;
      startTime = Date.now();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      handleSubmit();
    }
  }

  function prevQuestion() {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  function formatEnemId(id: string) {
    if (!id) return "";
    const [year, num] = id.split("_");
    return `ENEM ${year} • Questão ${num}`;
  }

  async function handleSubmit() {
    submitting = true;
    try {
      const payload = {
        user_id: 0, // O backend substituirá pelo ID do token
        type: "pratica_direcionada",
        answers: Object.entries(selectedAnswers).map(([qId, aId]) => ({
          question_id: qId,
          selected_option_id: aId,
          time_seconds: Math.round(answersTime[qId] || 0),
        })),
      };

      const response = await api.post("/assessment/submit", payload);

      const attemptId = response.attempt_id;
      const audit = response.audit_summary;

      if (audit && audit.has_warnings) {
        toasts.warning(
          "O padrão de respostas foi muito acelerado. Dedique mais tempo à leitura técnica nas próximas sessões!",
          8000
        );
      }

      goto(`/prova/resultado?id=${attemptId}`);
    } catch (e) {
      goto("/dashboard");
    } finally {
      submitting = false;
    }
  }
</script>

{#if submitting}
  <div class="status-screen" in:fade>
    <LoadingSpinner />
    <h2>Consolidando seu aprendizado...</h2>
    <p>Estamos atualizando seu mapa de proficiência com base nos seus novos resultados.</p>
  </div>
{:else}
  <div class="onboarding-page">
    <div class="background-decor">
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
    </div>

    <div class="content-wrapper">
      {#if loading}
        <div class="loading-container" in:fade>
          <LoadingSpinner />
          <p class="text-gradient">Preparando seu simulado direcionado...</p>
        </div>
      {:else if questions.length > 0}
        <header class="onboarding-header" in:fly={{ y: -20, duration: 600 }}>
          <h1 class="text-gradient">Prática de Habilidade</h1>
          <p class="subtitle">
            Validando seu domínio sobre: <br/>
            <span class="skill-focus">{friendly_name}</span>
          </p>

          <div class="progress-wrapper">
            <div class="progress-bar">
              <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <span class="progress-text"
              >Questão {currentQuestionIndex + 1} de {questions.length}</span
            >
          </div>
        </header>

        <main class="question-section">
          {#key currentQuestionIndex}
            <div
              class="glass-card question-card"
              in:fly={{ x: 30, duration: 500 }}
              out:fly={{ x: -30, duration: 300 }}
            >
              <div class="card-meta">
                <div class="meta-left">
                  <span class="enem-badge"
                    >{formatEnemId(currentQuestion.id)}</span
                  >
                  <span class="concept-tag">Foco: {skill_id}</span>
                </div>
                <div class="difficulty-badge">
                  <span class="dot {currentQuestion.difficulty.toLowerCase()}"
                  ></span>
                  <span>{currentQuestion.difficulty}</span>
                </div>
              </div>

              <div class="question-body">
                <div class="question-text">{@html currentQuestion.text}</div>
              </div>

              <div class="options-container">
                {#each currentQuestion.options as option}
                  <button
                    class="option-item"
                    class:selected={selectedAnswers[currentQuestion.id] ===
                      option.id}
                    on:click={() => selectOption(currentQuestion.id, option.id)}
                  >
                    <div class="option-marker">
                      {String.fromCharCode(64 + option.id)}
                    </div>
                    <div class="option-content">{@html option.text}</div>
                  </button>
                {/each}
              </div>
            </div>
          {/key}
        </main>

        <footer class="onboarding-footer">
          <button
            class="btn btn-outline"
            on:click={prevQuestion}
            disabled={currentQuestionIndex === 0}
          >
            Anterior
          </button>

          {#if currentQuestionIndex === questions.length - 1}
            <button 
              class="btn btn-primary" 
              on:click={handleSubmit} 
              disabled={!selectedAnswers[currentQuestion.id] || submitting}
            >
              Finalizar Prática
            </button>
          {:else}
            <button
              class="btn btn-primary"
              on:click={nextQuestion}
              disabled={!selectedAnswers[currentQuestion.id]}
            >
              Próxima Questão
            </button>
          {/if}
        </footer>
      {/if}
    </div>
  </div>
{/if}

<style>
  .onboarding-page {
    min-height: 100vh;
    background: var(--bg-primary);
    color: var(--text-primary);
    position: relative;
    padding: 2rem 1rem 6rem;
    display: flex;
    justify-content: center;
  }

  .background-decor {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
  }

  .glow {
    position: absolute;
    width: 40vw;
    height: 40vw;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.1;
  }

  .glow-1 { top: -10%; right: -10%; background: var(--primary); }
  .glow-2 { bottom: -10%; left: -10%; background: var(--primary-dark); }

  .content-wrapper {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 850px;
    display: flex;
    flex-direction: column;
    gap: 3rem;
  }

  .onboarding-header { text-align: center; margin-top: 2rem; }
  .onboarding-header h1 { margin-bottom: 0.5rem; font-size: clamp(2rem, 5vw, 3.5rem); }

  .skill-focus {
    color: var(--primary-light);
    font-family: monospace;
    font-weight: 700;
    background: rgba(201, 160, 94, 0.1);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
  }

  .subtitle { color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 2.5rem; }

  .progress-wrapper { max-width: 300px; margin: 0 auto; }
  .progress-bar { height: 4px; background: rgba(255, 255, 255, 0.05); border-radius: 2px; margin-bottom: 0.75rem; overflow: hidden; }
  .progress-fill { height: 100%; background: var(--primary); box-shadow: 0 0 10px var(--primary); transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
  .progress-text { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-secondary); font-weight: 600; }

  .question-card { padding: 3.5rem; border-radius: 2rem; display: flex; flex-direction: column; gap: 2rem; }
  .card-meta { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 1.5rem; }
  .meta-left { display: flex; align-items: center; gap: 1.5rem; }
  .enem-badge { font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); opacity: 0.7; border-right: 1px solid rgba(255, 255, 255, 0.1); padding-right: 1.5rem; }
  .concept-tag { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; color: var(--primary); background: rgba(201, 160, 94, 0.1); padding: 0.35rem 1rem; border-radius: 2rem; }
  .difficulty-badge { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: var(--text-secondary); }
  .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot.fácil { background: var(--success); }
  .dot.médio { background: var(--warning); }
  .dot.difícil { background: var(--danger); }

  .question-text { font-size: 1.4rem; line-height: 1.7; color: var(--text-primary); }
  .options-container { display: grid; gap: 1rem; }

  .option-item {
    display: flex; align-items: flex-start; gap: 1.25rem; padding: 1.5rem;
    background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 1.25rem; cursor: pointer; text-align: left; transition: all 0.2s ease;
    width: 100%; color: var(--text-primary);
  }

  .option-item:hover { background: rgba(255, 255, 255, 0.04); border-color: rgba(201, 160, 94, 0.3); }
  .option-item.selected { background: rgba(201, 160, 94, 0.08); border-color: var(--primary); box-shadow: 0 0 20px rgba(201, 160, 94, 0.1); }

  .option-marker {
    width: 36px; height: 36px; flex-shrink: 0; background: rgba(255, 255, 255, 0.05);
    border-radius: 0.75rem; display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.9rem; color: var(--text-secondary);
  }

  .option-item.selected .option-marker { background: var(--primary); color: var(--text-dark); }
  .option-content { font-size: 1rem; line-height: 1.5; font-weight: 400; }

  .onboarding-footer { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0 4rem; }
  .loading-container { padding: 10rem 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2rem; }

  .status-screen { height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2rem; }
  .status-screen h2 { font-size: 2rem; margin-bottom: 1rem; color: #fff; }
  .status-screen p { color: var(--text-secondary); }

  @media (max-width: 768px) {
    .question-card { padding: 2rem 1.5rem; }
    .question-text { font-size: 1.2rem; }
    .onboarding-page { padding-top: 1rem; }
  }
</style>
