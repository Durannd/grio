<script lang="ts">
  import { browser } from '$app/environment';
  import '../app.css';
  import { fade, slide } from 'svelte/transition';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Chatbot from '$lib/components/Chatbot.svelte';
  import Toast from '$lib/components/Toast.svelte';

  let user: any = null;
  let showDropdown = false;
  let hasDiagnostic = false;

  // Navbar scroll logic
  let lastScrollY = 0;
  let navbarHidden = false;
  let scrollThreshold = 10;

  function handleScroll() {
    if (!browser) return;
    const currentScrollY = window.scrollY;
    
    if (Math.abs(currentScrollY - lastScrollY) < scrollThreshold) return;

    if (currentScrollY > lastScrollY && currentScrollY > 80) {
      navbarHidden = true;
    } else {
      navbarHidden = false;
    }
    lastScrollY = currentScrollY;
  }

  async function loadUser() {
    if (!browser) return;

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/me", {
        credentials: "include"
      });
      if (response.ok) {
        user = await response.json();
        hasDiagnostic = user.is_diagnostic_completed === true;
      } else {
        user = null;
      }
    } catch (error) {
      console.error("Erro ao carregar usuário:", error);
      user = null;
    }
  }

  async function logout() {
    try {
      await fetch("http://localhost:8000/api/v1/auth/logout", {
        method: "POST",
        credentials: "include"
      });
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
    }
    user = null;
    showDropdown = false;
    goto("/login");
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  onMount(() => {
    // loadUser is handled by the reactive statement on mount
    if (browser) {
      window.addEventListener('scroll', handleScroll);
      return () => window.removeEventListener('scroll', handleScroll);
    }
  });

  // Re-check when path changes (optional, but good for login/logout)
  $: if ($page.url.pathname) {
    if (browser) loadUser();
  }
</script>

<div class="app-layout">
  <nav class="glass-nav" class:nav-hidden={navbarHidden}>
    <div class="nav-content container">
      <a href="/" class="brand">
        <img src="/grio-logo.png" alt="Logotipo Griô" class="logo-img" />
      </a>
      <div class="links">
        {#if user}
          <a href="/dashboard">Dashboard</a>
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
                <button class="account-btn" on:click={() => { showDropdown = false; goto('/account'); }}>Minha Conta</button>
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

  <Toast />
  <Chatbot />
</div>

<style>
  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    width: 100%;
    overflow-x: hidden;
    background-color: #0A0A0B;
    color: #FFF;
  }

  .glass-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-bottom: var(--glass-border);
    padding: 0.75rem 0;
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;
  }

  .nav-hidden {
    transform: translateY(-100%);
    opacity: 0;
  }

  .nav-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
  }

  .brand {
    display: flex;
    align-items: center;
    margin-right: 2rem;
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
    white-space: nowrap;
  }

  .links a:hover {
    color: var(--primary);
  }

  .user-profile {
    position: relative;
    margin-left: 0.5rem;
    flex-shrink: 0;
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
    width: 36px;
    height: 36px;
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
    font-size: 1rem;
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
    box-shadow: var(--shadow-lg);
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
    color: var(--text-secondary);
  }

  .dropdown-divider {
    height: 1px;
    background: var(--glass-border);
    margin: 0.5rem 0;
  }

  .profile-dropdown a, .account-btn, .logout-btn {
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    transition: background 0.2s;
    text-align: left;
  }

  .profile-dropdown a:hover, .account-btn:hover, .logout-btn:hover {
    background: rgba(255,255,255,0.05);
    color: var(--primary-light) !important;
  }

  .account-btn {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    width: 100%;
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
    padding-top: 5.5rem;
    padding-bottom: 4rem;
    width: 100%;
    max-width: 100vw;
    box-sizing: border-box;
  }

  @media (max-width: 768px) {
    .links a:not(.login-link, .btn) {
      display: none;
    }
    
    .brand {
      margin-right: auto;
    }

    .nav-content {
      padding: 0 1rem;
    }
  }
</style>
