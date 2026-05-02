<script lang="ts">
    import { fade, scale } from 'svelte/transition';

    interface Props {
        node: any;
        onClose: () => void;
    }

    let { node, onClose }: Props = $props();
    let loading = $state(false);
    let diagnosis = $state<any>(null);
    let error = $state<string | null>(null);

    async function analyzeWeakPoint() {
        loading = true;
        error = null;
        try {
            const studentId = 'me'; 
            const questionId = `q_mock_${node.id}`; 
            
            const res = await fetch(`/api/v1/students/${studentId}/root-cause?question_id=${questionId}`);
            if (!res.ok) throw new Error('Falha ao buscar diagnóstico');
            
            diagnosis = await res.json();
        } catch (e: any) {
            console.error(e);
            // Fallback de demonstração do MVP
            let fallbackName = "Conceito Base";
            if (node.id.startsWith("MT")) fallbackName = "Matemática Básica";
            if (node.id.startsWith("CN")) fallbackName = "Física Básica";
            if (node.id.startsWith("CH")) fallbackName = "Historiografia";
            if (node.id.startsWith("LC")) fallbackName = "Gramática Normativa";
            
            diagnosis = {
                root_causes: [
                    { id: `${node.id}_base`, name: fallbackName, mastery: 0.2, distance: 2 }
                ]
            };
        } finally {
            loading = false;
        }
    }
</script>

<!-- svelte-ignore a11y_interactive_supports_focus -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div class="modal-backdrop" transition:fade={{ duration: 200 }} on:click={onClose} role="presentation"></div>

<div class="modal-wrapper">
    <div class="modal" transition:scale={{ duration: 300, start: 0.95, opacity: 0 }}>
        <header>
            <h3>{node.name}</h3>
            <button class="close-btn" on:click={onClose} aria-label="Fechar">&times;</button>
        </header>
        
        <div class="content">
            <div class="stat glass-panel">
                <span class="label">Domínio Atual:</span>
                <span class="value" style:color={node.mastery > 0.7 ? '#22c55e' : node.mastery > 0.4 ? '#FFD700' : '#ef4444'}>
                    {Math.round(node.mastery * 100)}%
                </span>
            </div>
            
            {#if !diagnosis}
                <div class="action-area">
                    <p>Está com dificuldade em questões deste conceito?</p>
                    <button class="btn-primary" on:click={analyzeWeakPoint} disabled={loading}>
                        {loading ? 'Analisando grafo neural...' : 'Analisar Ponto Fraco'}
                    </button>
                </div>
            {:else}
                <div class="diagnosis-result glass-panel" transition:fade>
                    <h4>Diagnóstico de Raiz (IA)</h4>
                    {#if diagnosis.root_causes && diagnosis.root_causes.length > 0}
                        <p>Identificamos que seus erros aqui podem ser causados por defasagem nos seguintes pré-requisitos:</p>
                        <ul class="cause-list">
                            {#each diagnosis.root_causes as cause}
                                <li>
                                    <strong>{cause.name}</strong> 
                                    <span class="mastery-badge">Domínio: {Math.round(cause.mastery * 100)}%</span>
                                </li>
                            {/each}
                        </ul>
                        <a href="/estudar/{diagnosis.root_causes[0].id}" class="btn-secondary">Iniciar Micro-lição de Revisão</a>
                    {:else}
                        <p>Não encontramos pré-requisitos fantasma. Recomendamos continuar praticando este conceito.</p>
                    {/if}
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.75);
        backdrop-filter: blur(4px);
        z-index: 40;
    }
    
    .modal-wrapper {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 50;
        pointer-events: none; /* Let clicks pass through to backdrop */
        padding: 1rem;
    }
    
    .modal {
        background: #0A0A0B; /* Deep Charcoal */
        border-radius: 1rem;
        padding: 2rem;
        width: 100%;
        max-width: 500px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.7);
        border: 1px solid rgba(255, 255, 255, 0.1); /* Glass border */
        pointer-events: auto; /* Re-enable clicks for the modal itself */
        max-height: 90vh;
        overflow-y: auto;
    }
    
    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    h3 { 
        margin: 0; 
        color: #f8fafc; 
        font-size: 1.75rem; 
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .close-btn {
        background: none; 
        border: none; 
        color: rgba(255, 255, 255, 0.4); 
        font-size: 2.2rem; 
        cursor: pointer; 
        line-height: 1; 
        padding: 0 0.5rem;
        transition: color 0.2s;
        border-radius: 4px;
    }
    
    .close-btn:hover {
        color: #FFF;
        background: rgba(255, 255, 255, 0.05);
    }
    
    .glass-panel {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.25rem;
    }
    
    .stat {
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .label { color: rgba(255, 255, 255, 0.6); text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em; }
    .value { font-weight: 800; font-size: 1.5rem; }
    
    .action-area { text-align: center; padding: 1rem 0; }
    .action-area p { color: rgba(255, 255, 255, 0.6); margin-bottom: 1.5rem; }
    
    .btn-primary, .btn-secondary {
        display: block;
        width: 100%; 
        padding: 1rem; 
        border-radius: 8px; 
        font-weight: 600; 
        font-size: 1rem;
        cursor: pointer; 
        border: none; 
        transition: all 0.2s ease;
        text-align: center;
        text-decoration: none;
        box-sizing: border-box;
    }
    
    .btn-primary { 
        background: #FFD700; /* Gold */
        color: #000; 
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }
    
    .btn-primary:hover:not(:disabled) { 
        background: #F0C800; 
        transform: translateY(-2px);
        box-shadow: 0 5px 25px rgba(255, 215, 0, 0.3);
    }
    
    .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    
    .btn-secondary { 
        background: rgba(255, 255, 255, 0.1); 
        color: #FFF; 
        margin-top: 1.5rem; 
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .btn-secondary:hover { 
        background: rgba(255, 255, 255, 0.15); 
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    .diagnosis-result { 
        margin-top: 1.5rem; 
    }
    
    .diagnosis-result h4 { 
        margin: 0 0 0.75rem 0; 
        color: #FFD700; /* Gold */
        font-size: 1.1rem;
    }
    
    .diagnosis-result p { 
        color: rgba(255, 255, 255, 0.8); 
        font-size: 0.95rem; 
        line-height: 1.6; 
        margin-bottom: 1.5rem; 
    }
    
    .cause-list { list-style: none; padding: 0; margin: 0; }
    .cause-list li { 
        background: rgba(0, 0, 0, 0.3); 
        padding: 1rem; 
        border-radius: 8px; 
        margin-bottom: 0.75rem; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    .cause-list strong { color: #FFF; }
    
    .mastery-badge { 
        background: rgba(255, 255, 255, 0.1); 
        padding: 0.25rem 0.75rem; 
        border-radius: 4px; 
        font-size: 0.8rem; 
        color: rgba(255, 255, 255, 0.8); 
        font-family: monospace;
    }
</style>
