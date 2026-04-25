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

      // Fetch user profile
      const userRes = await fetch("http://localhost:8000/api/v1/auth/me", { headers });
      if (userRes.status === 401) {
        localStorage.removeItem("token");
        goto("/login");
        return;
      }
      user = await userRes.json();

      // Fetch learning path
      const pathRes = await fetch("http://localhost:8000/api/v1/learning-path", { headers });
      if (pathRes.ok) {
        const data = await pathRes.json();
        learningPath = data.learning_path;
      }

      loading = false; // Libera a UI básica

      // Fetch AI Study Plan
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
</script>

<div class="dashboard-page container section-padding">
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
      <div class="error-icon">⚠️</div>
      <p>{errorMessage}</p>
      <button class="btn btn-outline" on:click={() => window.location.reload()}>Tentar Novamente</button>
    </div>
  {:else}
    <div class="dashboard-grid">
      <aside class="dashboard-sidebar animate-slide-up stagger-1">
        <header class="dashboard-header">
          <div class="welcome">
            <span class="eyebrow">Painel do Aluno</span>
            <h1>Olá, <span class="text-gradient">{user.name}</span></h1>
            <p>Seu plano de estudos estratégico para o ENEM.</p>
          </div>
          <div class="sidebar-actions">
            <button class="btn btn-outline" on:click={logout}>Sair da Conta</button>
          </div>
        </header>

        <div class="glass-card overview-card">
           <h3>Seu Progresso</h3>
           <p>O Griô identificou módulos estratégicos com base no seu diagnóstico. Siga o cronograma para dominar as competências do ENEM.</p>
        </div>
      </aside>

      <section class="path-section animate-slide-up stagger-2">
        <div class="section-title">
          <h2>Seu Plano de Estudos</h2>
          <span class="badge-ai">IA ESTRATEGISTA</span>
        </div>
        
        {#if loadingPlan}
          <div class="plan-loading glass-card">Gerando recomendações personalizadas...</div>
        {:else if studyPlan && studyPlan.plan}
          <div class="study-plan-container animate-slide-up">
            <p class="motivation">"{studyPlan.motivation}"</p>
            <div class="plan-grid">
              {#each studyPlan.plan as step}
                <div class="plan-item glass-card">
                  <div class="plan-priority">#{step.priority}</div>
                  <div class="plan-content">
                    <h3>{step.title}</h3>
                    <div class="skill-ref">{formatPedagogicalCode(step.skill_code)}</div>
                    <p class="justification">{step.justification}</p>
                    <div class="topics">
                      <strong>Conteúdos para focar:</strong>
                      <ul>
                        {#each step.topics as topic}
                          <li>{topic}</li>
                        {/each}
                      </ul>
                    </div>
                    <div class="study-tip">
                      <strong>💡 Dica:</strong> {step.tip}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <div class="section-title mt-12">
          <h2>Sua Trilha de Conhecimento</h2>
        </div>
        
      {#if learningPath.length === 0}
        <div class="glass-card text-center empty-state">
          <h3>Seu plano ainda não foi gerado</h3>
          <p>Realize a avaliação diagnóstica para identificarmos seu nível de proficiência.</p>
          <a href="/prova" class="btn btn-primary" style="margin-top: 1.5rem;">Iniciar Avaliação</a>
        </div>
      {:else}
        <div class="timeline">
          <div class="timeline-line"></div>
          {#each learningPath as concept, i}
            <div class="timeline-node" style="animation-delay: {0.1 * (i + 3)}s">
              <div class="node-marker">
                <div class="node-dot"></div>
              </div>
              <div class="glass-card node-content">
                <div class="node-header">
                  <h3>{formatPedagogicalCode(concept.concept_name)}</h3>
                  <div class="proficiency-badge">
                    Proficiência: <strong>{(concept.score * 100).toFixed(0)}%</strong>
                  </div>
                </div>
                <p>{concept.description}</p>
                <div class="node-actions">
                  <button class="btn btn-primary">Estudar Módulo</button>
                </div>
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

  .dashboard-grid {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 4rem;
    align-items: start;
  }

  @keyframes spin { 100% { transform: rotate(360deg); } }
  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

  .eyebrow {
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    font-size: 0.7rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    display: block;
  }

  .dashboard-header {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }

  .welcome h1 {
    font-size: 2.5rem;
    margin-bottom: 0.25rem;
  }

  .welcome p {
    color: var(--text-secondary);
    font-size: 1.1rem;
  }

  .section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3rem;
  }

  .section-title h2 {
    font-size: 1.8rem;
    margin: 0;
  }

  .badge-ai {
    background: linear-gradient(135deg, var(--primary) 0%, #d4a017 100%);
    color: white;
    font-size: 0.7rem;
    font-weight: 800;
    padding: 0.3rem 0.8rem;
    border-radius: 2rem;
    letter-spacing: 0.1em;
  }

  .mt-12 { margin-top: 4rem; }

  .motivation {
    font-style: italic;
    color: var(--text-secondary);
    margin-bottom: 2rem;
    font-size: 1.1rem;
    border-left: 3px solid var(--primary);
    padding-left: 1.5rem;
  }

  .plan-grid {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 3rem;
  }

  .plan-item {
    display: flex;
    gap: 1.5rem;
    padding: 2rem;
  }

  .plan-priority {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary);
    opacity: 0.5;
  }

  .plan-content h3 {
    font-size: 1.3rem;
    margin-bottom: 0.25rem;
  }

  .skill-ref {
    font-size: 0.8rem;
    color: var(--primary-light);
    font-weight: 600;
    margin-bottom: 1rem;
    text-transform: uppercase;
  }

  .justification {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
  }

  .topics {
    margin-bottom: 1.5rem;
    background: rgba(255,255,255,0.03);
    padding: 1rem;
    border-radius: 0.75rem;
  }

  .topics strong {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }

  .topics ul {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .topics li::before {
    content: "•";
    color: var(--primary);
    margin-right: 0.5rem;
  }

  .topics li {
    font-size: 0.9rem;
    color: var(--text-primary);
  }

  .study-tip {
    font-size: 0.9rem;
    background: rgba(201, 160, 94, 0.1);
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    border-left: 3px solid var(--primary);
  }

  .plan-loading {
    padding: 3rem;
    text-align: center;
    color: var(--text-tertiary);
    font-style: italic;
  }

  .sidebar-actions {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-top: 2rem;
  }

  .retake-link {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    color: var(--primary);
    text-decoration: none;
    transition: color 0.3s ease;
  }
  
  .retake-link:hover {
    color: var(--primary-light);
  }

  .overview-card {
    padding: 2.5rem 2rem;
    margin-top: 2rem;
  }

  .overview-card h3 {
    margin-bottom: 1rem;
    color: var(--primary);
  }

  .overview-card p {
    color: var(--text-secondary);
    line-height: 1.6;
    font-size: 0.95rem;
  }

  /* Timeline Styles */
  .timeline {
    position: relative;
    padding-left: 2rem;
  }

  .timeline-line {
    position: absolute;
    left: 28px;
    top: 20px;
    bottom: 40px;
    width: 2px;
    background: linear-gradient(to bottom, rgba(201, 160, 94, 0.5), rgba(201, 160, 94, 0.1));
  }

  .timeline-node {
    position: relative;
    display: flex;
    gap: 2rem;
    margin-bottom: 3rem;
    opacity: 0;
    animation: slideUpFade 0.6s ease forwards;
  }

  .timeline-node:last-child {
    margin-bottom: 0;
  }

  .node-marker {
    position: relative;
    z-index: 2;
    padding-top: 1.5rem;
  }

  .node-dot {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--bg-primary);
    border: 3px solid var(--primary);
    box-shadow: 0 0 10px rgba(201, 160, 94, 0.4);
    transition: all var(--transition-fast);
  }

  .timeline-node:hover .node-dot {
    background: var(--primary);
    transform: scale(1.2);
    box-shadow: 0 0 15px rgba(201, 160, 94, 0.8);
  }

  .node-content {
    flex: 1;
    padding: 2rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  }

  .node-content:hover {
    transform: translateX(10px);
    border-color: rgba(201, 160, 94, 0.3);
  }

  .node-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .node-header h3 {
    margin: 0;
    font-size: 1.4rem;
  }

  .proficiency-badge {
    background: rgba(0,0,0,0.3);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    color: var(--text-secondary);
    border: 1px solid rgba(255,255,255,0.05);
  }

  .proficiency-badge strong {
    color: var(--primary);
  }

  .node-content p {
    color: var(--text-secondary);
    margin-bottom: 2rem;
    line-height: 1.6;
  }

  .node-actions {
    display: flex;
    justify-content: flex-end;
  }

  .node-actions .btn {
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
  }

  .empty-state {
    padding: 4rem 2rem;
  }
  
  .empty-state h3 {
    font-size: 1.5rem;
  }

  @media (max-width: 992px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
      gap: 3rem;
    }

    .dashboard-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 1.5rem;
    }
    
    .timeline {
      padding-left: 0;
    }
    
    .timeline-line {
      left: 8px;
    }
    
    .timeline-node {
      gap: 1rem;
    }
    
    .node-content {
      padding: 1.5rem;
    }
  }

  .status-screen.error-state {
    color: var(--danger);
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
  }
</style>
