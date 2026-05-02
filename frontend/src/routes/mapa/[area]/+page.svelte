<script lang="ts">
    import { page } from '$app/stores';
    import GraphViewport from '$lib/components/knowledge-map/GraphViewport.svelte';
    
    let area = $derived($page.params.area.toUpperCase());
    let { data } = $props();
</script>

<svelte:head>
    <title>Mapa - {area} | Griô</title>
</svelte:head>

<div class="mapa-wrapper">
    {#if data.nodes && data.nodes.length > 0}
        <GraphViewport nodes={data.nodes} edges={data.edges} />
    {:else}
        <div class="placeholder-content">
            <p>Carregando mapa de conhecimento para <strong>{area}</strong>...</p>
        </div>
    {/if}
</div>

<style>
    .mapa-wrapper {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .placeholder-content {
        color: #94a3b8;
    }
    strong { color: #f8fafc; }
</style>
