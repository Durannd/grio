<script lang="ts">
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let email = "";
  let password = "";

  function handleSubmit() {
    dispatch("submit", { email, password });
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <label>
    Email:
    <input type="email" bind:value={email} required />
  </label>
  <label>
    Senha:
    <input type="password" bind:value={password} required />
  </label>
  <button type="submit">Cadastrar</button>
</form>
