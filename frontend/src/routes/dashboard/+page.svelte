<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { formatPedagogicalCode } from '$lib/utils';

  let learningPath: Array<{area_id: string, concept_name: string, display_name: string, friendly_code: string, description: string, score: number}> = [];
  let history: Array<{id: number, created_at: string, type: string, has_analysis: boolean}> = [];
  let user: any = null;
  let loading = true;
  let errorMessage = "";

  onMount(async () => {
    try {
      const fetchOptions = {
        credentials: "include"
      };

      const userRes = await fetch("http://localhost:8000/api/v1/auth/me", fetchOptions);
      if (userRes.status === 401) {
        goto("/login");
        return;
      }
      user = await userRes.json();

      const pathRes = await fetch("http://localhost:8000/api/v1/learning-path", fetchOptions);
      if (pathRes.ok) {
        const data = await pathRes.json();
        learningPath = data.learning_path;
      }

      const historyRes = await fetch("http://localhost:8000/api/v1/assessment-report/history", fetchOptions);
      if (historyRes.ok) {
        const hData = await historyRes.json();
        history = hData.history;
      }

      loading = false;
    } catch (error) {
      console.error("Error loading dashboard:", error);
      errorMessage = "Houve um erro ao carregar seus dados. Por favor, tente novamente mais tarde.";
      loading = false;
    }
  });

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  }

  $: areaScores = {
    'MT': { label: 'Matemática', color: '#00D1FF', score: 0, count: 0, delay: 150 },
    'CN': { label: 'Ciências da Natureza', color: '#BFFF00', score: 0, count: 0, delay: 300 },
    'LC': { label: 'Linguagens', color: '#FF4D00', score: 0, count: 0, delay: 450 },
    'CH': { label: 'Ciências Humanas', color: '#FFD700', score: 0, count: 0, delay: 600 }
  };

  $: {
    if (learningPath.length > 0) {
      let temp: Record<string, { score: number, count: number }> = {
        'MT': { score: 0, count: 0 },
        'CN': { score: 0, count: 0 },
        'LC': { score: 0, count: 0 },
        'CH': { score: 0, count: 0 }
      };
      
      learningPath.forEach(item => {
        const prefix = item.area_id || (item.concept_name && !item.concept_name.startsWith('SKL-') ? item.concept_name.substring(0, 2) : 'MT');
        if (temp[prefix]) {
          temp[prefix].score += item.score;
          temp[prefix].count += 1;
        }
      });
      
      Object.keys(temp).forEach(key => {
        if (temp[key].count > 0) {
          areaScores[key as keyof typeof areaScores].score = temp[key].score / temp[key].count;
        }
      });
    }
  }
  
  $: areaCards = Object.keys(areaScores).map(k => ({ id: k, ...areaScores[k as keyof typeof areaScores] }));
</script>

<div class="dashboard-wrapper">
  {#if loading}
    <div class="status-screen" out:fade>
      <div class="loader-visual">
        <div class="orbit"></div>
        <div class="center-glow"></div>
      </div>
      <p>Sincronizando seus dados...</p>
    </div>
  {:else if errorMessage}
    <div class="status-screen error-state">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      </div>
      <p>{errorMessage}</p>
      <button class="btn btn-outline mt-4" on:click={() => window.location.reload()}>Tentar Novamente</button>
    </div>
  {:else}
    <div class="dashboard-header animate-fade-in">
      <div>
        <h1 class="page-title">Bem-vindo(a), <span class="text-gradient">{user.name.split(' ')[0]}</span></h1>
        <p class="page-subtitle">Acompanhe seu desempenho por área do conhecimento.</p>
      </div>
      <div class="header-actions">
        {#if !user.is_diagnostic_completed}
          <a href="/prova" class="btn btn-primary">
            Novo Diagnóstico
          </a>
        {/if}
      </div>
    </div>

    <!-- Liquid Glass 2.0 Area Cards -->
    <div class="area-cards-grid">
      {#each areaCards as area (area.id)}
        <a 
          href="/area/{area.id}"
          class="area-card"
          style="--area-color: {area.color}; text-decoration: none;"
          in:fly={{ y: 20, duration: 800, delay: area.delay }}
        >
          <div class="area-content">
            <h3 class="area-title">{area.label}</h3>
            <div class="area-score-wrap">
              <span class="area-score">{(area.score * 100).toFixed(0)}%</span>
              <span class="area-label">Proficiência</span>
            </div>
            <div class="area-progress">
              <div class="progress-fill" style="width: {area.score * 100}%;"></div>
            </div>
          </div>
        </a>
      {/each}
    </div>

    <div class="main-content-grid">
      <!-- History Section -->
      <section class="plan-section" in:fade={{ duration: 800, delay: 800 }}>
        <div class="section-header">
          <h2 class="section-title">Histórico de Avaliações</h2>
        </div>

        {#if history.length > 0}
          <div class="plan-cards">
            {#each history.slice(0, 2) as item}
              <div class="plan-card glass-panel group">
                <div class="plan-card-header">
                  <div class="priority-badge">Data: {formatDate(item.created_at)}</div>
                  <span class="skill-tag">{item.type.toUpperCase()}</span>
                </div>
                <h3 class="plan-card-title">Análise de Proficiência</h3>
                <p class="plan-card-desc">Veja os detalhes desta avaliação, incluindo suas forças, fraquezas e o plano de ação estratégico.</p>

                <div class="plan-card-footer mt-4">
                  <a href="/prova/resultado?id={item.id}" class="btn btn-outline" style="width: 100%; text-align: center;">Ver Análise Completa</a>
                </div>
              </div>
            {/each}
          </div>
          <div class="mt-4 text-center">
            <a href="/history" class="btn btn-outline" style="width: 100%;">Ver todo o histórico</a>
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
      </section>

      <!-- Profile Link Section -->
      <section class="profile-section" in:fade={{ duration: 800, delay: 900 }}>
        <div class="glass-panel text-center profile-panel">
          <h2 class="section-title">Dados Técnicos</h2>
          <p class="mt-2 mb-4">Acesse seu perfil para visualizar a análise granular de competências e habilidades (Matriz ENEM).</p>
          <a href="/profile" class="btn btn-secondary" style="width: 100%;">Acessar Perfil Completo</a>
        </div>
      </section>
    </div>
  {/if}
</div>

<style>
  /* Base Layout */
  .dashboard-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }

  /* Status Screens */
  .status-screen {
    height: 60vh;
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

  .error-state { color: #EF4444; }
  .error-icon { margin-bottom: 1rem; opacity: 0.8; }
  .mt-4 { margin-top: 1rem; }
  .mt-2 { margin-top: 0.5rem; }
  .mb-4 { margin-bottom: 1rem; }
  .text-center { text-align: center; }

  /* Header */
  .dashboard-header {
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

  .btn-primary {
    background: #FFF;
    color: #000;
  }

  .btn-primary:hover {
    background: rgba(255,255,255,0.8);
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #FFF;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.4);
  }

  .btn-outline {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.2);
    color: #FFF;
  }

  .btn-outline:hover {
    background: rgba(255,255,255,0.1);
  }

  /* Liquid Glass 2.0 Area Cards */
  .area-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3.5rem;
  }

  .area-card {
    position: relative;
    background: #0A0A0B; /* Deep Charcoal/Navy */
    border: 1px solid rgba(255, 255, 255, 0.05); /* 1px fine border */
    border-radius: 12px;
    padding: 2rem 1.5rem;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Spring-like */
    display: block;
  }

  .area-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top left, var(--area-color), transparent 70%);
    opacity: 0.05;
    transition: opacity 0.4s ease;
    pointer-events: none;
  }

  .area-card:hover {
    border-color: var(--area-color);
    box-shadow: 0 0 25px var(--area-color), inset 0 0 10px rgba(255, 255, 255, 0.02);
    transform: translateY(-5px);
  }

  .area-card:hover::before {
    opacity: 0.15;
  }

  .area-content {
    position: relative;
    z-index: 2;
  }

  .area-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #FFF;
    margin-bottom: 1.5rem;
    letter-spacing: 0.02em;
    text-transform: uppercase;
  }

  .area-score-wrap {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .area-score {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--area-color);
    text-shadow: 0 0 15px var(--area-color);
  }

  .area-label {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .area-progress {
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--area-color);
    box-shadow: 0 0 10px var(--area-color);
    border-radius: 2px;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Main Grid */
  .main-content-grid {
    display: grid;
    grid-template-columns: 1fr 400px;
    gap: 3rem;
  }

  /* Section Styles */
  .section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #FFF;
  }

  /* Plan Cards */
  .plan-cards {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .plan-card {
    padding: 2rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    transition: all 0.3s ease;
  }

  .plan-card:hover {
    border-color: rgba(255,255,255,0.2);
  }

  .plan-card-header {
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

  .plan-card-title {
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #FFF;
  }

  .plan-card-desc {
    color: rgba(255,255,255,0.6);
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  /* Profile Panel */
  .profile-panel {
    padding: 2rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .profile-panel p {
    color: rgba(255,255,255,0.6);
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .empty-state {
    padding: 3rem 2rem;
    text-align: center;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
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

  @media (max-width: 1024px) {
    .main-content-grid {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 768px) {
    .dashboard-wrapper {
      padding: 1.5rem 1rem;
    }
    
    .page-title {
      font-size: 1.75rem;
    }

    .area-cards-grid {
      grid-template-columns: 1fr;
    }

    .main-content-grid {
      gap: 2.5rem;
    }

    .plan-card {
      padding: 1.5rem;
    }
  }
</style>
