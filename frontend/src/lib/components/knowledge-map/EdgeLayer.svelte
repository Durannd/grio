<script lang="ts">
    export type NodeInfo = {
        id: string;
        x: number;
        y: number;
    };

    export type EdgeInfo = {
        source: string;
        target: string;
        type: 'DEPENDS_ON' | 'UNLOCKS' | string;
    };

    interface Props {
        edges?: EdgeInfo[];
        nodes?: NodeInfo[];
    }

    let { edges = [], nodes = [] }: Props = $props();

    // Map for fast node lookups
    let nodeMap = $derived(
        nodes.reduce((map, node) => {
            map[node.id] = node;
            return map;
        }, {} as Record<string, NodeInfo>)
    );
</script>

<g class="edge-layer">
    {#each edges as edge}
        {@const source = nodeMap[edge.source]}
        {@const target = nodeMap[edge.target]}
        
        {#if source && target}
            <line 
                x1={source.x} 
                y1={source.y} 
                x2={target.x} 
                y2={target.y} 
                class="edge {edge.type.toLowerCase()}" 
            />
        {/if}
    {/each}
</g>

<style>
    .edge-layer {
        pointer-events: none;
    }
    
    .edge {
        stroke-width: 2px;
        opacity: 0.3;
        transition: stroke 0.3s ease, opacity 0.3s ease;
    }
    
    .edge.depends_on {
        stroke: rgba(255, 255, 255, 0.4); /* Subdued light */
        stroke-dasharray: 4 4;
    }
    
    .edge.unlocks {
        stroke: #FFD700; /* Gold */
        opacity: 0.5;
    }
</style>
