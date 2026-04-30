<script lang="ts">
  import { onMount } from "svelte";
  import { fly, fade } from "svelte/transition";
  import LoadingSpinner from "$lib/components/LoadingSpinner.svelte";
  import { goto } from "$app/navigation";
  import { api } from "$lib/api";
  import { user, loadUser } from "$lib/stores/userStore";

  interface LearningPathItem {
    area_id?: string;
    concept_name: string;
    display_name?: string;
    friendly_code?: string;
    description: string;
    score: number;
    is_inferred?: boolean;
  }

  let loading = $state(true);
  let saving = $state(false);
  let successMessage = $state("");
  let errorMessage = $state("");

  let name = $state("");
  let email = $state("");
  let password = $state("");
  let avatar_url = $state("");

  let learningPath: LearningPathItem[] = $state([]);
  let activeTab = $state('profile'); 

  onMount(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('tab') === 'technical') {
      activeTab = 'technical';
    }
  });

  let groupedPath = $derived(learningPath.reduce((acc: Record<string, LearningPathItem[]>, item) => {
    const area = item.area_id || (item.concept_name && !item.concept_name.startsWith('SKL-') ? item.concept_name.substring(0, 2) : 'MT');
    if (!acc[area]) acc[area] = [];
    acc[area].push(item);
    return acc;
  }, {}));

  onMount(async () => {
    try {
      // Ensure user is loaded from store or fetch
      if (!$user) await loadUser();
      
      if ($user) {
        name = $user.name;
        email = $user.email;
        avatar_url = $user.avatar_url || "";
      }

      const data = await api.get("/learning-path/full") as { learning_path?: LearningPathItem[] } | LearningPathItem[];
      if (data) {
        learningPath = (data as any).learning_path || data;
      }
    } catch (e) {
      console.error(e);
      // api service lida com unauthorized
    } finally {
      loading = false;
    }
  });

  async function handleUpdate(e: Event) {
    e.preventDefault();
    saving = true;
    successMessage = "";
    errorMessage = "";
    
    try {
      const payload: any = { name };
      if (password) {
        payload.password = password;
      }
      if (avatar_url) {
        payload.avatar_url = avatar_url;
      }

      await api.put("/auth/me", payload);
      await loadUser(); // Refresh the store
      
      successMessage = "Configurações salvas com sucesso!";
      password = ""; // Clear password field after saving
    } catch (e: any) {
      errorMessage = e.message || "Erro ao salvar alterações.";
    } finally {
      saving = false;
    }
  }
</script>

<div class="account-page container section-padding">
  {#if loading}
    <div class="status-screen" out:fade>
      <LoadingSpinner />
    </div>
  {:else if $user}
    <div class="account-layout">
      <aside class="account-sidebar animate-slide-up">
        <div class="profile-preview glass-panel">
          <div class="avatar-edit">
            {#if avatar_url}
              <img src={avatar_url} alt={name} class="large-avatar" />
            {:else}
              <div class="large-avatar-placeholder">{name.charAt(0).toUpperCase()}</div>
            {/if}
          </div>
          <h3>{name}</h3>
          <p>{email}</p>
        </div>
        
        <nav class="account-nav glass-panel">
          <button class={activeTab === 'profile' ? 'active' : ''} onclick={() => activeTab = 'profile'}>Perfil e Segurança</button>
          <button class={activeTab === 'technical' ? 'active' : ''} onclick={() => activeTab = 'technical'}>Análise Granular</button>
        </nav>
      </aside>

      <main class="account-content animate-slide-up stagger-1">
        {#if activeTab === 'profile'}
          <div class="glass-panel main-settings" in:fly={{ y: 10, duration: 400 }}>
            <h2>Configurações de Conta</h2>
            <form onsubmit={handleUpdate}>
              <div class="form-group">
                <label for="name">Nome Completo</label>
                <input type="text" id="name" bind:value={name} required minlength="2" />
              </div>
              
              <div class="form-group">
                <label for="email">E-mail</label>
                <input type="email" id="email" bind:value={email} disabled />
                <p class="helper-text">O e-mail não pode ser alterado por segurança.</p>
              </div>

              <div class="form-group">
                <label for="password">Nova Senha (opcional)</label>
                <input type="password" id="password" bind:value={password} placeholder="Deixe em branco para não alterar" minlength="8" />
                <p class="helper-text">Mínimo 8 caracteres, 1 maiúscula, 1 número.</p>
              </div>

              <div class="form-group">
                <label for="avatar">URL da Foto de Perfil (opcional)</label>
                <input type="text" id="avatar" bind:value={avatar_url} placeholder="https://..." />
              </div>

              {#if successMessage}
                <div class="success-alert" in:fade>{successMessage}</div>
              {/if}

              {#if errorMessage}
                <div class="error-alert" in:fade>{errorMessage}</div>
              {/if}

              <button type="submit" class="btn btn-primary" disabled={saving}>
                {saving ? "Salvando..." : "Salvar Alterações"}
              </button>
            </form>
          </div>
        {:else if activeTab === 'technical'}
          <div class="technical-section" in:fly={{ y: 10, duration: 400 }}>
            <div class="section-header">
              <div>
                <h2 class="section-title">Matriz ENEM</h2>
                <p class="section-desc">Detalhamento da sua proficiência em competências e habilidades da Matriz de Referência.</p>
              </div>
            </div>

            {#if learningPath.length === 0}
              <div class="glass-panel empty-state">
                <h3>Mapeamento Pendente</h3>
                <p>Ainda não temos dados suficientes para traçar sua proficiência granular.</p>
                <a href="/prova" class="btn btn-primary mt-4">Fazer Diagnóstico</a>
              </div>
            {:else}
              {#each Object.entries(groupedPath) as [areaCode, concepts]}
                <div class="area-group mb-4">
                  <h3 class="area-group-title">
                    {areaCode === 'MT' ? 'Matemática e suas Tecnologias' : areaCode === 'CN' ? 'Ciências da Natureza e suas Tecnologias' : areaCode === 'LC' ? 'Linguagens, Códigos e suas Tecnologias' : 'Ciências Humanas e suas Tecnologias'}
                  </h3>
                  <div class="proficiency-list">
                    {#each concepts as concept (concept.concept_name)}
                      <div class="proficiency-item glass-panel" class:inferred={concept.is_inferred}>
                        <div class="prof-header">
                          <div class="prof-title-wrap">
                            <span class="prof-code">{concept.friendly_code}</span>
                            <h4>{concept.display_name}</h4>
                          </div>
                          {#if concept.is_inferred}
                            <div class="inferred-badge">POTENCIAL</div>
                          {:else}
                            <div class="prof-score" class:high={concept.score >= 0.7} class:med={concept.score >= 0.4 && concept.score < 0.7} class:low={concept.score < 0.4}>
                              {(concept.score * 100).toFixed(0)}%
                            </div>
                          {/if}
                        </div>
                        <p class="prof-desc">{concept.description}</p>
                        <div class="progress-bar-container" class:inferred-bar={concept.is_inferred}>
                          <div class="progress-bar" style="width: {concept.score * 100}%; background-color: {concept.is_inferred ? '#6B7280' : (concept.score >= 0.7 ? '#10B981' : (concept.score >= 0.4 ? '#F59E0B' : '#EF4444'))}"></div>
                        </div>
                        <div class="prof-footer mt-4">
                          <a href="/estudar/{concept.friendly_code || concept.concept_name}" class="btn btn-primary btn-sm" style="width: 100%; text-align: center;">
                            {concept.is_inferred ? 'Explorar' : 'Estudar'}
                          </a>
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/each}
            {/if}
          </div>
        {/if}
      </main>
    </div>
  {/if}
</div>

<style>
  .account-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 2rem;
    align-items: start;
  }

  .profile-preview {
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .avatar-edit {
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: center;
  }

  .large-avatar, .large-avatar-placeholder {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid var(--primary);
    object-fit: cover;
  }

  .large-avatar-placeholder {
    background: var(--primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3.5rem;
    font-weight: 700;
  }

  .profile-preview h3 {
    margin-bottom: 0.25rem;
  }

  .profile-preview p {
    color: var(--text-tertiary);
    font-size: 0.9rem;
  }

  .account-nav {
    display: flex;
    flex-direction: column;
    padding: 0.75rem;
  }

  .account-nav button {
    background: none;
    border: none;
    padding: 1rem;
    text-align: left;
    color: var(--text-secondary);
    border-radius: 0.75rem;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
  }

  .account-nav button.active {
    background: rgba(255,255,255,0.05);
    color: var(--primary-light);
  }

  .account-nav button:hover:not(.active) {
    background: rgba(255,255,255,0.02);
    color: var(--text-primary);
  }

  .main-settings {
    padding: 2.5rem;
  }

  h2 {
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 2rem;
  }

  .helper-text {
    font-size: 0.8rem;
    color: var(--text-tertiary);
    margin-top: 0.5rem;
  }

  .success-alert {
    background: rgba(34, 197, 94, 0.1);
    color: #4ade80;
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(34, 197, 94, 0.2);
  }

  .error-alert {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(239, 68, 68, 0.2);
  }

  /* Technical Section Styles */
  .section-header {
    margin-bottom: 2rem;
  }

  .area-group {
    margin-bottom: 3rem;
  }

  .area-group-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-light, #DFB97B);
    margin-bottom: 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 0.5rem;
  }

  .proficiency-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .proficiency-item {
    padding: 1.5rem;
    transition: transform 0.2s ease, border-color 0.2s ease;
  }

  .proficiency-item:hover {
    transform: translateX(4px);
    border-color: rgba(255,255,255,0.15);
  }

  .prof-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .prof-title-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .prof-code {
    font-size: 0.8rem;
    font-family: monospace;
    background: rgba(255,255,255,0.1);
    color: #FFF;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    width: fit-content;
  }

  .prof-title-wrap h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #FFF;
  }

  .prof-score {
    font-weight: 700;
    font-size: 1rem;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
  }

  .prof-score.high { color: #34D399; }
  .prof-score.med { color: #FBBF24; }
  .prof-score.low { color: #F87171; }

  .inferred-badge {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.1);
    color: #FFF;
    letter-spacing: 0.05em;
  }

  .prof-desc {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.6);
    margin-bottom: 1.25rem;
    line-height: 1.6;
  }

  .progress-bar-container {
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-bar {
    height: 100%;
    border-radius: 3px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .prof-footer {
    display: flex;
    justify-content: flex-end;
  }

  .empty-state { text-align: center; }
  .empty-state h3 { margin-bottom: 0.5rem; font-size: 1.25rem; color: #FFF; }
  .empty-state p { color: rgba(255,255,255,0.6); font-size: 0.95rem; }
  .mt-4 { margin-top: 1rem; }

  @media (max-width: 768px) {
    .account-layout {
      grid-template-columns: 1fr;
    }
  }
</style>
