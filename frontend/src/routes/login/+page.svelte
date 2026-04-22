<script lang="ts">
  import LoginForm from "$lib/components/LoginForm.svelte";
  import { goto } from "$app/navigation";

  let errorMessage = "";

  async function handleSubmit(event: any) {
    const { email, password } = event.detail;
    errorMessage = "";

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        goto("/dashboard");
      } else {
        const data = await response.json();
        errorMessage = data.detail || "Email ou senha incorretos.";
      }
    } catch (error) {
      errorMessage = "Não foi possível conectar ao servidor.";
    }
  }
</script>

<div class="auth-container">
  <div class="auth-header animate-slide-up stagger-1">
    <h1 class="text-gradient">Acesse o Griô</h1>
    <p>Bem-vindo de volta à sua jornada de conhecimento.</p>
  </div>

  <LoginForm on:submit={handleSubmit} />

  {#if errorMessage}
    <p class="error-msg animate-slide-up stagger-3">{errorMessage}</p>
  {/if}

  <p class="auth-footer animate-slide-up stagger-3">
    Ainda não tem uma conta? <a href="/cadastro">Cadastre-se</a>
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
