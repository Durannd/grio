<script lang="ts">
  import { onMount } from 'svelte';
  import { fly, fade, scale } from 'svelte/transition';
  import axios from 'axios';

  let report = null;
  let loading = true;
  let error = null;

  // Mapeamento de cores por área
  const areaColors = {
    'Matemática e suas Tecnologias': '#C9A05E',
    'Ciências da Natureza e suas Tecnologias': '#22C55E',
    'Ciências Humanas e suas Tecnologias': '#EF4444',
    'Linguagens, Códigos e suas Tecnologias': '#3B82F6',
    'Geral': '#A3A3A3'
  };

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

  // Agrupar habilidades por área
  $: groupedSkills = report?.proficiencies ? report.proficiencies.reduce((acc, p) => {
    const area = p.area || 'Geral';
    if (!acc[area]) acc[area] = [];
    acc[area].push(p);
    return acc;
  }, {}) : {};
</script>

<div class="results-page">
  {#if loading}
    <div class="status-screen" out:fade>
      <div class="loader-visual">
        <div class="orbit"></div>
        <div class="center-glow"></div>
      </div>
      <h2>O Mentor Griô está analisando sua trilha...</h2>
      <p>Cruzando dados de competências e habilidades para gerar seu plano.</p>
    </div>
  {:else if error}
    <div class="status-screen error">
      <div class="icon">⚠️</div>
      <h2>Ops! Algo deu errado.</h2>
      <p>{error}</p>
      <a href="/prova" class="btn btn-outline">Tentar Novamente</a>
    </div>
  {:else if report && report.status === 'pending'}
    <div class="status-screen pending">
      <div class="icon">⏳</div>
      <h2>Seu diagnóstico está sendo gerado.</h2>
      <p>Isso acontece quando você ainda não completou questões suficientes ou o sistema está processando seu grafo de conhecimento.</p>
      <a href="/prova" class="btn btn-primary">Voltar para a Prova</a>
    </div>
  {:else if report}
    <div class="dashboard container" in:fade={{ duration: 800 }}>
      <header class="dashboard-header text-center">
        <span class="eyebrow">Resultado Oficial</span>
        <h1 class="text-gradient">Seu Mapa de Proficiência</h1>
      </header>

      <!-- AI Insight Highlight -->
      <section class="ai-insight-card glass-panel animate-slide-up">
        <div class="insight-header">
          <div class="ai-badge">IA MENTOR</div>
          <h2>{report.analysis.title}</h2>
        </div>
        <p class="summary">{report.analysis.summary}</p>
        
        <div class="points-grid">
          <div class="point-box strengths">
            <h3><span class="dot"></span> Pontos de Domínio</h3>
            <ul>
              {#each report.analysis.strengths as s}
                <li>{s}</li>
              {/each}
            </ul>
          </div>
          <div class="point-box gaps">
            <h3><span class="dot"></span> Lacunas Críticas</h3>
            <ul>
              {#each report.analysis.weaknesses as w}
                <li>{w}</li>
              {/each}
            </ul>
          </div>
        </div>

        <div class="action-footer">
          <div class="plan-icon">🎯</div>
          <div class="plan-text">
            <strong>Estratégia Recomendada:</strong>
            <p>{report.analysis.action_plan}</p>
          </div>
        </div>
      </section>

      <!-- Stats Summary -->
      <div class="quick-stats">
        <div class="glass-card stat-card" in:scale={{delay: 200}}>
          <span class="val">{(report.summary_stats.average_score * 100).toFixed(0)}%</span>
          <span class="lab">Domínio Médio</span>
        </div>
        <div class="glass-card stat-card" in:scale={{delay: 400}}>
          <span class="val">{report.summary_stats.total_skills_mapped}</span>
          <span class="lab">Habilidades Mapeadas</span>
        </div>
      </div>

      <!-- Skills Detail -->
      <section class="skills-detail">
        <h2 class="section-title">Detalhamento Pedagógico</h2>
        
        {#each Object.entries(groupedSkills) as [area, skills]}
          <div class="area-group">
            <h3 class="area-title" style="border-left-color: {areaColors[area] || '#fff'}">{area}</h3>
            <div class="skills-grid">
              {#each skills as skill}
                <div class="skill-item glass-card">
                  <div class="skill-info">
                    <span class="code">{skill.id}</span>
                    <span class="score" style="color: {getScoreColor(skill.score)}">
                      {(skill.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p class="desc">{skill.description}</p>
                  <div class="bar-bg">
                    <div class="bar-fill" style="width: {skill.score * 100}%; background: {areaColors[area] || 'var(--primary)'}"></div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </section>

      <footer class="dash-footer">
        <a href="/dashboard" class="btn btn-primary btn-lg">Acessar Meu Painel Completo</a>
      </footer>
    </div>
  {/if}
</div>

<style>
  .results-page {
    min-height: 100vh;
    padding-bottom: 6rem;
  }

  .status-screen {
    height: 80vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
  }

  .loader-visual {
    position: relative;
    width: 100px;
    height: 100px;
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
    filter: blur(15px);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
  }

  .dashboard {
    display: flex;
    flex-direction: column;
    gap: 4rem;
  }

  .eyebrow {
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.3em;
    font-size: 0.8rem;
    font-weight: 700;
  }

  /* AI Insight Card */
  .ai-insight-card {
    padding: 3.5rem;
    position: relative;
    overflow: hidden;
  }

  .ai-badge {
    background: var(--primary);
    color: var(--text-dark);
    font-size: 0.7rem;
    font-weight: 800;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    display: inline-block;
  }

  .summary {
    font-size: 1.2rem;
    color: var(--text-primary);
    line-height: 1.6;
    margin-bottom: 3rem;
  }

  .points-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    margin-bottom: 3rem;
  }

  .point-box h3 {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .point-box.strengths h3 { color: var(--success); }
  .point-box.gaps h3 { color: var(--warning); }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
  }

  .point-box ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .point-box li {
    font-size: 0.95rem;
    color: var(--text-secondary);
    padding-left: 1.5rem;
    position: relative;
  }

  .point-box li::before {
    content: "•";
    position: absolute;
    left: 0;
    color: var(--primary);
  }

  .action-footer {
    background: rgba(201, 160, 94, 0.05);
    padding: 2rem;
    border-radius: 1rem;
    display: flex;
    gap: 1.5rem;
    align-items: center;
    border-left: 4px solid var(--primary);
  }

  .plan-icon { font-size: 2rem; }
  .plan-text strong { display: block; color: var(--primary); font-size: 0.8rem; margin-bottom: 0.3rem; }
  .plan-text p { font-size: 0.95rem; color: var(--text-secondary); }

  /* Quick Stats */
  .quick-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .stat-card {
    text-align: center;
    padding: 2.5rem;
  }

  .stat-card .val { font-size: 3rem; font-weight: 700; color: var(--text-primary); display: block; }
  .stat-card .lab { font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; }

  /* Skills Detail */
  .area-group {
    margin-bottom: 4rem;
  }

  .area-title {
    font-size: 1.2rem;
    padding-left: 1.5rem;
    border-left: 4px solid;
    margin-bottom: 2rem;
  }

  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .skill-item {
    padding: 1.5rem;
  }

  .skill-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.8rem;
  }

  .code { font-weight: 700; color: var(--primary); font-size: 0.8rem; }
  .score { font-weight: 700; }
  .desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1.2rem; }

  .bar-bg { height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden; }
  .bar-fill { height: 100%; transition: width 1s ease; }

  .dash-footer { display: flex; justify-content: center; margin-top: 2rem; }

  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

  @media (max-width: 768px) {
    .points-grid, .quick-stats { grid-template-columns: 1fr; }
    .ai-insight-card { padding: 2rem; }
  }
</style>
