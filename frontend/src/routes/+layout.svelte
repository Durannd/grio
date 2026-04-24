<script>
  import '../app.css';
  import { fade } from 'svelte/transition';
  import { page } from '$app/stores';
  import Chatbot from '$lib/components/Chatbot.svelte';
</script>

<div class="app-layout">
  <nav class="glass-nav">
    <div class="nav-content container">
      <a href="/" class="brand">
        <img src="/grio-logo.png" alt="Logotipo Griô" class="logo-img" />
      </a>
      <div class="links">
        <a href="/dashboard">Dashboard</a>
        <a href="/prova">Prova</a>
        <a href="/sobre">Sobre</a>
      </div>
    </div>
  </nav>

  {#key $page.url.pathname}
    <div class="page-transition-wrapper container" in:fade={{ duration: 300, delay: 150 }} out:fade={{ duration: 150 }}>
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
    padding: 0.75rem 0;
  }

  .nav-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brand {
    display: flex;
    align-items: center;
  }

  .logo-img {
    height: 40px;
    width: auto;
    object-fit: contain;
    transition: transform 0.3s ease;
  }

  .logo-img:hover {
    transform: scale(1.05);
  }

  .links {
    display: flex;
    gap: 1.5rem;
  }

  .links a {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    color: var(--text-secondary);
    transition: color var(--transition-fast);
  }

  .links a:hover {
    color: var(--primary);
  }

  .page-transition-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding-top: 2rem;
    padding-bottom: 4rem;
  }
</style>
