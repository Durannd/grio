<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let learningPath: Array<{concept_name: string, description: string, score: number}> = [];
  let user: any = null;
  let loading = true;

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

      loading = false;
    } catch (error) {
      console.error("Error loading dashboard:", error);
      loading = false;
    }
  });

  function logout() {
    localStorage.removeItem("token");
    goto("/login");
  }
</script>

<div class="dashboard-container">
  {#if loading}
    <div class="loading-state animate-slide-up stagger-1">
      <div class="spinner"></div>
      <p>Consultando o oráculo...</p>
    </div>
  {:else}
    <div class="dashboard-grid">
      <aside class="dashboard-sidebar animate-slide-up stagger-1">
        <header class="dashboard-header">
          <div class="welcome">
            <h1>Olá, <span class="text-gradient">{user.name}</span></h1>
            <p>Esta é a sua Trilha de Conhecimento.</p>
          </div>
          <div class="sidebar-actions">
            <button class="btn btn-outline" on:click={logout}>Desconectar</button>
            <a href="/prova" class="retake-link">Refazer Nivelamento</a>
          </div>
        </header>

        <div class="glass-card overview-card">
           <h3>Seu Progresso</h3>
           <p>Continue estudando os módulos recomendados para fortalecer sua base e avançar nos estudos do vestibular.</p>
        </div>
      </aside>

      <section class="path-section animate-slide-up stagger-2">
        <div class="section-title">
          <h2>Próximos Passos</h2>
        </div>
        
      {#if learningPath.length === 0}
        <div class="glass-card text-center empty-state">
          <h3>Sua jornada ainda não começou</h3>
          <p>Faça a prova de nivelamento para descobrirmos por onde você deve começar.</p>
          <a href="/prova" class="btn btn-primary" style="margin-top: 1.5rem;">Iniciar Nivelamento</a>
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
                  <h3>{concept.concept_name}</h3>
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
  .dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 4rem 2rem;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 4rem;
    align-items: start;
  }

  .loading-state {
    text-align: center;
    padding: 6rem 0;
    color: var(--primary);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(201, 160, 94, 0.2);
    border-top-color: var(--primary);
    border-radius: 50%;
    margin: 0 auto 1.5rem;
    animation: spin 1s linear infinite;
  }

  @keyframes spin { 100% { transform: rotate(360deg); } }

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
</style>
