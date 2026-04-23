<script>
  import '../app.css';
  import { fade } from 'svelte/transition';
  import { page } from '$app/stores';
  import Chatbot from '$lib/components/Chatbot.svelte';
</script>

<div class="app-layout">
  <nav class="glass-nav">
    <div class="nav-content">
      <a href="/" class="brand">
        <img src="/grio-logo.png" alt="Logotipo Griô" class="logo-img" />
      </a>
      <div class="links">
        <a href="/dashboard">Dashboard</a>
        <a href="/prova">Prova</a>
      </div>
    </div>
  </nav>

  {#key $page.url.pathname}
    <div class="page-transition-wrapper" in:fade={{ duration: 300, delay: 150 }} out:fade={{ duration: 150 }}>
      <slot />
    </div>
  {/key}

  <Chatbot />
</div>

<style>
  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .glass-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-bottom: var(--glass-border);
    padding: 1rem 0;
  }

  .nav-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brand {
    display: flex;
    align-items: center;
  }

  .logo-img {
    height: 48px; /* Ajuste o tamanho conforme necessário */
    width: auto;
    object-fit: contain;
    transition: transform 0.3s ease;
  }

  .logo-img:hover {
    transform: scale(1.05);
  }

  .links {
    display: flex;
    gap: 2rem;
  }

  .links a {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .links a:hover {
    color: var(--primary);
  }

  .page-transition-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
</style>
