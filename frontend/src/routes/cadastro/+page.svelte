<script lang="ts">
  import CadastroForm from "$lib/components/CadastroForm.svelte";

  let successMessage = "";
  let errorMessage = "";

  async function handleSubmit(event: any) {
    const { email, password } = event.detail;
    errorMessage = "";
    successMessage = "";

    try {
      const response = await fetch("http://localhost:8000/api/v1/users/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        successMessage = "Usuário criado com sucesso!";
      } else {
        const data = await response.json();
        errorMessage = data.detail || "Ocorreu um erro.";
      }
    } catch (error) {
      errorMessage = "Não foi possível conectar ao servidor.";
    }
  }
</script>

<h1>Cadastro</h1>

<CadastroForm on:submit={handleSubmit} />

{#if successMessage}
  <p style="color: green;">{successMessage}</p>
{/if}

{#if errorMessage}
  <p style="color: red;">{errorMessage}</p>
{/if}
