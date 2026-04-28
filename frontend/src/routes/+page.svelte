<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { user } from '$lib/stores/userStore';

  let isLoaded = false;

  $: hasCompleted = $user && ($user.is_diagnostic_completed === 1 || $user.is_diagnostic_completed === true);
  $: diagnosticLink = hasCompleted ? '/dashboard' : '/prova';
  $: diagnosticText = hasCompleted ? 'Ir para o Dashboard' : 'Começar Agora';
  
  onMount(() => {
    isLoaded = true;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.15 });
    
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  });
</script>

<div class="home-container">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="hero-bg">
      <div class="overlay"></div>
    </div>
    
    <div class="hero-content container">
      {#if isLoaded}
        <div in:fly={{ y: 50, duration: 1000 }} class="hero-text">
          <span class="eyebrow">Bem-vindo ao Futuro do Saber</span>
          <h1 class="text-gradient">Griô: Inteligência Pedagógica que Acelera sua Aprovação</h1>
          <p class="subtitle">Desbloqueie seu potencial acadêmico através de um diagnóstico guiado por IA que entende seu perfil e personaliza seu aprendizado.</p>

          <div class="cta-actions">
            <a href={diagnosticLink} class="btn btn-primary">{diagnosticText}</a>
            <a href="/sobre" class="btn btn-outline">Conheça o Projeto</a>
          </div>
        </div>
      {/if}
    </div>
  </section>

  <!-- Manifesto Section -->
  <section class="manifesto-section reveal">
    <div class="container grid-two-cols">
      <div class="manifesto-text">
        <h2 class="text-gradient">O Manifesto Griô</h2>
        <p>A Inteligência Griô redefine a preparação para o vestibular. Unimos ciência pedagógica avançada e inteligência artificial para criar uma jornada de aprendizado que respeita sua individualidade.</p>
        <p>Acreditamos que cada resposta é um dado valioso. Nossa tecnologia não apenas avalia seu conhecimento; ela decodifica seus padrões para direcionar seu progresso com precisão.</p>
      </div>
      <div class="manifesto-visual glass-panel">
        <div class="stats-card">
          <div class="stat-item">
            <span class="stat-val">30+</span>
            <span class="stat-label">Habilidades ENEM mapeadas</span>
          </div>
          <div class="stat-item">
            <span class="stat-val">Gemini</span>
            <span class="stat-label">IA de Análise Pedagógica</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Process Section -->
  <section class="process-section reveal">
    <div class="container">
      <h2 class="text-center mb-12">Sua Trilha de Evolução</h2>
      <div class="process-grid">
        <div class="glass-card process-step">
          <div class="step-num">01</div>
          <h3>Diagnóstico</h3>
          <p>Um teste adaptativo que identifica lacunas fundamentais em sua base de conhecimento.</p>
        </div>
        <div class="glass-card process-step">
          <div class="step-num">02</div>
          <h3>Insights</h3>
          <p>Nossa IA analisa seu desempenho e gera um relatório personalizado com foco em habilidades.</p>
        </div>
        <div class="glass-card process-step">
          <div class="step-num">03</div>
          <h3>Domínio</h3>
          <p>Receba recomendações precisas e transforme seus pontos fracos em sua maior força.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Final CTA -->
  <section class="final-cta reveal container">
    <div class="glass-panel text-center">
      <h2 class="text-gradient">Pronto para começar?</h2>
      <p>Sua aprovação universitária começa agora. Descubra sua proficiência.</p>
      <a href={diagnosticLink} class="btn btn-primary btn-lg">{diagnosticText}</a>
    </div>
  </section>
</div>

<style>
  .home-container {
    width: 100%;
  }

  /* Hero Section Styles */
  .hero-section {
    position: relative;
    height: 90vh;
    display: flex;
    align-items: center;
    margin-top: -2rem; /* Compensate layout padding */
  }

  .hero-bg {
    position: absolute;
    inset: 0;
    z-index: -1;
  }

  .hero-bg .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, transparent, var(--bg-primary));
  }

  .hero-content {
    z-index: 1;
  }

  .hero-text {
    max-width: 700px;
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

  .subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    margin-bottom: 2.5rem;
    line-height: 1.8;
  }

  .cta-actions {
    display: flex;
    gap: 1.5rem;
  }

  /* Reveal Animation Utility */
  .reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.8s cubic-bezier(0.2, 1, 0.3, 1);
  }

  :global(.reveal.visible) {
    opacity: 1;
    transform: translateY(0);
  }

  /* Manifesto Section */
  .grid-two-cols {
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    gap: 4rem;
    align-items: center;
    padding: 8rem 0;
  }

  .manifesto-text p {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
  }

  .manifesto-visual {
    padding: 3rem;
    display: flex;
    justify-content: center;
  }

  .stat-item {
    margin-bottom: 2rem;
    text-align: center;
  }

  .stat-val {
    display: block;
    font-size: 2.5rem;
    font-family: var(--font-serif);
    color: var(--primary);
    font-weight: 700;
  }

  .stat-label {
    color: var(--text-secondary);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  /* Process Section */
  .process-section {
    padding-bottom: 8rem;
  }

  .process-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }

  .process-step {
    position: relative;
    padding-top: 3rem;
  }

  .step-num {
    position: absolute;
    top: 1.5rem;
    left: 2rem;
    font-size: 4rem;
    font-family: var(--font-serif);
    color: rgba(255, 255, 255, 0.05);
    font-weight: 900;
    z-index: -1;
  }

  .final-cta {
    padding-bottom: 8rem;
  }

  @media (max-width: 900px) {
    .grid-two-cols, .process-grid {
      grid-template-columns: 1fr;
    }
    
    .hero-section {
      height: 70vh;
    }
  }
</style>
