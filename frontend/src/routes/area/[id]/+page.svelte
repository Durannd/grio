<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { formatPedagogicalCode } from '$lib/utils';

  let learningPath: Array<{concept_name: string, description: string, score: number, is_inferred?: boolean}> = [];
  let user: any = null;
  let loading = true;
  let errorMessage = "";
  
  $: areaId = $page.params.id;
  $: areaLabel = areaId === 'MT' ? 'Matemática e suas Tecnologias' : areaId === 'CN' ? 'Ciências da Natureza e suas Tecnologias' : areaId === 'LC' ? 'Linguagens, Códigos e suas Tecnologias' : 'Ciências Humanas e suas Tecnologias';
  
  $: areaConcepts = learningPath.filter(c => c.concept_name.startsWith(areaId));
  $: areaScore = areaConcepts.length > 0 ? areaConcepts.reduce((acc, c) => acc + c.score, 0) / areaConcepts.length : 0;

  onMount(async () => {
    try {
      const fetchOptions = { credentials: "include" };
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
      loading = false;
    } catch (error) {
      console.error("Error loading area:", error);
      errorMessage = "Houve um erro ao carregar os dados desta área.";
      loading = false;
    }
  });
</script>

<div class="area-wrapper">
  {#if loading}
    <div class="status-screen" out:fade>
      <div class="loader-visual">
        <div class="orbit"></div>
        <div class="center-glow"></div>
      </div>
      <p>Sincronizando dados da área...</p>
    </div>
  {:else if errorMessage}
    <div class="status-screen error-state">
      <p>{errorMessage}</p>
      <button class="btn btn-outline mt-4" on:click={() => window.location.reload()}>Tentar Novamente</button>
    </div>
  {:else}
    <div class="area-header animate-fade-in">
      <div>
        <a href="/dashboard" class="back-link">← Voltar ao Dashboard</a>
        <h1 class="page-title text-gradient">{areaLabel}</h1>
        <div class="area-score-wrap">
          <span class="area-score">{(areaScore * 100).toFixed(0)}%</span>
          <span class="area-label">Proficiência na Área</span>
        </div>
      </div>
      <div class="header-actions">
        <a href="/prova?area={areaId}" class="btn btn-primary">
          Novo Diagnóstico Específico
        </a>
      </div>
    </div>

    <div class="technical-section" in:fly={{ y: 10, duration: 400 }}>
      <div class="section-header">
        <h2 class="section-title">Habilidades e Competências ({areaId})</h2>
      </div>

      {#if areaConcepts.length === 0}
        <div class="glass-panel empty-state">
          <h3>Mapeamento Pendente</h3>
          <p>Ainda não temos dados suficientes para traçar sua proficiência nesta área.</p>
        </div>
      {:else}
        <div class="proficiency-list">
          {#each areaConcepts as concept (concept.concept_name)}
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
      {/if}
    </div>
  {/if}
</div>

<style>
  .area-wrapper {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }
  .back-link { color: rgba(255,255,255,0.6); text-decoration: none; display: inline-block; margin-bottom: 1rem; }
  .back-link:hover { color: #FFF; }
  .status-screen { height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
  .loader-visual { position: relative; width: 60px; height: 60px; margin-bottom: 2rem; }
  .orbit { position: absolute; inset: 0; border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 50%; border-top-color: #FFF; animation: spin 1.5s linear infinite; }
  .center-glow { position: absolute; inset: 30%; background: #FFF; filter: blur(10px); border-radius: 50%; animation: pulse 2s ease-in-out infinite; }
  @keyframes spin { 100% { transform: rotate(360deg); } }
  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
  .error-state { color: #EF4444; }
  .area-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
  .page-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.02em; color: #FFF; }
  .area-score-wrap { display: flex; align-items: baseline; gap: 0.5rem; }
  .area-score { font-size: 2rem; font-weight: 800; color: #FFF; }
  .area-label { font-size: 0.85rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.05em; }
  .btn { display: inline-flex; align-items: center; justify-content: center; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 600; text-decoration: none; transition: all 0.2s ease; cursor: pointer; border: none; }
  .btn-primary { background: #FFF; color: #000; }
  .btn-primary:hover { background: rgba(255,255,255,0.8); }
  .btn-outline { background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #FFF; }
  .btn-outline:hover { background: rgba(255,255,255,0.1); }
  .mt-4 { margin-top: 1rem; }
  .glass-panel { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 2rem; }
  .section-title { font-size: 1.5rem; font-weight: 600; color: #FFF; margin-bottom: 1.5rem; }
  .proficiency-list { display: flex; flex-direction: column; gap: 1.25rem; }
  .proficiency-item { padding: 1.5rem; transition: transform 0.2s ease, border-color 0.2s ease; }
  .proficiency-item:hover { transform: translateX(4px); border-color: rgba(255,255,255,0.15); }
  .prof-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
  .prof-title-wrap { display: flex; flex-direction: column; gap: 0.25rem; }
  .prof-code { font-size: 0.8rem; font-family: monospace; background: rgba(255,255,255,0.1); color: #FFF; padding: 0.15rem 0.5rem; border-radius: 4px; width: fit-content; }
  .prof-title-wrap h4 { font-size: 1.1rem; font-weight: 600; color: #FFF; }
  .prof-score { font-weight: 700; font-size: 1rem; padding: 0.3rem 0.6rem; border-radius: 4px; background: rgba(255,255,255,0.05); }
  .prof-score.high { color: #34D399; }
  .prof-score.med { color: #FBBF24; }
  .prof-score.low { color: #F87171; }
  .inferred-badge { font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.5rem; border-radius: 4px; background: rgba(255,255,255,0.1); color: #FFF; letter-spacing: 0.05em; }
  .prof-desc { font-size: 0.95rem; color: rgba(255,255,255,0.6); margin-bottom: 1.25rem; line-height: 1.6; }
  .progress-bar-container { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
  .progress-bar { height: 100%; border-radius: 3px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
  .empty-state { text-align: center; }
  .empty-state h3 { margin-bottom: 0.5rem; font-size: 1.25rem; color: #FFF; }
  .empty-state p { color: rgba(255,255,255,0.6); font-size: 0.95rem; }
  @media (max-width: 768px) { .area-header { flex-direction: column; align-items: flex-start; gap: 1.5rem; } }
</style>