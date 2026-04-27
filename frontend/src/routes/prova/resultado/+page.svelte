<script lang="ts">
  import { onMount } from "svelte";
  import { fly, fade, scale } from "svelte/transition";
  import axios from "axios";
  import { formatPedagogicalCode } from "$lib/utils";
  import LoadingSpinner from "$lib/components/LoadingSpinner.svelte";
  import { page } from "$app/stores";

  let report = null;
  let loading = true;
  let error = null;

  // Mapeamento de cores por área
  const areaColors = {
    "Matemática e suas Tecnologias": "#C9A05E",
    "Ciências da Natureza e suas Tecnologias": "#22C55E",
    "Ciências Humanas e suas Tecnologias": "#EF4444",
    "Linguagens, Códigos e suas Tecnologias": "#3B82F6",
    Geral: "#A3A3A3",
  };

  onMount(async () => {
    try {
      const id = $page.url.searchParams.get("id");
      const url = id 
        ? `http://localhost:8000/api/v1/assessment-report/history/${id}`
        : "http://localhost:8000/api/v1/assessment-report/report";
        
      const res = await axios.get(url, {
        withCredentials: true
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
    if (score >= 0.7) return "var(--success)";
    if (score >= 0.4) return "var(--warning)";
    return "var(--danger)";
  }

  // Agrupar habilidades por área
  $: groupedSkills = report?.proficiencies
    ? report.proficiencies.reduce((acc, p) => {
        const area = p.area || "Geral";
        if (!acc[area]) acc[area] = [];
        acc[area].push(p);
        return acc;
      }, {})
    : {};
</script>

<div class="results-page">
  {#if loading}
    <div class="status-screen" out:fade>
      <LoadingSpinner />
      <h2>Estamos analisando a sua trilha...</h2>
      <p>Cruzando dados de competências e habilidades para gerar seu plano.</p>
    </div>
  {:else if error}
    <div class="status-screen error">
      <h2>Ops! Algo deu errado.</h2>
      <p>{error}</p>
      <a href="/prova" class="btn btn-outline">Tentar Novamente</a>
    </div>
  {:else if report && report.status === "pending"}
    <div class="status-screen pending">
      <h2>Seu diagnóstico está sendo gerado.</h2>
      <p>
        Isso acontece quando você ainda não completou questões suficientes ou o
        sistema está processando seu grafo de conhecimento.
      </p>
      <a href="/prova" class="btn btn-primary">Voltar para a Prova</a>
    </div>
  {:else if report}
    <div class="dashboard container" in:fade={{ duration: 800 }}>
      <header class="dashboard-header text-center">
        <span class="eyebrow">Resultado Oficial</span>
        <h1 class="text-gradient">Seu Mapa de Proficiência</h1>
      </header>

      <!-- AI Insight Highlight -->
      {#if report.analysis}
        <section class="ai-insight-card glass-panel animate-slide-up">
          <div class="insight-header">
            <div class="ai-badge">ANÁLISE ESTRATÉGICA</div>
            <h2>{report.analysis.title}</h2>
          </div>
          <p class="summary">{report.analysis.summary}</p>

          <div class="points-grid">
            <div class="point-box strengths">
              <h3><span class="dot"></span> Pontos de Domínio</h3>
              <ul>
                {#each report.analysis.strengths || [] as s}
                  <li>{s}</li>
                {/each}
              </ul>
            </div>
            <div class="point-box gaps">
              <h3><span class="dot"></span> Lacunas Críticas</h3>
              <ul>
                {#each report.analysis.weaknesses || [] as w}
                  <li>{w}</li>
                {/each}
              </ul>
            </div>
          </div>

          <div class="action-footer">
            <div class="plan-text">
              <strong>Estratégia Recomendada:</strong>
              <p>{report.analysis.action_plan}</p>
            </div>
          </div>
        </section>
      {:else}
        <div class="glass-panel text-center p-8 animate-pulse">
          <p>Gerando análise pedagógica personalizada...</p>
        </div>
      {/if}

      <!-- Stats Summary -->
      <div class="quick-stats">
        <div class="glass-card stat-card" in:scale={{ delay: 200 }}>
          <span class="val"
            >{(report.summary_stats.average_score * 100).toFixed(0)}%</span
          >
          <span class="lab">Domínio Médio</span>
        </div>
        <div class="glass-card stat-card" in:scale={{ delay: 400 }}>
          <span class="val">{report.summary_stats.total_skills_mapped}</span>
          <span class="lab">Habilidades Mapeadas</span>
        </div>
      </div>

      <!-- Skills Detail -->
      <section class="skills-detail">
        <h2 class="section-title">Detalhamento Pedagógico</h2>

        {#each Object.entries(groupedSkills) as [area, skills]}
          <div class="area-group">
            <h3
              class="area-title"
              style="border-left-color: {areaColors[area] || '#fff'}"
            >
              {area}
            </h3>
            <div class="skills-grid">
              {#each skills as skill}
                <div class="skill-item glass-card">
                  <div class="skill-info">
                    <span class="code">{formatPedagogicalCode(skill.id)}</span>
                    <span class="score" style="color: {getScoreColor(skill.score)}">
                      {(skill.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p class="desc">{skill.description}</p>
                  <div class="bar-bg">
                    <div
                      class="bar-fill"
                      style="width: {skill.score *
                        100}%; background: {areaColors[area] ||
                        'var(--primary)'}"
                    ></div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </section>

      <footer class="dash-footer">
        <a href="/dashboard" class="btn btn-primary btn-lg"
          >Acessar Meu Painel Completo</a
        >
      </footer>
    </div>
  {/if}
</div>

<style>
  .results-page {
    padding-bottom: 6rem;
    width: 100%;
  }

  .status-screen {
    height: 80vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 1.5rem;
  }

  .dashboard {
    display: flex;
    flex-direction: column;
    gap: 3.5rem;
    padding: 0 1.5rem;
    max-width: 1000px;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
  }

  .dashboard-header h1 {
    font-size: clamp(2rem, 5vw, 3.5rem);
    margin-top: 1rem;
    line-height: 1.2;
  }

  .eyebrow {
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.3em;
    font-size: 0.75rem;
    font-weight: 700;
  }

  /* AI Insight Card */
  .ai-insight-card {
    padding: 3rem;
    position: relative;
    overflow: hidden;
    border-radius: 1.5rem;
  }

  .ai-badge {
    background: var(--primary);
    color: var(--text-dark);
    font-size: 0.65rem;
    font-weight: 800;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    margin-bottom: 1.25rem;
    display: inline-block;
    letter-spacing: 0.05em;
  }

  .summary {
    font-size: 1.15rem;
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
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 700;
  }

  .point-box.strengths h3 {
    color: var(--success);
  }
  .point-box.gaps h3 {
    color: var(--warning);
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .point-box ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .point-box li {
    font-size: 0.95rem;
    color: var(--text-secondary);
    padding-left: 1.5rem;
    position: relative;
    line-height: 1.5;
  }

  .point-box li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--primary);
    opacity: 0.6;
  }

  .action-footer {
    background: rgba(201, 160, 94, 0.05);
    padding: 2rem;
    border-radius: 1.25rem;
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
    border-left: 4px solid var(--primary);
  }

  .plan-text strong {
    display: block;
    color: var(--primary);
    font-size: 0.85rem;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
  }
  .plan-text p {
    font-size: 1rem;
    color: var(--text-secondary);
    line-height: 1.6;
  }

  /* Quick Stats */
  .quick-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .stat-card {
    text-align: center;
    padding: 2.5rem;
    border-radius: 1.5rem;
  }

  .stat-card .val {
    font-size: 3rem;
    font-weight: 800;
    color: var(--primary);
    display: block;
    font-family: var(--font-serif);
    margin-bottom: 0.25rem;
  }
  .stat-card .lab {
    font-size: 0.75rem;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
  }

  /* Area Groups & Skills */
  .skills-detail {
    margin-top: 2rem;
  }

  .section-title {
    font-size: 2rem;
    margin-bottom: 3rem;
    text-align: center;
  }

  .area-group {
    margin-bottom: 4rem;
  }

  .area-title {
    font-size: 1.1rem;
    padding-left: 1.25rem;
    border-left: 4px solid;
    margin-bottom: 2.5rem;
    font-weight: 700;
  }

  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .skill-item {
    padding: 2rem;
    border-radius: 1.5rem;
  }

  .skill-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
  }

  .code {
    font-weight: 700;
    color: var(--primary);
    font-size: 0.85rem;
  }
  .score {
    font-weight: 800;
    font-size: 1.1rem;
  }
  .desc {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .bar-bg {
    height: 4px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 2px;
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    transition: width 1s ease;
  }

  .dash-footer {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  @keyframes pulse {
    0%,
    100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }

  @media (max-width: 768px) {
    .dashboard {
      padding: 0 1rem;
      gap: 2.5rem;
    }

    .ai-insight-card {
      padding: 2.25rem 1.5rem;
    }

    .summary {
      font-size: 1.05rem;
    }

    .points-grid {
      grid-template-columns: 1fr;
      gap: 2.5rem;
    }

    .quick-stats {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .stat-card {
      padding: 2rem;
    }

    .stat-card .val {
      font-size: 2.5rem;
    }

    .skills-grid {
      grid-template-columns: 1fr;
    }

    .skill-item {
      padding: 1.5rem;
    }
    
    .area-group {
      margin-bottom: 3rem;
    }

    .area-title {
      font-size: 1.1rem;
      margin-bottom: 1.5rem;
    }

    .section-title {
      font-size: 1.75rem;
    }
  }
</style>
