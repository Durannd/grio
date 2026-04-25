<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { formatPedagogicalCode } from '$lib/utils';

  let learningPath: Array<{concept_name: string, description: string, score: number}> = [];
  let studyPlan: any = null;
  let user: any = null;
  let loading = true;
  let loadingPlan = true;
  let errorMessage = "";

  onMount(async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        goto("/login");
        return;
      }

      const headers = {
        "Authorization": `Bearer ${token}`
      };

      const userRes = await fetch("http://localhost:8000/api/v1/auth/me", { headers });
      if (userRes.status === 401) {
        localStorage.removeItem("token");
        goto("/login");
        return;
      }
      user = await userRes.json();

      const pathRes = await fetch("http://localhost:8000/api/v1/learning-path", { headers });
      if (pathRes.ok) {
        const data = await pathRes.json();
        learningPath = data.learning_path;
      }

      loading = false;

      const planRes = await fetch("http://localhost:8000/api/v1/study-plan", { headers });
      if (planRes.ok) {
        studyPlan = await planRes.json();
      }
      loadingPlan = false;
    } catch (error) {
      console.error("Error loading dashboard:", error);
      errorMessage = "Houve um erro ao carregar seus dados. Por favor, tente novamente mais tarde.";
      loading = false;
      loadingPlan = false;
    }
  });

  function logout() {
    localStorage.removeItem("token");
    goto("/login");
  }

  $: totalModules = learningPath.length;
  $: masteredModules = learningPath.filter(m => m.score >= 0.8).length;
  $: needsAttention = learningPath.filter(m => m.score < 0.5).length;
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
        <p class="page-subtitle">Acompanhe seu desempenho e siga as recomendações da IA para evoluir no ENEM.</p>
      </div>
      <div class="header-actions">
        {#if learningPath.length === 0}
          <a href="/prova" class="btn btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="m18 15-6-6-6 6"/></svg>
            Fazer Diagnóstico
          </a>
        {/if}
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid animate-slide-up stagger-1">
      <div class="kpi-card glass-panel">
        <div class="kpi-icon blue">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>
        </div>
        <div class="kpi-data">
          <p class="kpi-label">Módulos Analisados</p>
          <h3 class="kpi-value">{totalModules}</h3>
        </div>
      </div>
      
      <div class="kpi-card glass-panel">
        <div class="kpi-icon green">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        </div>
        <div class="kpi-data">
          <p class="kpi-label">Competências Dominadas</p>
          <h3 class="kpi-value">{masteredModules}</h3>
        </div>
      </div>

      <div class="kpi-card glass-panel">
        <div class="kpi-icon orange">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="kpi-data">
          <p class="kpi-label">Precisam de Revisão</p>
          <h3 class="kpi-value">{needsAttention}</h3>
        </div>
      </div>
      
      <div class="kpi-card glass-panel ai-highlight">
        <div class="kpi-icon ai-gold">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="kpi-data">
          <p class="kpi-label">Foco Recomendado</p>
          <h3 class="kpi-value text-gradient">{studyPlan?.plan?.[0]?.skill_code ? formatPedagogicalCode(studyPlan.plan[0].skill_code) : "Aguardando"}</h3>
        </div>
      </div>
    </div>

    <div class="main-content-grid">
      <!-- AI Study Plan Column -->
      <section class="plan-section animate-slide-up stagger-2">
        <div class="section-header">
          <h2 class="section-title">Plano de Ação Estratégico</h2>
          <span class="badge ai-badge">IA Griô</span>
        </div>

        {#if loadingPlan}
          <div class="glass-panel loading-skeleton">
            <div class="skeleton-line" style="width: 60%"></div>
            <div class="skeleton-line"></div>
            <div class="skeleton-line" style="width: 80%"></div>
          </div>
        {:else if studyPlan && studyPlan.plan && studyPlan.plan.length > 0}
          <p class="ai-motivation">"{studyPlan.motivation}"</p>
          
          <div class="plan-cards">
            {#each studyPlan.plan as step}
              <div class="plan-card glass-panel group">
                <div class="plan-card-header">
                  <div class="priority-badge">Prioridade {step.priority}</div>
                  <span class="skill-tag">{formatPedagogicalCode(step.skill_code)}</span>
                </div>
                <h3 class="plan-card-title">{step.title}</h3>
                <p class="plan-card-desc">{step.justification}</p>
                
                <div class="plan-card-body">
                  <div class="topics-list">
                    <strong>Conteúdos-chave:</strong>
                    <ul>
                      {#each step.topics as topic}
                        <li>
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                          <span>{topic}</span>
                        </li>
                      {/each}
                    </ul>
                  </div>
                </div>
                <div class="plan-card-footer">
                  <div class="tip-box">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tip-icon"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1.41.56 2.63 1.49 3.49.77.77 1.24 1.53 1.42 2.51"/></svg>
                    <span>{step.tip}</span>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="glass-panel empty-state">
            <p>Seu plano ainda não foi gerado ou você precisa completar o diagnóstico.</p>
          </div>
        {/if}
      </section>

      <!-- Mastery / Path Column -->
      <section class="path-section animate-slide-up stagger-3">
        <div class="section-header">
          <h2 class="section-title">Mapa de Proficiência</h2>
        </div>

        {#if learningPath.length === 0}
          <div class="glass-panel empty-state">
             <div class="empty-icon">
               <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
             </div>
             <h3>Mapeamento Pendente</h3>
             <p>Ainda não temos dados suficientes para traçar sua proficiência.</p>
             <a href="/prova" class="btn btn-primary mt-4">Iniciar Diagnóstico</a>
          </div>
        {:else}
          <div class="proficiency-list">
            {#each learningPath as concept}
              <div class="proficiency-item glass-panel">
                <div class="prof-header">
                  <h4>{formatPedagogicalCode(concept.concept_name)}</h4>
                  <div class="prof-score" class:high={concept.score >= 0.7} class:med={concept.score >= 0.4 && concept.score < 0.7} class:low={concept.score < 0.4}>
                    {(concept.score * 100).toFixed(0)}%
                  </div>
                </div>
                <p class="prof-desc">{concept.description}</p>
                <div class="progress-bar-container">
                  <div class="progress-bar" style="width: {concept.score * 100}%; background-color: {concept.score >= 0.7 ? '#10B981' : (concept.score >= 0.4 ? '#F59E0B' : '#EF4444')}"></div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
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
    border: 2px solid rgba(201, 160, 94, 0.2);
    border-radius: 50%;
    border-top-color: var(--primary);
    animation: spin 1.5s linear infinite;
  }

  .center-glow {
    position: absolute;
    inset: 30%;
    background: var(--primary);
    filter: blur(10px);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes spin { 100% { transform: rotate(360deg); } }
  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

  .error-state { color: var(--danger); }
  .error-icon { margin-bottom: 1rem; opacity: 0.8; }
  .mt-4 { margin-top: 1rem; }

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
  }

  .page-subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
    max-width: 600px;
  }

  /* KPI Grid */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3.5rem;
  }

  .kpi-card {
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    transition: transform 0.3s ease, border-color 0.3s ease;
  }

  .kpi-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255,255,255,0.15);
  }

  .ai-highlight {
    background: linear-gradient(145deg, rgba(201, 160, 94, 0.05), rgba(0,0,0,0.4));
    border: 1px solid rgba(201, 160, 94, 0.2);
  }

  .kpi-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
  }

  .kpi-icon.blue { color: #60A5FA; background: rgba(96, 165, 250, 0.1); }
  .kpi-icon.green { color: #34D399; background: rgba(52, 211, 153, 0.1); }
  .kpi-icon.orange { color: #FBBF24; background: rgba(251, 191, 36, 0.1); }
  .kpi-icon.ai-gold { color: var(--primary); background: rgba(201, 160, 94, 0.15); }

  .kpi-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }

  .kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1;
  }

  /* Main Grid */
  .main-content-grid {
    display: grid;
    grid-template-columns: 1fr 400px;
    gap: 3rem;
  }

  @media (max-width: 1024px) {
    .main-content-grid {
      grid-template-columns: 1fr;
    }
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
  }

  .badge {
    padding: 0.3rem 0.75rem;
    border-radius: 2rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .ai-badge {
    background: linear-gradient(135deg, var(--primary) 0%, #d4a017 100%);
    color: #000;
  }

  .ai-motivation {
    font-size: 1.15rem;
    color: var(--text-secondary);
    font-style: italic;
    margin-bottom: 2.5rem;
    padding-left: 1.5rem;
    border-left: 3px solid var(--primary);
  }

  /* Plan Cards */
  .plan-cards {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .plan-card {
    padding: 2rem;
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.3s ease;
  }

  .plan-card:hover {
    border-color: rgba(201, 160, 94, 0.3);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
    color: var(--primary);
    background: rgba(201, 160, 94, 0.1);
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .skill-tag {
    font-size: 0.85rem;
    color: var(--text-tertiary);
    font-family: monospace;
    background: rgba(0,0,0,0.3);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .plan-card-title {
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
  }

  .plan-card-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .topics-list {
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .topics-list strong {
    display: block;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
  }

  .topics-list ul {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
  }

  .topics-list li {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    font-size: 0.95rem;
    color: var(--text-primary);
  }

  .topics-list li svg {
    margin-top: 0.15rem;
    flex-shrink: 0;
  }

  .tip-box {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    background: rgba(201, 160, 94, 0.05);
    border: 1px solid rgba(201, 160, 94, 0.2);
    padding: 1rem;
    border-radius: 8px;
  }

  .tip-icon {
    color: var(--primary);
    flex-shrink: 0;
    margin-top: 0.1rem;
  }

  .tip-box span {
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--text-secondary);
  }

  /* Proficiency Map */
  .proficiency-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .proficiency-item {
    padding: 1.5rem;
    transition: transform 0.2s ease;
  }
  
  .proficiency-item:hover {
    transform: translateX(4px);
    border-color: rgba(255,255,255,0.15);
  }

  .prof-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .prof-header h4 {
    font-size: 1.05rem;
    font-weight: 600;
  }

  .prof-score {
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
  }
  
  .prof-score.high { color: #34D399; }
  .prof-score.med { color: #FBBF24; }
  .prof-score.low { color: #F87171; }

  .prof-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .progress-bar-container {
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-bar {
    height: 100%;
    border-radius: 3px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .empty-state {
    padding: 3rem 2rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .empty-icon {
    color: var(--text-tertiary);
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
  }

  .empty-state p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 300px;
  }

  /* Skeleton Loader */
  .loading-skeleton {
    padding: 2rem;
  }

  .skeleton-line {
    height: 20px;
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    margin-bottom: 1rem;
    animation: skeleton-pulse 1.5s infinite;
  }

  @keyframes skeleton-pulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
  }
</style>