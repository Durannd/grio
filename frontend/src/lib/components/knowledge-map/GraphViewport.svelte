<script lang="ts">
    import ConceptNode from './ConceptNode.svelte';
    import EdgeLayer from './EdgeLayer.svelte';
    import RootCauseSheet from './RootCauseSheet.svelte';
    
    interface Props {
        nodes: any[];
        edges: any[];
    }
    
    let { nodes = [], edges = [] }: Props = $props();
    
    // Convert nodes to local reactive state so they can be dragged
    let localNodes = $state([...nodes]);
    
    let selectedId = $state<string | null>(null);
    let selectedNode = $derived(localNodes.find(n => n.id === selectedId));
    
    // Pan & Zoom state
    let svgContainer: SVGSVGElement;
    let viewBox = $state({ x: 0, y: 0, w: 600, h: 600 });
    let isPanning = $state(false);
    let startPan = { x: 0, y: 0 };
    
    function onWheel(e: WheelEvent) {
        e.preventDefault();
        const zoomIntensity = 0.1;
        const zoomFactor = e.deltaY > 0 ? (1 + zoomIntensity) : (1 - zoomIntensity);
        
        // Ensure reasonable zoom limits
        if (viewBox.w * zoomFactor < 200 || viewBox.w * zoomFactor > 3000) return;
        
        // Zoom towards center for simplicity
        const dw = viewBox.w * zoomFactor - viewBox.w;
        const dh = viewBox.h * zoomFactor - viewBox.h;
        
        viewBox.x -= dw / 2;
        viewBox.y -= dh / 2;
        viewBox.w *= zoomFactor;
        viewBox.h *= zoomFactor;
    }
    
    function onPointerDown(e: PointerEvent) {
        if (e.target === svgContainer) {
            e.preventDefault(); // Prevent native drag/select
            isPanning = true;
            startPan = { x: e.clientX, y: e.clientY };
            svgContainer.setPointerCapture(e.pointerId);
        }
    }
    
    function onPointerMove(e: PointerEvent) {
        if (isPanning) {
            const dx = (e.clientX - startPan.x) * (viewBox.w / svgContainer.clientWidth);
            const dy = (e.clientY - startPan.y) * (viewBox.h / svgContainer.clientHeight);
            viewBox.x -= dx;
            viewBox.y -= dy;
            startPan = { x: e.clientX, y: e.clientY };
        }
    }
    
    function onPointerUp(e: PointerEvent) {
        if (isPanning) {
            isPanning = false;
            svgContainer.releasePointerCapture(e.pointerId);
        }
    }

    // Node Dragging
    function handleNodeDrag(id: string, dx: number, dy: number) {
        // Convert screen delta to SVG coordinates delta
        const scaleX = viewBox.w / svgContainer.clientWidth;
        const scaleY = viewBox.h / svgContainer.clientHeight;
        const nodeIndex = localNodes.findIndex(n => n.id === id);
        if (nodeIndex !== -1) {
            localNodes[nodeIndex].x += dx * scaleX;
            localNodes[nodeIndex].y += dy * scaleY;
            localNodes = [...localNodes]; // trigger reactivity
        }
    }
</script>

<div class="viewport-container">
    <svg 
        bind:this={svgContainer}
        class="graph-svg" 
        viewBox="{viewBox.x} {viewBox.y} {viewBox.w} {viewBox.h}"
        onwheel={onWheel}
        onpointerdown={onPointerDown}
        onpointermove={onPointerMove}
        onpointerup={onPointerUp}
        onpointerleave={onPointerUp}
    >
        <EdgeLayer {edges} nodes={localNodes} />
        
        {#each localNodes as node}
            <ConceptNode 
                id={node.id}
                name={node.name}
                x={node.x}
                y={node.y}
                mastery={node.mastery}
                selected={selectedId === node.id}
                onclick={(id) => selectedId = id}
                ondrag={handleNodeDrag}
            />
        {/each}
    </svg>
    
    {#if selectedNode}
        <RootCauseSheet node={selectedNode} onClose={() => selectedId = null} />
    {/if}
</div>

<style>
    .viewport-container {
        width: 100%;
        height: 100%;
        position: relative;
        background-color: #0A0A0B; /* Deep Charcoal/Navy */
        background-image: radial-gradient(rgba(255, 215, 0, 0.1) 1px, transparent 1px); /* Subtle gold dots */
        background-size: 40px 40px;
        background-position: center center;
        overflow: hidden;
        user-select: none;
        -webkit-user-select: none;
    }
    
    .graph-svg {
        width: 100%;
        height: 100%;
        display: block;
        cursor: grab;
        touch-action: none;
    }
    
    .graph-svg:active {
        cursor: grabbing;
    }
</style>
