<script lang="ts">
  import { toasts } from "../stores/toast";
  import { flip } from "svelte/animate";
  import { fly } from "svelte/transition";
</script>

<div class="toast-container">
  {#each $toasts as toast (toast.id)}
    <div
      class="toast {toast.type}"
      animate:flip={{ duration: 300 }}
      in:fly={{ x: 100, duration: 400 }}
      out:fly={{ x: 100, duration: 300 }}
    >
      <div class="toast-content">
        <span class="icon">
          {#if toast.type === 'success'}
            ✅
          {:else if toast.type === 'error'}
            ❌
          {:else if toast.type === 'warning'}
            ⚠️
          {:else}
            ℹ️
          {/if}
        </span>
        <p>{toast.message}</p>
      </div>
      <button class="close-btn" onclick={() => toasts.remove(toast.id)}>
        &times;
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    top: 2rem;
    right: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    z-index: 9999;
    pointer-events: none;
    max-width: 400px;
  }

  .toast {
    pointer-events: auto;
    background: rgba(30, 20, 15, 0.9);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .toast p {
    margin: 0;
    font-size: 0.9rem;
    color: var(--text-primary);
    line-height: 1.4;
  }

  .icon {
    font-size: 1.25rem;
  }

  .close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
    opacity: 0.5;
    transition: opacity 0.2s;
  }

  .close-btn:hover {
    opacity: 1;
  }

  .toast.success { border-left: 4px solid var(--success); }
  .toast.error { border-left: 4px solid var(--danger); }
  .toast.warning { border-left: 4px solid var(--warning); }
  .toast.info { border-left: 4px solid var(--primary); }
</style>
