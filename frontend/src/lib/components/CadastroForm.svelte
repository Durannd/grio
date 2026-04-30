<script lang="ts">
  let { onsubmit } = $props();

  let name = $state("");
  let email = $state("");
  let password = $state("");

  function handleSubmit(e: Event) {
    e.preventDefault();
    onsubmit?.({ name, email, password });
  }
</script>

<div class="glass-card animate-slide-up stagger-2">
  <form onsubmit={handleSubmit}>
    <div class="form-group">
      <label for="name">Nome Completo</label>
      <input type="text" id="name" bind:value={name} placeholder="Seu nome completo" required />
    </div>

    <div class="form-group">
      <label for="email">E-mail</label>
      <input type="email" id="email" bind:value={email} placeholder="seu@email.com" required />
    </div>
    
    <div class="form-group">
      <label for="password">Senha Segura</label>
      <input type="password" id="password" bind:value={password} placeholder="••••••••" required />
    </div>
    
    <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem; min-height: 48px;">
      Criar Minha Conta
    </button>
    
    <div class="reflective-statement" style="text-align: center; margin-top: 2rem; font-size: 0.85rem; color: var(--text-secondary);">
      <p>Nossa missão é democratizar a educação de alta performance através de IA e dados.</p>
    </div>

    <div class="secure-badge">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lock-icon">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
      </svg>
      <span>SSL Secure Encrypted</span>
    </div>
  </form>
</div>

<style>
  .glass-card {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }

  .secure-badge {
    text-align: center; 
    margin-top: 1.5rem; 
    color: var(--success); 
    font-size: 0.75rem; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 0.5rem;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }

  .lock-icon {
    width: 14px;
    height: 14px;
  }
</style>
