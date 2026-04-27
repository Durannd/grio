<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { fade } from 'svelte/transition';
  import snarkdown from 'snarkdown';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { formatPedagogicalCode } from '$lib/utils';
  import { api } from '$lib/api';

  let skill_id = $page.params.id;
  let microlesson: {
    skill_id: string,
    friendly_name: string,
    content: string,
    description: string,
    area: string
  } | null = null;
  let loading = true;
  let error = "";

  onMount(async () => {
    try {
      const response = await api.get(`/study/${skill_id}`);
      if (response) {
        microlesson = response;
      } else {
        error = "Lição não encontrada para este conceito.";
      }
    } catch (e: any) {
      if (e.message.includes('404')) {
        error = "Lição não encontrada para este conceito.";
      } else {
        error = e.message || "Ocorreu um erro ao carregar a lição.";
      }
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>Grio - Estudar {microlesson ? formatPedagogicalCode(microlesson.skill_id) : skill_id}</title>
</svelte:head>

<div class="study-container container">
  <div class="header-nav animate-slide-up stagger-1">
    <a href="/area/{skill_id.substring(0, 2)}" class="btn btn-outline">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;"><path d="m15 18-6-6 6-6"/></svg>
      Voltar para Área
    </a>
  </div>

  {#if loading}
    <div class="status-screen" out:fade>
      <LoadingSpinner />
      <p>Buscando sua lição personalizada...</p>
    </div>
  {:else if error}
    <div class="status-screen error-state animate-slide-up">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </div>
      <h2>Ops! Algo deu errado</h2>
      <p>{error}</p>
      <a href="/dashboard" class="btn btn-primary mt-6">Voltar ao Início</a>
    </div>
  {:else if microlesson}
    <article class="lesson-content animate-slide-up stagger-2">
      <header class="lesson-header glass-panel mb-8">
        <div class="area-badge">{microlesson.area}</div>
        <h1>{formatPedagogicalCode(microlesson.skill_id)}</h1>
        <p class="description">{microlesson.description}</p>
      </header>

      <div class="markdown-body glass-panel">
        <h1>{microlesson.friendly_name}</h1>
        {@html snarkdown(microlesson.content)}
      </div>

      <footer class="lesson-footer mt-12 animate-slide-up stagger-3">
        <div class="glass-panel completion-card">
          <h3>Pronto para praticar?</h3>
          <p>Agora que você revisou este conceito, que tal testar seus conhecimentos com um micro-simulado direcionado?</p>
          <div class="actions mt-6">
            <a href="/praticar/{microlesson.skill_id}" class="btn btn-primary">Praticar Agora</a>
            <a href="/area/{skill_id.substring(0, 2)}" class="btn btn-outline ml-4">Voltar para Área</a>
          </div>
        </div>
      </footer>
    </article>
  {/if}
</div>

<style>
  .study-container {
    padding-top: 3rem;
    padding-bottom: 6rem;
    max-width: 900px;
  }

  .header-nav {
    margin-bottom: 2.5rem;
  }

  .btn-sm {
    padding: 0.6rem 1.25rem;
    font-size: 0.85rem;
  }

  /* Status Screens */
  .status-screen {
    height: 50vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .loader-visual {
    position: relative;
    width: 60px;
    height: 60px;
    margin-bottom: 2rem;
  }

  .orbit {
    position: absolute;
    inset: 0;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    border-top-color: #FFF;
    animation: spin 1.5s linear infinite;
  }

  .center-glow {
    position: absolute;
    inset: 30%;
    background: #FFF;
    filter: blur(10px);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes spin { 100% { transform: rotate(360deg); } }
  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

  .error-state h2 {
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
  }
  
  .error-state p {
    color: var(--text-secondary);
  }

  /* Lesson Layout */
  .lesson-header {
    padding: 3rem;
    text-align: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .area-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #FFF;
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.5rem;
  }

  .description {
    font-size: 1.15rem;
    color: var(--text-secondary);
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.6;
  }

  .markdown-body {
    padding: 3.5rem;
    line-height: 1.8;
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.9);
  }

  /* Markdown specific styling */
  .markdown-body :global(h2) {
    margin-top: 2.5rem;
    margin-bottom: 1.25rem;
    color: var(--primary-light);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 0.5rem;
  }

  .markdown-body :global(h3) {
    margin-top: 2rem;
    color: var(--text-primary);
  }

  .markdown-body :global(p) {
    margin-bottom: 1.5rem;
  }

  .markdown-body :global(ul), .markdown-body :global(ol) {
    margin-bottom: 1.5rem;
    padding-left: 1.5rem;
  }

  .markdown-body :global(li) {
    margin-bottom: 0.5rem;
  }

  .markdown-body :global(code) {
    background: rgba(0, 0, 0, 0.3);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9em;
    color: var(--primary-light);
  }

  .markdown-body :global(blockquote) {
    border-left: 4px solid var(--primary);
    background: rgba(255, 255, 255, 0.05);
    padding: 1.5rem 2rem;
    margin: 2rem 0;
    font-style: italic;
    color: var(--text-secondary);
    border-radius: 0 8px 8px 0;
  }

  .markdown-body :global(strong) {
    color: var(--primary-light);
    font-weight: 600;
  }

  /* Completion Card */
  .completion-card {
    text-align: center;
    padding: 3rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.02), rgba(0,0,0,0.4));
  }

  .completion-card h3 {
    font-size: 1.75rem;
    margin-bottom: 0.75rem;
  }

  .completion-card p {
    color: var(--text-secondary);
    max-width: 500px;
    margin: 0 auto;
  }

  .mt-6 { margin-top: 1.5rem; }
  .mt-12 { margin-top: 3rem; }
  .mb-8 { margin-bottom: 2rem; }
  .ml-4 { margin-left: 1rem; }

  @media (max-width: 768px) {
    .study-container {
      padding-top: 1.5rem;
      padding-left: 1rem;
      padding-right: 1rem;
    }

    .lesson-header, .markdown-body, .completion-card {
      padding: 2rem 1.5rem;
    }

    .markdown-body {
      font-size: 1rem;
    }

    .actions {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .actions .btn {
      margin-left: 0 !important;
      width: 100%;
    }
  }
</style>
