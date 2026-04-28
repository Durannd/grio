<script>
  import { onMount } from 'svelte';
  let isVisible = false;
  onMount(() => isVisible = true);
</script>

<div class="sobre-page container section-padding">
  <header class="text-center mb-16">
    <span class="eyebrow">A Inteligência</span>
    <h1 class="text-gradient">O Ecossistema Griô</h1>
    <p class="lead max-w-2xl mx-auto">Tecnologia pedagógica de ponta para transformar dados em aprovação.</p>
  </header>

  <div class="story-grid">
    <div class="glass-panel story-card animate-slide-up stagger-1">
      <h2>Inteligência Pedagógica</h2>
      <p>O <strong>Griô</strong> utiliza algoritmos avançados de análise de proficiência para mapear o conhecimento do estudante de forma granular. Nossa plataforma não apenas aplica testes; ela compreende os padrões de aprendizagem para oferecer uma jornada otimizada.</p>
      <p>Através de uma arquitetura de dados moderna, transformamos cada interação em insights acionáveis, garantindo que o tempo de estudo seja direcionado exatamente para onde há maior potencial de crescimento.</p>
    </div>

    <div class="glass-panel story-card animate-slide-up stagger-2">
      <h2>Aceleração Acadêmica</h2>
      <p>Em um cenário de alta competitividade, a eficiência é o diferencial. O excesso de conteúdo e a falta de direção tornam o estudo exaustivo e muitas vezes improfícuo.</p>
      <p>Nossa missão é democratizar o acesso à análise de desempenho de alto nível. Usamos inteligência artificial para personalizar cada etapa da preparação, reduzindo o caminho até o ingresso no ensino superior.</p>
    </div>
  </div>

  <section class="tech-stack mt-24">
    <h2 class="text-center mb-12">Nossa Infraestrutura de Inteligência</h2>
    <div class="tech-grid">
      <div class="tech-item glass-card">
        <h3>Processamento em Tempo Real</h3>
        <p>Arquitetura otimizada para fornecer feedback imediato e personalizado.</p>
      </div>
      <div class="tech-item glass-card">
        <h3>Grafos de Conhecimento</h3>
        <p>Mapeamento não-linear que compreende as interconexões entre competências.</p>
      </div>
      <div class="tech-item glass-card">
        <h3>Modelos Generativos</h3>
        <p>Inteligência artificial avançada para mentorias socráticas e análise pedagógica.</p>
      </div>
      <div class="tech-item glass-card">
        <h3>Interface Adaptativa</h3>
        <p>Design focado na redução da carga cognitiva e na fluidez do aprendizado.</p>
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
