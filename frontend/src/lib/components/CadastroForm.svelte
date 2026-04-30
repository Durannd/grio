<script lang="ts">
  let { onsubmit } = $props();

  let name = $state("");
  let email = $state("");
  let password = $state("");
  let termsAccepted = $state(false);

  // Password Validation Runes
  let hasMinLength = $derived(password.length >= 8);
  let hasUppercase = $derived(/[A-Z]/.test(password));
  let hasNumber = $derived(/[0-9]/.test(password));
  
  let isPasswordValid = $derived(hasMinLength && hasUppercase && hasNumber);

  function handleSubmit(e: Event) {
    e.preventDefault();
    if (isPasswordValid && termsAccepted) {
      onsubmit?.({ name, email, password });
    }
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
      
      <!-- Interactive Password Strength Indicator -->
      <div class="password-requirements">
        <span class="req-item" class:met={hasMinLength}>
          <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="3" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>
          Mínimo 8 caracteres
        </span>
        <span class="req-item" class:met={hasUppercase}>
          <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="3" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>
          1 Letra Maiúscula
        </span>
        <span class="req-item" class:met={hasNumber}>
          <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="3" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>
          1 Número
        </span>
      </div>
    </div>

    <div class="form-group checkbox-group">
      <label class="checkbox-container">
        <input type="checkbox" bind:checked={termsAccepted} required />
        <span class="checkmark"></span>
        <span class="checkbox-text">
          Li e concordo com os <a href="/termos" target="_blank">Termos de Uso</a> e a <a href="/privacidade" target="_blank">Política de Privacidade</a> (LGPD).
        </span>
      </label>
    </div>
    
    <button type="submit" class="btn btn-primary" disabled={!isPasswordValid || !name || !email || !termsAccepted} style="width: 100%; margin-top: 1rem; min-height: 48px;">
      Criar Minha Conta
    </button>
    
    <div class="reflective-statement" style="text-align: center; margin-top: 2rem; font-size: 0.85rem; color: var(--text-secondary);">
      <p>Nossa missão é democratizar a educação de alta performance através de IA e dados.</p>
    </div>
  </form>
</div>

<style>
  .glass-card {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }

  .password-requirements {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-top: 0.75rem;
  }

  .req-item {
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--danger);
    transition: color 0.3s ease;
  }

  .req-item svg {
    opacity: 0.5;
    transition: opacity 0.3s ease;
  }

  .req-item.met {
    color: var(--success);
  }

  .req-item.met svg {
    opacity: 1;
  }

  /* Checkbox styling */
  .checkbox-group {
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .checkbox-container {
    display: flex;
    align-items: flex-start;
    position: relative;
    cursor: pointer;
    font-size: 0.85rem;
    user-select: none;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .checkbox-container input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
  }

  .checkmark {
    position: relative;
    top: 2px;
    left: 0;
    height: 18px;
    width: 18px;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    flex-shrink: 0;
    margin-right: 12px;
    transition: all 0.2s ease;
  }

  .checkbox-container:hover input ~ .checkmark {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .checkbox-container input:checked ~ .checkmark {
    background-color: var(--primary);
    border-color: var(--primary);
  }

  .checkmark:after {
    content: "";
    position: absolute;
    display: none;
  }

  .checkbox-container input:checked ~ .checkmark:after {
    display: block;
  }

  .checkbox-container .checkmark:after {
    left: 6px;
    top: 2px;
    width: 4px;
    height: 9px;
    border: solid #000;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
  }

  .checkbox-text a {
    color: var(--primary-light);
    text-decoration: underline;
    text-decoration-color: rgba(212, 163, 115, 0.3);
    text-underline-offset: 2px;
    transition: text-decoration-color 0.2s ease;
  }

  .checkbox-text a:hover {
    text-decoration-color: var(--primary-light);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
