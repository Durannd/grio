<script>
  import { onMount } from 'svelte';
  let isVisible = false;
  onMount(() => isVisible = true);
</script>

<div class="sobre-page container section-padding">
  <header class="text-center mb-16">
    <span class="eyebrow">A Essência</span>
    <h1 class="text-gradient">O Conceito Griô</h1>
    <p class="lead max-w-2xl mx-auto">Mais do que uma plataforma, um resgate cultural aplicado à educação do século XXI.</p>
  </header>

  <div class="story-grid">
    <div class="glass-panel story-card animate-slide-up stagger-1">
      <h2>O Significado</h2>
      <p>Na África Ocidental, os <strong>Griôs</strong> (ou Jali) são contadores de histórias, genealogistas, poetas e músicos. Eles são os pilares da tradição oral, responsáveis por transmitir o conhecimento das gerações passadas para as futuras.</p>
      <p>Nosso projeto herda esse nome pois acreditamos que a tecnologia deve atuar como um Griô digital: identificando onde sua história começou (diagnóstico) e guiando você até o próximo capítulo (aprovação).</p>
    </div>

    <div class="glass-panel story-card animate-slide-up stagger-2">
      <h2>Nossa Motivação</h2>
      <p>O acesso ao ensino superior no Brasil ainda é um abismo para muitos. O excesso de conteúdo e a falta de direção tornam o estudo ineficiente e exaustivo.</p>
      <p>O <strong>Griô</strong> nasceu para democratizar o acesso à análise de desempenho de alto nível, antes restrita a cursinhos de elite, usando inteligência artificial para personalizar cada etapa da preparação.</p>
    </div>
  </div>

  <section class="tech-stack mt-24">
    <h2 class="text-center mb-12">Tecnologia de Vanguarda</h2>
    <div class="tech-grid">
      <div class="tech-item glass-card">
        <h3>FastAPI</h3>
        <p>Backend de alta performance para processamento assíncrono.</p>
      </div>
      <div class="tech-item glass-card">
        <h3>Neo4j</h3>
        <p>Banco de grafos para mapear conexões complexas entre habilidades.</p>
      </div>
      <div class="tech-item glass-card">
        <h3>Gemini IA</h3>
        <p>Inteligência generativa para análise pedagógica personalizada.</p>
      </div>
      <div class="tech-item glass-card">
        <h3>SvelteKit</h3>
        <p>Frontend reativo para uma experiência de usuário fluida e rápida.</p>
      </div>
    </div>
  </section>
</div>

<style>
  .sobre-page {
    max-width: 1000px;
  }

  .eyebrow {
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.3em;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: block;
  }

  .lead {
    font-size: 1.2rem;
    color: var(--text-secondary);
  }

  .story-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .story-card h2 {
    color: var(--primary-light);
    margin-bottom: 1.5rem;
  }

  .story-card p {
    color: var(--text-secondary);
    margin-bottom: 1rem;
    line-height: 1.7;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .tech-item h3 {
    font-family: var(--font-sans);
    font-size: 1.1rem;
    color: var(--primary);
    margin-bottom: 0.5rem;
  }

  .tech-item p {
    font-size: 0.9rem;
    color: var(--text-secondary);
  }

  .max-w-2xl { max-width: 42rem; }
  .mx-auto { margin-left: auto; margin-right: auto; }
  .mt-24 { margin-top: 6rem; }
  .mb-16 { margin-bottom: 4rem; }
  .mb-12 { margin-bottom: 3rem; }

  @media (max-width: 768px) {
    .story-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
