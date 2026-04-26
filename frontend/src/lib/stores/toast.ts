import { writable } from 'svelte/store';

export interface Toast {
    id: number;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
}

function createToastStore() {
    const { subscribe, update } = writable<Toast[]>([]);

    let count = 0;

    function add(message: string, type: Toast['type'] = 'info', duration = 5000) {
        const id = count++;
        update(all => [{ id, message, type, duration }, ...all]);

        if (duration > 0) {
            setTimeout(() => {
                remove(id);
            }, duration);
        }
    }

    function remove(id: number) {
        update(all => all.filter(t => t.id !== id));
    }

    return {
        subscribe,
        add,
        remove,
        success: (msg: string, dur?: number) => add(msg, 'success', dur),
        error: (msg: string, dur?: number) => add(msg, 'error', dur),
        warning: (msg: string, dur?: number) => add(msg, 'warning', dur),
        info: (msg: string, dur?: number) => add(msg, 'info', dur),
    };
}

export const toasts = createToastStore();
