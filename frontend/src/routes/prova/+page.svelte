<script lang="ts">
  import { onMount } from 'svelte';
  import type { Question } from '../../lib/types/assessment';

  let questions: Question[] = [];

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/assessment');
      if (response.ok) {
        questions = await response.json();
      } else {
        console.error('Failed to fetch questions:', response.statusText);
      }
    } catch (error) {
      console.error('An error occurred while fetching questions:', error);
    }
  });
</script>

<main>
  <h1>Prova de Nivelamento</h1>

  {#each questions as question}
    <div>
      <p>{question.text}</p>
      <textarea placeholder="Sua resposta"></textarea>
    </div>
  {/each}

  <button>Enviar Respostas</button>
</main>

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  div {
    margin-bottom: 2rem;
  }
</style>
