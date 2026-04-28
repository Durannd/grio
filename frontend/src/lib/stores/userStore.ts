import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { api } from '$lib/api';

export interface User {
  id: number;
  name: string;
  email: string;
  avatar_url?: string;
  is_diagnostic_completed: boolean;
}

const initialUser: User | null = null;

const userStore = writable<User | null>(initialUser);

async function loadUser() {
  if (!browser) return;

  try {
    const userData: User = await api.get('/auth/me');
    if (userData) {
      userStore.set(userData);
    } else {
      userStore.set(null);
    }
  } catch (error) {
    // A api.get já lida com o log e toast de erro
    userStore.set(null);
  }
}

// Carrega o usuário quando a store é inicializada no navegador
if (browser) {
  loadUser();
}

export default {
  subscribe: userStore.subscribe,
  set: userStore.set,
  load: loadUser,
  logout: () => userStore.set(null),
};
