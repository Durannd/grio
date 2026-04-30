import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		watch: {
			usePolling: true, // Ativa polling para HMR funcionar dentro do Docker no Windows
			interval: 100
		}
	}
});
