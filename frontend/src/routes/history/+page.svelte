<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { PUBLIC_API_BASE_URL } from '$env/static/public';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { goto } from '$app/navigation';

  let history: Array<{id: number, created_at: string, type: string, has_analysis: boolean}> = [];
  let user: any = null;
  let loading = true;
  let errorMessage = "";

  onMount(async () => {
    try {
      const fetchOptions = {
        credentials: "include"
      };

      const userRes = await fetch(`${PUBLIC_API_BASE_URL}/api/v1/auth/me`, fetchOptions);
      if (userRes.status === 401) {
        goto("/login");
        return;
      }
      user = await userRes.json();

      const historyRes = await fetch(`${PUBLIC_API_BASE_URL}/api/v1/assessment-report/history`, fetchOptions);
      if (historyRes.ok) {
        const hData = await historyRes.json();
        history = hData.history;
      }

      loading = false;
    } catch (error) {
      console.error("Error loading history:", error);
      errorMessage = "Houve um erro ao carregar seu histórico. Por favor, tente novamente mais tarde.";
      loading = false;
    }
  });

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  }
</script>

<div class="history-wrapper">
  {#if loading}
    <div class="status-screen" out:fade>
      <LoadingSpinner />
      <p>Carregando histórico...</p>
    </div>
  {:else if errorMessage}
    <div class="status-screen error-state">
      <p>{errorMessage}</p>
      <button class="btn btn-outline mt-4" on:click={() => window.location.reload()}>Tentar Novamente</button>
    </div>
  {:else}
    <div class="history-header animate-fade-in">
      <div>
        <h1 class="page-title">Histórico de Avaliações</h1>
        <p class="page-subtitle">Acompanhe todas as suas avaliações anteriores.</p>
      </div>
      <div class="header-actions">
        <a href="/dashboard" class="btn btn-outline">Voltar ao Dashboard</a>
      </div>
    </div>

    {#if history.length > 0}
      <div class="history-grid">
        {#each history as item, index (item.id)}
          <div class="history-card glass-panel group" in:fly={{ y: 20, duration: 600, delay: index * 50 }}>
            <div class="history-card-header">
              <div class="priority-badge">Data: {formatDate(item.created_at)}</div>
              <span class="skill-tag">{item.type.toUpperCase()}</span>
            </div>
            <h3 class="history-card-title">Análise de Proficiência</h3>
            <p class="history-card-desc">Detalhes desta avaliação, incluindo diagnóstico e plano de ação.</p>
            <div class="history-card-footer mt-4">
              <a href="/prova/resultado?id={item.id}" class="btn btn-primary" style="width: 100%; text-align: center;">Ver Análise Completa</a>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="glass-panel empty-state">
        <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>    
        </div>
        <h3>Nenhum histórico</h3>
        <p>Você ainda não realizou nenhuma avaliação.</p>
      </div>
    {/if}
  {/if}
</div>

<style>
  .history-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }

  .status-screen {
    height: 60vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .error-state { color: #EF4444; }
  .mt-4 { margin-top: 1rem; }

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }

  .page-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
    color: #FFF;
  }

  .page-subtitle {
    color: rgba(255,255,255,0.6);
    font-size: 1.1rem;
    max-width: 600px;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
  }

  .btn-outline {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.2);
    color: #FFF;
  }

  .btn-outline:hover {
    background: rgba(255,255,255,0.1);
  }

  .btn-primary {
    background: #FFF;
    color: #000;
  }

  .btn-primary:hover {
    background: rgba(255,255,255,0.8);
  }

  .history-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .glass-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 2rem;
  }

  .history-card {
    transition: all 0.3s ease;
  }

  .history-card:hover {
    border-color: rgba(255,255,255,0.2);
    transform: translateY(-4px);
  }

  .history-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
  }

  .priority-badge {
    font-size: 0.8rem;
    font-weight: 700;
    color: #FFF;
    background: rgba(255,255,255,0.1);
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .skill-tag {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.6);
    font-family: monospace;
    background: rgba(0,0,0,0.3);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .history-card-title {
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #FFF;
  }

  .history-card-desc {
    color: rgba(255,255,255,0.6);
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .empty-state {
    padding: 3rem 2rem;
    text-align: center;
  }

  .empty-icon {
    color: rgba(255,255,255,0.4);
    margin-bottom: 1rem;
    display: flex;
    justify-content: center;
  }

  .empty-state h3 {
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
    color: #FFF;
  }

  .empty-state p {
    color: rgba(255,255,255,0.6);
    font-size: 0.95rem;
  }

  @media (max-width: 768px) {
    .history-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }
  }
</style>
