<script lang="ts">
    interface Props {
        id: string;
        name: string;
        x: number;
        y: number;
        mastery?: number;
        selected?: boolean;
        onclick?: (id: string) => void;
        ondrag?: (id: string, dx: number, dy: number) => void;
    }

    let { id, name, x, y, mastery = 0, selected = false, onclick, ondrag }: Props = $props();

    // calculate circumference for progress ring, r=20
    const radius = 20;
    const circumference = 2 * Math.PI * radius;
    const offset = $derived(circumference - (mastery * circumference));

    // Dragging state
    let isDragging = $state(false);
    let startPos = { x: 0, y: 0 };
    let dragHasMoved = $state(false);

    function onPointerDown(e: PointerEvent) {
        // Stop propagation so viewport doesn't pan
        e.stopPropagation();
        e.preventDefault(); // Prevent native dragging/selection of elements
        isDragging = true;
        dragHasMoved = false;
        startPos = { x: e.clientX, y: e.clientY };
        (e.currentTarget as SVGElement).setPointerCapture(e.pointerId);
    }

    function onPointerMove(e: PointerEvent) {
        if (isDragging) {
            dragHasMoved = true;
            const dx = e.clientX - startPos.x;
            const dy = e.clientY - startPos.y;
            startPos = { x: e.clientX, y: e.clientY };
            ondrag?.(id, dx, dy);
        }
    }

    function onPointerUp(e: PointerEvent) {
        if (isDragging) {
            isDragging = false;
            (e.currentTarget as SVGElement).releasePointerCapture(e.pointerId);
            // If it was just a click and not a drag, trigger onclick
            if (!dragHasMoved) {
                onclick?.(id);
            }
        }
    }
</script>

<g 
    class="node" 
    class:selected={selected} 
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointerleave={onPointerUp}
    onkeydown={(e) => e.key === 'Enter' && onclick?.(id)}
    role="button"
    tabindex="0"
>
    <!-- Base background circle -->
    <circle cx={x} cy={y} r="24" class="base-circle" />

    <!-- Progress circle -->
    <circle 
        cx={x} 
        cy={y} 
        r={radius} 
        class="progress-circle" 
        style:stroke-dasharray="{circumference}"
        style:stroke-dashoffset="{offset}"
        transform="rotate(-90 {x} {y})"
    />

    <!-- Inner circle (visual dot) -->
    <circle cx={x} cy={y} r="16" class="inner-circle" />

    <text x={x} y={y + 40} text-anchor="middle" class="label">
        {name}
    </text>
</g>

<style>
    .node {
        cursor: grab;
        outline: none;
    }
    
    .node:active {
        cursor: grabbing;
    }
    
    .node:hover .inner-circle {
        fill: #1A1A1D; /* Slightly lighter than deep charcoal */
    }

    .node.selected .inner-circle {
        fill: rgba(255, 215, 0, 0.1); /* Gold tint */
        stroke: #FFD700; /* Gold */
        stroke-width: 2px;
    }

    .node.selected .base-circle {
        stroke: #FFD700; /* Gold highlight on base */
        filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.4));
    }

    .node.selected .label {
        fill: #FFD700; /* Gold */
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }

    .base-circle {
        fill: #0A0A0B; /* Deep Charcoal */
        stroke: rgba(255, 255, 255, 0.1); /* Subtle glass edge */
        stroke-width: 4px;
        transition: stroke 0.3s ease, filter 0.3s ease;
    }

    .progress-circle {
        fill: transparent;
        stroke: #22c55e; /* Keep green for progress/mastery */
        stroke-width: 4px;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.6s ease-out;
    }

    .inner-circle {
        fill: #121214; /* Darker center */
        transition: fill 0.2s ease-in-out, stroke 0.2s ease-in-out;
    }

    .label {
        fill: rgba(255, 255, 255, 0.6); /* Muted white */
        font-size: 12px;
        font-family: system-ui, -apple-system, sans-serif;
        pointer-events: none;
        transition: fill 0.2s ease-in-out;
    }
</style>
