<script lang="ts">
    import { page } from '$app/stores';
    let { children } = $props();
    
    let area = $derived($page.params.area.toUpperCase());
</script>

<div class="map-layout">
    <header class="map-header">
        <nav>
            <a href="/dashboard" class="back-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                Voltar
            </a>
            <h2>Mapa de Conhecimento: {area}</h2>
        </nav>
    </header>
    
    <main class="map-content">
        {@render children()}
    </main>
</div>

<style>
    .map-layout {
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
        background-color: #0A0A0B; /* Deep Charcoal/Navy */
        color: #f8fafc; /* slate-50 */
    }
    
    .map-header {
        padding: 1rem 1.5rem;
        background-color: rgba(10, 10, 11, 0.8);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05); /* glass border */
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        z-index: 10;
    }
    
    .map-header nav {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .back-link {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        color: #FFD700; /* Gold */
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease, text-shadow 0.2s ease;
    }
    
    .back-link:hover {
        color: #F0C800; /* Bright Gold */
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    .map-header h2 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: #FFF;
        letter-spacing: 0.02em;
    }
    
    .map-content {
        flex: 1;
        position: relative;
        overflow: hidden;
    }
</style>
