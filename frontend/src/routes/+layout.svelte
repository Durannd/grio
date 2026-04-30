<script lang="ts">
  import { browser } from '$app/environment';
  import '../app.css';
  import { fade, slide } from 'svelte/transition';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Chatbot from '$lib/components/Chatbot.svelte';
  import Toast from '$lib/components/Toast.svelte';
  import { api } from '$lib/api';
  import { user, loadingStore, loadUser } from '$lib/stores/userStore';
  import DOMPurify from 'isomorphic-dompurify';

  $: ({ name: userName, email, avatar_url, is_diagnostic_completed } = $user || {});
  $: safeName = userName ? DOMPurify.sanitize(userName) : '';

  let showDropdown = false;

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

  async function logout() {
    try {
      await api.post('/auth/logout', {});
    } catch (error) {
      // api service já lida com o log
    }
    user.set(null);
    showDropdown = false;
    await invalidateAll();
    goto("/");
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  function closeDropdown() {
    showDropdown = false;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      closeDropdown();
    }
  }

  function clickOutside(node: HTMLElement) {
    const handleClick = (event: MouseEvent) => {
      if (node && !node.contains(event.target as Node) && !event.defaultPrevented) {
        closeDropdown();
      }
    };

    document.addEventListener('click', handleClick, true);

    return {
      destroy() {
        document.removeEventListener('click', handleClick, true);
      }
    };
  }

  onMount(async () => {
    if (browser) {
      window.addEventListener('scroll', handleScroll);
      // Garante que o usuário seja carregado sempre que o layout for montado/atualizado
      await loadUser();
      return () => window.removeEventListener('scroll', handleScroll);
    }
  });
</script>

<div class="app-layout">
  <nav class="glass-nav" class:nav-hidden={navbarHidden}>
    <div class="nav-content container">
      <a href="/" class="brand">
        <img src="/grio-logo.png" alt="Logotipo Griô" class="logo-img" />
      </a>
      <div class="links">
        {#if $loadingStore}
          <div class="avatar-placeholder skeleton-pulse"></div>
        {:else if $user}
          <a href="/dashboard">Dashboard</a>
          <a href="/sobre">Sobre</a>

          <div class="user-profile">
            <button class="profile-trigger" on:click={toggleDropdown} aria-haspopup="true" aria-expanded={showDropdown}>
              {#if $user.avatar_url}
                <img src={$user.avatar_url} alt={`Avatar de ${safeName}`} class="avatar" />
              {:else}
                <div class="avatar-placeholder">{safeName.charAt(0).toUpperCase()}</div>
              {/if}
            </button>

            {#if showDropdown}
              <div class="profile-dropdown glass-panel" role="menu" tabindex="-1" in:slide={{ duration: 200 }} use:clickOutside on:keydown={handleKeydown}>
                <div class="dropdown-header">
                  <span class="user-name">{safeName}</span>
                  <span class="user-email">{$user.email}</span>
                </div>
                <div class="dropdown-divider"></div>
                <button class="account-btn" role="menuitem" on:click={() => { showDropdown = false; goto('/account'); }}>Minha Conta</button>
                <button class="logout-btn" role="menuitem" on:click={logout}>Sair</button>
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
    width: 100%;
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

  .account-btn, .logout-btn {
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    transition: background 0.2s;
    text-align: left;
  }

  .account-btn:hover, .logout-btn:hover {
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

  .skeleton-pulse {
    animation: pulse 1.5s ease-in-out infinite;
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.8; }
  }
</style>
