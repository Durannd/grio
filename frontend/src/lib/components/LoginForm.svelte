<script lang="ts">
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let email = "";
  let password = "";

  function handleSubmit() {
    dispatch("submit", { email, password });
  }
</script>

<style>
  .glass-card {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }
</style>

<div class="glass-card animate-slide-up stagger-2">
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="email">E-mail</label>
      <input type="email" id="email" bind:value={email} placeholder="seu@email.com" required />
    </div>
    
    <div class="form-group">
      <label for="password">Senha</label>
      <input type="password" id="password" bind:value={password} placeholder="••••••••" required />
    </div>
    
    <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">
      Entrar na Plataforma
    </button>
    <div style="text-align: center; margin-top: 1rem; color: var(--success); font-size: 0.8rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
      🔒 <span>SSL Secure Login</span>
    </div>
  </form>
</div>
