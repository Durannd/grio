<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import type { Question } from '../../lib/types/assessment';

  let questions: Question[] = [];
  let loading = true;
  let submitting = false;
  let answers: Record<string, string> = {};

  onMount(async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        goto("/login");
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/assessment', {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        goto("/login");
        return;
      }

      if (response.ok) {
        const data = await response.json();
        questions = data.questions;
      } else {
        console.error('Failed to fetch questions:', response.statusText);
      }
      loading = false;
    } catch (error) {
      console.error('An error occurred while fetching questions:', error);
      loading = false;
    }
  });

  async function handleSubmit() {
    submitting = true;
    // Mocking submission
    setTimeout(() => {
      submitting = false;
      goto('/dashboard');
    }, 2000);
  }
</script>

<div class="assessment-container">
  {#if loading}
    <div class="loading-state animate-slide-up">
      <div class="spinner"></div>
      <p>Preparando os pergaminhos do conhecimento...</p>
    </div>
  {:else}
    <header class="assessment-header animate-slide-up stagger-1">
      <h1 class="text-gradient">O Rito de Passagem</h1>
      <p>Responda com honestidade. Isso moldará a sua jornada.</p>
    </header>

    <form on:submit|preventDefault={handleSubmit} class="assessment-form">
      {#each questions as question, index}
        <div class="glass-card question-card animate-slide-up" style="animation-delay: {0.1 * (index + 2)}s">
          <div class="question-header">
            <span class="question-number">Enigma {index + 1}</span>
            <span class="question-topic">{question.concept_name}</span>
          </div>
          <h2 class="question-text">{question.text}</h2>
          
          <div class="form-group">
            <label for="answer-{question.id}" class="sr-only">Sua Resposta</label>
            <textarea 
              id="answer-{question.id}" 
              placeholder="Descreva seu raciocínio aqui..." 
              bind:value={answers[question.id]}
              required
            ></textarea>
          </div>
        </div>
      {/each}

      <div class="submit-wrapper animate-slide-up" style="animation-delay: {0.1 * (questions.length + 3)}s">
        <button type="submit" class="btn btn-primary btn-large" disabled={submitting}>
          {#if submitting}
            <span class="spinner-small"></span>
            Avaliando...
          {:else}
            Selar Meu Destino
          {/if}
        </button>
      </div>
    </form>
  {/if}
</div>

<style>
  .assessment-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 4rem 2rem 6rem;
  }

  .loading-state {
    text-align: center;
    padding: 8rem 0;
    color: var(--primary);
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 3px solid rgba(201, 160, 94, 0.2);
    border-top-color: var(--primary);
    border-radius: 50%;
    margin: 0 auto 1.5rem;
    animation: spin 1s linear infinite;
  }

  .spinner-small {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid rgba(0, 0, 0, 0.2);
    border-top-color: #000;
    border-radius: 50%;
    margin-right: 0.5rem;
    animation: spin 1s linear infinite;
  }

  @keyframes spin { 100% { transform: rotate(360deg); } }

  .assessment-header {
    text-align: center;
    margin-bottom: 4rem;
  }

  .assessment-header h1 {
    font-size: clamp(2.5rem, 5vw, 4rem);
    margin-bottom: 0.5rem;
  }

  .assessment-header p {
    color: var(--text-secondary);
    font-size: 1.2rem;
  }

  .assessment-form {
    display: flex;
    flex-direction: column;
    gap: 3rem;
  }

  .question-card {
    padding: 3rem;
  }

  .question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(250, 250, 250, 0.1);
    padding-bottom: 1rem;
  }

  .question-number {
    font-family: var(--font-serif);
    color: var(--primary);
    font-size: 1.2rem;
    font-weight: 600;
  }

  .question-topic {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    background: rgba(0,0,0,0.4);
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-full);
  }

  .question-text {
    font-size: 1.4rem;
    line-height: 1.6;
    margin-bottom: 2rem;
    font-family: var(--font-sans);
    font-weight: 400;
  }

  textarea {
    width: 100%;
    min-height: 150px;
    padding: 1.25rem;
    border-radius: var(--radius-md);
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(250, 250, 250, 0.1);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 1rem;
    line-height: 1.6;
    resize: vertical;
    transition: all var(--transition-fast);
  }

  textarea:focus {
    outline: none;
    border-color: var(--primary);
    background: rgba(0, 0, 0, 0.5);
    box-shadow: 0 0 0 2px rgba(201, 160, 94, 0.2);
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }

  .submit-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
  }

  .btn-large {
    font-size: 1.2rem;
    padding: 1.25rem 4rem;
  }

  @media (max-width: 768px) {
    .question-card {
      padding: 2rem 1.5rem;
    }
  }
</style>
