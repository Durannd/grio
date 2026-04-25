<script lang="ts">
  import { browser } from '$app/environment';
  import '../app.css';
  import { fade, slide } from 'svelte/transition';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Chatbot from '$lib/components/Chatbot.svelte';

  let user: any = null;
  let showDropdown = false;
  let hasDiagnostic = false;

  async function loadUser() {
    if (!browser) return;
    const token = localStorage.getItem("token");
    if (!token) {
      user = null;
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        user = await response.json();
        hasDiagnostic = user.is_diagnostic_completed === true;
      } else {
        user = null;
        localStorage.removeItem("token");
      }
    } catch (error) {
      console.error("Erro ao carregar usuário:", error);
    }
  }

  function logout() {
    localStorage.removeItem("token");
    user = null;
    showDropdown = false;
    goto("/login");
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  onMount(() => {
    loadUser();
  });

  // Re-check when path changes (optional, but good for login/logout)
  $: if ($page.url.pathname) {
    if (browser) loadUser();
  }
</script>

<div class="app-layout">
  <nav class="glass-nav">
    <div class="nav-content container">
      <a href="/" class="brand">
        <img src="/grio-logo.png" alt="Logotipo Griô" class="logo-img" />
      </a>
      <div class="links">
        {#if user}
          <a href="/dashboard">Dashboard</a>
          {#if !hasDiagnostic}
            <a href="/prova" class="btn-highlight">Fazer Prova</a>
          {/if}
          <a href="/sobre">Sobre</a>
          
          <div class="user-profile">
            <button class="profile-trigger" on:click={toggleDropdown}>
              {#if user.avatar_url}
                <img src={user.avatar_url} alt={user.name} class="avatar" />
              {:else}
                <div class="avatar-placeholder">{user.name.charAt(0).toUpperCase()}</div>
              {/if}
            </button>
            
            {#if showDropdown}
              <div class="profile-dropdown glass-panel" in:slide={{ duration: 200 }}>
                <div class="dropdown-header">
                  <span class="user-name">{user.name}</span>
                  <span class="user-email">{user.email}</span>
                </div>
                <div class="dropdown-divider"></div>
                <a href="/account" on:click={() => showDropdown = false}>Minha Conta</a>
                <button class="logout-btn" on:click={logout}>Sair</button>
              </div>
            {/if}
          </div>
        {:else}
          <a href="/sobre">Sobre</a>
          <a href="/login" class="login-link">Entrar</a>
          <a href="/cadastro" class="btn btn-primary btn-sm">Cadastrar</a>
        {/if}
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
    align-items: center;
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

  .btn-highlight {
    background: var(--gradient-primary);
    color: var(--text-dark) !important;
    padding: 0.6rem 1.5rem;
    border-radius: var(--radius-full);
    font-weight: 700;
    box-shadow: var(--shadow-glow);
    transition: all var(--transition-fast);
  }

  .btn-highlight:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(201, 160, 94, 0.4);
  }

  .user-profile {
    position: relative;
    margin-left: 1rem;
  }

  .profile-trigger {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
  }

  .avatar, .avatar-placeholder {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 2px solid var(--primary);
    object-fit: cover;
  }

  .avatar-placeholder {
    background: var(--primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.1rem;
  }

  .profile-dropdown {
    position: absolute;
    top: calc(100% + 15px);
    right: 0;
    width: 240px;
    padding: 1rem;
    z-index: 1000;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    border-radius: 1rem;
  }

  .dropdown-header {
    display: flex;
    flex-direction: column;
    padding-bottom: 0.5rem;
  }

  .user-name {
    font-weight: 700;
    font-size: 1rem;
    color: var(--text-primary);
  }

  .user-email {
    font-size: 0.75rem;
    color: var(--text-tertiary);
  }

  .dropdown-divider {
    height: 1px;
    background: var(--glass-border);
    margin: 0.5rem 0;
  }

  .profile-dropdown a, .logout-btn {
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    transition: background 0.2s;
    text-align: left;
  }

  .profile-dropdown a:hover, .logout-btn:hover {
    background: rgba(255,255,255,0.05);
    color: var(--primary-light) !important;
  }

  .logout-btn {
    background: none;
    border: none;
    color: var(--danger);
    cursor: pointer;
    width: 100%;
  }

  .login-link {
    display: flex;
    align-items: center;
  }

  .page-transition-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding-top: 2rem;
    padding-bottom: 4rem;
  }
</style>
