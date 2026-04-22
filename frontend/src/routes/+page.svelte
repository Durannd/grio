<script lang="ts">
  import { onMount } from 'svelte';
  
  let isLoaded = false;
  
  onMount(() => {
    isLoaded = true;
    
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.story-section').forEach(el => observer.observe(el));
  });
</script>

<div class="landing-page {isLoaded ? 'loaded' : ''}">
  
  <!-- Hero / Intro Hook -->
  <section class="hero story-section">
    <div class="glass-panel text-center max-w-4xl mx-auto hero-content">
      <h1 class="text-gradient">A Sabedoria Que Transforma</h1>
      <p class="subtitle">Uma jornada de autodescoberta e nivelamento para conquistar seu espaço na universidade.</p>
      
      <div class="cta-group">
        <a href="/cadastro" class="btn btn-primary">Comece Sua Jornada</a>
        <a href="/login" class="btn btn-outline">Já sou aluno</a>
      </div>
    </div>
    
    <div class="scroll-indicator">
      <span class="mouse"></span>
      <p>Descubra</p>
    </div>
  </section>

  <!-- Chapter 1: Problem -->
  <section class="chapter story-section">
    <div class="glass-card chapter-content">
      <h2 class="text-gradient">O Vestibular Não Precisa Ser Um Abismo.</h2>
      <p>Muitos estudantes perdem tempo focando no que não importa. O nervosismo, a falta de direção e o excesso de conteúdo criam um bloqueio. Acreditamos que o conhecimento não deve ser um peso, mas sim a sua maior herança.</p>
    </div>
  </section>

  <!-- Chapter 2: Journey -->
  <section class="chapter chapter-alt story-section">
    <div class="glass-card chapter-content">
      <h2 class="text-gradient">Uma Trilha Feita Para Você</h2>
      <p>Assim como o Griô transmite a sabedoria de geração em geração, nossa Inteligência Artificial mapeia suas forças e fraquezas. Você começa com um teste de nivelamento que entende exatamente de onde sua história deve começar.</p>
      
      <div class="feature-grid">
        <div class="feature">
          <div class="icon">🧭</div>
          <h3>Diagnóstico Preciso</h3>
          <p>Descubra suas reais habilidades antes de estudar.</p>
        </div>
        <div class="feature">
          <div class="icon">✨</div>
          <h3>IA Adaptativa</h3>
          <p>Questões que se moldam ao seu ritmo de aprendizado.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Chapter 3 & Climax CTA -->
  <section class="chapter climax story-section">
    <div class="glass-panel text-center">
      <h2>Pronto Para Escrever Seu Futuro?</h2>
      <p>O ouro do saber está ao seu alcance.</p>
      <a href="/cadastro" class="btn btn-primary cta-large">Desbloquear Meu Nivelamento</a>
    </div>
  </section>

</div>

<style>
  .landing-page {
    position: relative;
    padding-bottom: 4rem;
  }
  
  /* Background glow effects */
  .landing-page::before, .landing-page::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    z-index: -1;
    opacity: 0.15;
    transition: opacity var(--transition-slow);
  }
  
  .landing-page::before {
    top: -10%; left: -10%;
    width: 500px; height: 500px;
    background: var(--primary);
  }
  
  .landing-page::after {
    bottom: -10%; right: -10%;
    width: 600px; height: 600px;
    background: var(--primary-dark);
  }
  
  .loaded::before, .loaded::after {
    opacity: 0.3;
  }

  .story-section {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    opacity: 0;
    transform: translateY(40px);
    transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .story-section.visible {
    opacity: 1;
    transform: translateY(0);
  }

  /* Hero Section */
  .hero {
    position: relative;
  }
  
  .hero-content {
    max-width: 800px;
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .hero h1 {
    font-size: clamp(3rem, 6vw, 5rem);
    margin-bottom: 1.5rem;
  }
  
  .subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    margin-bottom: 3rem;
    max-width: 600px;
    margin-inline: auto;
  }
  
  .cta-group {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  /* Scroll Indicator */
  .scroll-indicator {
    position: absolute;
    bottom: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    color: var(--primary-light);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    animation: bounce 2s infinite ease-in-out;
  }
  
  .mouse {
    width: 24px;
    height: 36px;
    border: 2px solid var(--primary-light);
    border-radius: 12px;
    position: relative;
  }
  
  .mouse::after {
    content: '';
    position: absolute;
    top: 6px;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: 8px;
    background: var(--primary-light);
    border-radius: 2px;
    animation: scroll 2s infinite;
  }

  /* Chapters */
  .chapter-content {
    max-width: 800px;
    width: 100%;
  }
  
  .chapter h2 {
    font-size: clamp(2rem, 4vw, 3.5rem);
    margin-bottom: 1.5rem;
  }
  
  .chapter p {
    font-size: 1.15rem;
    color: var(--text-secondary);
    line-height: 1.8;
    margin-bottom: 2rem;
  }
  
  .chapter-alt .chapter-content {
    margin-left: auto;
  }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
  }
  
  .feature .icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }
  
  .feature h3 {
    font-size: 1.25rem;
    color: var(--primary-light);
    margin-bottom: 0.5rem;
    font-family: var(--font-sans);
  }
  
  .feature p {
    font-size: 0.95rem;
    margin-bottom: 0;
  }

  /* Climax */
  .climax .glass-panel {
    padding: 5rem 2rem;
    max-width: 800px;
    width: 100%;
  }
  
  .cta-large {
    font-size: 1.1rem;
    padding: 1.25rem 3rem;
    margin-top: 1rem;
  }

  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(10px); }
  }
  
  @keyframes scroll {
    0% { transform: translate(-50%, 0); opacity: 1; }
    100% { transform: translate(-50%, 15px); opacity: 0; }
  }

  @media (max-width: 768px) {
    .story-section {
      min-height: auto;
      padding: 4rem 1.5rem;
    }
    
    .hero {
      min-height: 100vh;
    }
  }
</style>
