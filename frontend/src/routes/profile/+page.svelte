<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { formatPedagogicalCode } from '$lib/utils';

  let learningPath: Array<{concept_name: string, description: string, score: number, is_inferred?: boolean}> = [];
  let user: any = null;
  let loading = true;
  let errorMessage = "";
  
  // Tab management
  let activeTab = 'technical'; // 'profile' | 'technical'

  $: groupedPath = learningPath.reduce((acc: any, item) => {
    const area = item.concept_name.substring(0, 2);
    if (!acc[area]) acc[area] = [];
    acc[area].push(item);
    return acc;
  }, {});

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

      const pathRes = await fetch("http://localhost:8000/api/v1/learning-path/full", fetchOptions);
      if (pathRes.ok) {
        const data = await pathRes.json();
        learningPath = data.learning_path || data;
      }

      loading = false;
    } catch (error) {
      console.error("Error loading profile:", error);
      errorMessage = "Houve um erro ao carregar seus dados.";
      loading = false;
    }
  });
</script>

<div class="profile-wrapper">
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
      <p>{errorMessage}</p>
      <button class="btn btn-outline mt-4" on:click={() => window.location.reload()}>Tentar Novamente</button>
    </div>
  {:else}
    <div class="profile-header animate-fade-in">
      <div class="header-content">
        {#if user.avatar_url}
          <img src={user.avatar_url} alt={user.name} class="avatar" />
        {:else}
          <div class="avatar">{user.name.charAt(0).toUpperCase()}</div>
        {/if}
        <div>
          <h1 class="page-title">{user.name}</h1>
          <p class="page-subtitle">{user.email}</p>
        </div>
      </div>
      <div class="header-actions">
        <a href="/dashboard" class="btn btn-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="m15 18-6-6 6-6"/></svg>
          Voltar ao Dashboard
        </a>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <button 
        class="tab-btn {activeTab === 'profile' ? 'active' : ''}" 
        on:click={() => activeTab = 'profile'}
      >
        Perfil Geral
      </button>
      <button 
        class="tab-btn {activeTab === 'technical' ? 'active' : ''}" 
        on:click={() => activeTab = 'technical'}
      >
        Dados Técnicos (Matriz ENEM)
      </button>
    </div>

    <div class="tab-content">
      {#if activeTab === 'profile'}
        <div class="glass-panel text-center" in:fly={{ y: 10, duration: 400 }}>
          <h2 class="section-title mb-4">Informações da Conta</h2>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Nome Completo</span>
              <span class="info-value">{user.name}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Email</span>
              <span class="info-value">{user.email}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Dias de Ofensiva</span>
              <span class="info-value streak">{user.current_streak} dias 🔥</span>
            </div>
          </div>
        </div>
      {:else if activeTab === 'technical'}
        <div class="technical-section" in:fly={{ y: 10, duration: 400 }}>
          <div class="section-header">
            <div>
              <h2 class="section-title">Análise Granular</h2>
              <p class="section-desc">Detalhamento da sua proficiência em competências e habilidades da Matriz de Referência do ENEM.</p>
            </div>
          </div>

          {#if learningPath.length === 0}
            <div class="glass-panel empty-state">
              <h3>Mapeamento Pendente</h3>
              <p>Ainda não temos dados suficientes para traçar sua proficiência granular.</p>
            </div>
          {:else}
            {#each Object.entries(groupedPath) as [areaCode, concepts]}
              <div class="area-group mb-4">
                <h3 class="area-group-title">
                  {areaCode === 'MT' ? 'Matemática e suas Tecnologias' : areaCode === 'CN' ? 'Ciências da Natureza e suas Tecnologias' : areaCode === 'LC' ? 'Linguagens, Códigos e suas Tecnologias' : 'Ciências Humanas e suas Tecnologias'}
                </h3>
                <div class="proficiency-list">
                  {#each concepts as concept (concept.concept_name)}
                    <div class="proficiency-item glass-panel" class:inferred={concept.is_inferred}>
                      <div class="prof-header">
                        <div class="prof-title-wrap">
                          <span class="prof-code">{concept.concept_name}</span>
                          <h4>{formatPedagogicalCode(concept.concept_name)}</h4>
                        </div>
                        {#if concept.is_inferred}
                          <div class="inferred-badge">POTENCIAL</div>
                        {:else}
                          <div class="prof-score" class:high={concept.score >= 0.7} class:med={concept.score >= 0.4 && concept.score < 0.7} class:low={concept.score < 0.4}>
                            {(concept.score * 100).toFixed(0)}%
                          </div>
                        {/if}
                      </div>
                      <p class="prof-desc">{concept.description}</p>
                      <div class="progress-bar-container" class:inferred-bar={concept.is_inferred}>
                        <div class="progress-bar" style="width: {concept.score * 100}%; background-color: {concept.is_inferred ? '#6B7280' : (concept.score >= 0.7 ? '#10B981' : (concept.score >= 0.4 ? '#F59E0B' : '#EF4444'))}"></div>
                      </div>
                      <div class="prof-footer mt-4">
                        <a href="/estudar/{concept.concept_name}" class="btn btn-primary btn-sm" style="width: 100%; text-align: center;">
                          {concept.is_inferred ? 'Explorar Habilidade' : 'Estudar este conceito'}
                        </a>
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .profile-wrapper {
    max-width: 1000px;
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

  /* Header */
  .profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .avatar {
    width: 80px;
    height: 80px;
    background: var(--primary);
    border: 2px solid var(--primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    font-weight: 800;
    color: white;
    object-fit: cover;
  }

  .page-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    letter-spacing: -0.02em;
    color: #FFF;
  }

  .page-subtitle {
    color: rgba(255,255,255,0.6);
    font-size: 1.1rem;
  }

  /* Buttons */
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

  .btn-outline {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.2);
    color: #FFF;
  }

  .btn-outline:hover {
    background: rgba(255,255,255,0.1);
  }

  .btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  /* Tabs */
  .tabs-container {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }

  .tab-btn {
    background: none;
    border: none;
    color: rgba(255,255,255,0.5);
    font-size: 1.1rem;
    font-weight: 600;
    padding: 1rem 1.5rem;
    cursor: pointer;
    position: relative;
    transition: color 0.3s ease;
  }

  .tab-btn:hover {
    color: rgba(255,255,255,0.8);
  }

  .tab-btn.active {
    color: #FFF;
  }

  .tab-btn.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: #FFF;
    box-shadow: 0 0 10px rgba(255,255,255,0.5);
  }

  /* Content Panels */
  .glass-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 2rem;
  }

  .text-center {
    text-align: center;
  }

  .section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #FFF;
  }

  .section-desc {
    color: rgba(255,255,255,0.6);
    font-size: 0.95rem;
    margin-top: 0.5rem;
  }

  .mb-4 {
    margin-bottom: 1rem;
  }
  .mt-4 {
    margin-top: 1rem;
  }

  /* Info Grid */
  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    text-align: left;
  }

  .info-item {
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
    background: rgba(0,0,0,0.3);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.02);
  }

  .info-label {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }

  .info-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: #FFF;
  }

  .streak {
    color: #FF4D00;
  }

  /* Technical Section */
  .section-header {
    margin-bottom: 2rem;
  }

  .area-group {
    margin-bottom: 3rem;
  }

  .area-group-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-light, #DFB97B);
    margin-bottom: 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 0.5rem;
  }

  .proficiency-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .proficiency-item {
    padding: 1.5rem;
    transition: transform 0.2s ease, border-color 0.2s ease;
  }

  .proficiency-item:hover {
    transform: translateX(4px);
    border-color: rgba(255,255,255,0.15);
  }

  .prof-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .prof-title-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .prof-code {
    font-size: 0.8rem;
    font-family: monospace;
    background: rgba(255,255,255,0.1);
    color: #FFF;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    width: fit-content;
  }

  .prof-title-wrap h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #FFF;
  }

  .prof-score {
    font-weight: 700;
    font-size: 1rem;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
  }

  .prof-score.high { color: #34D399; }
  .prof-score.med { color: #FBBF24; }
  .prof-score.low { color: #F87171; }

  .inferred-badge {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.1);
    color: #FFF;
    letter-spacing: 0.05em;
  }

  .prof-desc {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.6);
    margin-bottom: 1.25rem;
    line-height: 1.6;
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

  .prof-footer {
    display: flex;
    justify-content: flex-end;
  }

  @media (max-width: 768px) {
    .profile-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 1.5rem;
    }
    
    .tabs-container {
      flex-direction: column;
      gap: 0;
    }

    .tab-btn {
      text-align: left;
      padding: 1rem 0;
    }

    .info-grid {
      grid-template-columns: 1fr;
    }
    
    .prof-header {
      flex-direction: column;
      gap: 1rem;
    }
  }
</style>