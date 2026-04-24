<script lang="ts">
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let name = "";
  let email = "";
  let password = "";

  function handleSubmit() {
    dispatch("submit", { name, email, password });
  }
</script>

<div class="glass-card animate-slide-up stagger-2" style="max-width: 400px; width: 100%; margin: 0 auto;">
  <form on:submit|preventDefault={handleSubmit}>
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
    
    <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">
      Criar Minha Conta
    </button>
    <div style="text-align: center; margin-top: 1rem; color: var(--success); font-size: 0.8rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
      🔒 <span>SSL Secure Encrypted</span>
    </div>
  </form>
</div>
