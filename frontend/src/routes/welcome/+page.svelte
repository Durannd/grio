<script lang="ts">
  import { onMount } from "svelte";
  import { fly, fade, scale } from "svelte/transition";
  import { goto } from "$app/navigation";
  import { api } from "$lib/api";

  let user: any = $state(null);

  onMount(async () => {
    try {
      user = await api.get("/auth/me");
    } catch (error) {
      // api service lida com unauthorized
    }
  });
</script>

<div class="welcome-container container">
  {#if user}
    <div class="content-wrapper">
      <header class="welcome-header" in:fly={{ y: -30, duration: 800 }}>
        <h1 class="text-gradient">Bem-vindo ao Griô, {user.name}!</h1>
        <p class="lead">Estamos muito felizes em ter você conosco nesta etapa da sua vida.</p>
      </header>

      <div class="main-card glass-panel" in:scale={{ start: 0.95, duration: 1000, delay: 200 }}>
        <div class="card-content">
          <div class="icon-box" in:scale={{ start: 0.5, duration: 600, delay: 600 }}>
            <span class="icon">🎯</span>
          </div>
          <h2>Primeiro passo: Seu Diagnóstico</h2>
          <p>
            Para que possamos criar um plano de estudos realmente eficiente para você, 
            precisamos entender quais são seus pontos fortes e onde podemos evoluir juntos.
          </p>
          <div class="action-box">
            <a href="/prova" class="btn btn-primary btn-lg">Iniciar Avaliação Diagnóstica</a>
            <p class="small-text">Leva cerca de 15-20 minutos.</p>
          </div>
        </div>
      </div>

      <div class="secondary-info" in:fade={{ duration: 1000, delay: 800 }}>
        <p>Prefere explorar primeiro? <a href="/dashboard">Ir para o Dashboard</a></p>
      </div>
    </div>
  {/if}
</div>

<style>
  .welcome-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 120px);
    text-align: center;
  }

  .content-wrapper {
    max-width: 700px;
    width: 100%;
  }

  .welcome-header {
    margin-bottom: 3rem;
  }

  .welcome-header h1 {
    font-size: 3.5rem;
    margin-bottom: 1rem;
  }

  .lead {
    font-size: 1.25rem;
    color: var(--text-secondary);
  }

  .main-card {
    padding: 4rem 2rem;
    border-radius: 2rem;
    margin-bottom: 2rem;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
  }

  .icon-box {
    margin-bottom: 2rem;
  }

  .icon {
    font-size: 4rem;
    filter: drop-shadow(0 0 10px var(--primary));
  }

  h2 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
  }

  p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: var(--text-secondary);
    margin-bottom: 2.5rem;
  }

  .action-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .small-text {
    font-size: 0.85rem;
    opacity: 0.7;
    margin-bottom: 0;
  }

  .secondary-info {
    color: var(--text-tertiary);
  }

  .secondary-info a {
    color: var(--primary-light);
    font-weight: 600;
  }
</style>
