<script lang="ts">
  import CadastroForm from "$lib/components/CadastroForm.svelte";
  import { goto, invalidateAll } from "$app/navigation";
  import { api } from "$lib/api";
  import { loadUser } from "$lib/stores/userStore";

  let errorMessage = $state("");

  async function handleSubmit(data: any) {
    const { name, email, password } = data;
    errorMessage = "";

    try {
      await api.post("/auth/signup", { name, email, password });
      
      await loadUser();
      await invalidateAll();
      // Redireciona para a tela de boas-vindas após o cadastro
      goto("/welcome");
    } catch (error: any) {
      errorMessage = error.message || "Não foi possível realizar o cadastro.";
    }
  }
</script>

<div class="auth-container">
  <div class="auth-header animate-slide-up stagger-1">
    <h1 class="text-gradient">Crie sua Conta</h1>
    <p>Comece sua jornada de estudos agora mesmo.</p>
  </div>

  <CadastroForm onsubmit={handleSubmit} />

  {#if errorMessage}
    <p class="error-msg animate-slide-up stagger-3">{errorMessage}</p>
  {/if}

  <p class="auth-footer animate-slide-up stagger-3">
    Já tem uma conta? <a href="/login">Entre aqui</a>
  </p>
</div>

<style>
  .auth-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 80px);
    padding: 2rem;
  }

  .auth-header {
    text-align: center;
    margin-bottom: 3rem;
  }

  .auth-header h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
  }

  .auth-header p {
    color: var(--text-secondary);
    font-size: 1.1rem;
  }

  .error-msg {
    color: var(--danger);
    background: rgba(204, 79, 79, 0.1);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    margin-top: 1.5rem;
    font-size: 0.9rem;
    border: 1px solid rgba(204, 79, 79, 0.2);
  }

  .auth-footer {
    margin-top: 2rem;
    color: var(--text-secondary);
  }
</style>
