<script lang="ts">
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import axios from 'axios';

  let report = null;
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://localhost:8000/api/v1/assessment-report/report', {
        headers: { Authorization: `Bearer ${token}` }
      });
      report = res.data;
    } catch (e) {
      error = "Não foi possível carregar seu diagnóstico.";
      console.error(e);
    } finally {
      loading = false;
    }
  });

  function getScoreColor(score: number) {
    if (score >= 0.7) return 'var(--success)';
    if (score >= 0.4) return 'var(--warning)';
    return 'var(--danger)';
  }
</script>

<div class="results-container">
  {#if loading}
    <div class="loading-state" out:fade>
      <div class="spinner"></div>
      <p>Processando análise estatística do seu desempenho...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <p>{error}</p>
      <a href="/prova" class="btn">Tentar Novamente</a>
    </div>
  {:else if report}
    <div class="content-wrapper" in:fly={{ y: 20, duration: 800 }}>
      <header class="results-header">
        <h1 class="text-gradient">Diagnóstico de Desempenho</h1>
        <p class="subtitle">Análise técnica detalhada baseada nas competências oficiais do ENEM.</p>
      </header>

      <section class="ai-analysis-card glass-card">
        <div class="card-header">
          <span class="icon">📊</span>
          <h2>{report.analysis.title || 'Análise de Proficiência'}</h2>
        </div>
        
        <div class="analysis-content">
          <div class="summary-section">
            <p>{report.analysis.summary}</p>
          </div>

          <div class="insights-grid">
            <div class="insight-col">
              <h4 class="text-success">Pontos de Domínio</h4>
              <ul>
                {#each report.analysis.strengths as strength}
                  <li>{strength}</li>
                {/each}
              </ul>
            </div>
            <div class="insight-col">
              <h4 class="text-warning">Oportunidades de Melhoria</h4>
              <ul>
                {#each report.analysis.weaknesses as weakness}
                  <li>{weakness}</li>
                {/each}
              </ul>
            </div>
          </div>

          <div class="action-plan-box">
            <strong>Estratégia Recomendada:</strong>
            <p>{report.analysis.action_plan}</p>
          </div>
        </div>
      </section>

      <div class="stats-grid">
        <div class="stat-item glass-card">
          <span class="label">Habilidades Mapeadas</span>
          <span class="value">{report.summary_stats.total_skills_mapped}</span>
        </div>
        <div class="stat-item glass-card">
          <span class="label">Proficiência Média</span>
          <span class="value">{(report.summary_stats.average_score * 100).toFixed(0)}%</span>
        </div>
      </div>

      <section class="skills-section">
        <h3>Detalhamento por Habilidade</h3>
        <div class="skills-grid">
          {#each report.proficiencies.filter(p => p.type === 'Skill') as skill}
            <div class="skill-card glass-card">
              <div class="skill-header">
                <span class="skill-id">{skill.id}</span>
                <span class="score-percent" style="color: {getScoreColor(skill.score)}">
                  {(skill.score * 100).toFixed(0)}%
                </span>
              </div>
              <p class="skill-desc">{skill.description}</p>
              <div class="progress-bg">
                <div class="progress-fill" style="width: {skill.score * 100}%; background: {getScoreColor(skill.score)}"></div>
              </div>
            </div>
          {/each}
        </div>
      </section>

      <footer class="results-footer">
        <button class="btn btn-primary btn-large">Iniciar Minha Trilha de Estudos</button>
      </footer>
    </div>
  {/if}
</div>

<style>
  .results-container {
    min-height: 100vh;
    padding: 4rem 2rem;
    background: radial-gradient(circle at top right, rgba(201, 160, 94, 0.05), transparent),
                radial-gradient(circle at bottom left, rgba(201, 160, 94, 0.02), transparent);
  }

  .content-wrapper {
    max-width: 1000px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 3rem;
  }

  .results-header {
    text-align: center;
  }

  .results-header h1 {
    font-size: 3.5rem;
    margin-bottom: 1rem;
  }

  .ai-analysis-card {
    padding: 2.5rem;
    border-radius: 2rem;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .card-header h2 {
    font-size: 1.5rem;
    color: var(--primary);
  }

  .analysis-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .summary-section p {
    font-size: 1.15rem;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  .insights-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 1rem;
  }

  .insight-col h4 {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .insight-col ul {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .insight-col li {
    font-size: 0.95rem;
    color: var(--text-primary);
    padding-left: 1.25rem;
    position: relative;
  }

  .insight-col li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--primary);
  }

  .action-plan-box {
    padding: 1.5rem;
    border-left: 4px solid var(--primary);
    background: rgba(201, 160, 94, 0.05);
    border-radius: 0 1rem 1rem 0;
  }

  .action-plan-box strong {
    display: block;
    color: var(--primary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
  }

  .text-success { color: #4ade80; }
  .text-warning { color: #fbbf24; }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .stat-item {
    padding: 2rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-item .label {
    font-size: 0.9rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .stat-item .value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
  }

  .skills-section h3 {
    font-size: 1.8rem;
    margin-bottom: 2rem;
    color: var(--text-primary);
  }

  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .skill-card {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .skill-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .skill-id {
    font-weight: 700;
    color: var(--primary);
  }

  .skill-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
    flex-grow: 1;
  }

  .progress-bg {
    height: 4px;
    background: rgba(255,255,255,0.05);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    transition: width 1s ease-out;
  }

  .results-footer {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
  }

  .btn-large {
    padding: 1.25rem 3rem;
    font-size: 1.2rem;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 60vh;
    gap: 2rem;
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 3px solid rgba(201, 160, 94, 0.1);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
