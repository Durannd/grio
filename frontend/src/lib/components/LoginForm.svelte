<script lang="ts">
  let { onsubmit } = $props();

  let email = $state("");
  let password = $state("");

  function handleSubmit(e: Event) {
    e.preventDefault();
    onsubmit?.({ email, password });
  }
</script>

<div class="glass-card animate-slide-up stagger-2">
  <form onsubmit={handleSubmit}>
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
  </form>
</div>

<style>
  .glass-card {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }
</style>
