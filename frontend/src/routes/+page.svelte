<script lang="ts">
  import { onMount } from 'svelte';

  let message = 'Carregando...';

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000');
      const data = await response.json();
      message = data.message;
    } catch (error) {
      message = 'Erro ao conectar com a API.';
    }
  });
</script>

<h1>Bem-vindo ao Griô</h1>
<p>Status da API: {message}</p>
