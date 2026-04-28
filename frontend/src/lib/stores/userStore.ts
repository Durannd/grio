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

// Store central de usuário
export const user = writable<User | null>(null);
export const isLoading = writable<boolean>(true);

/**
 * Carrega os dados do usuário atual a partir da API com lógica de retry.
 */
export async function loadUser(retryCount = 0) {
  if (!browser) return;

  // Só mostra o estado de carregamento global na primeira tentativa
  if (retryCount === 0) isLoading.set(true);
  
  try {
    console.log(`[UserStore] Tentando carregar usuário... (Tentativa ${retryCount + 1})`);
    const userData = await api.get('/auth/me') as User;
    
    if (userData && userData.id) {
      console.log('[UserStore] Usuário identificado:', userData.email);
      user.set(userData);
    } else {
      user.set(null);
    }
    // Sucesso: garante que o loading pare
    isLoading.set(false);
  } catch (error: any) {
    console.warn(`[UserStore] Erro no carregamento (Tentativa ${retryCount + 1}):`, error.message);
    
    // Se for 401, tentamos mais uma vez após um breve respiro (processamento de cookie)
    if (error.message === 'Unauthorized' && retryCount < 2) {
      await new Promise(resolve => setTimeout(resolve, 400));
      return loadUser(retryCount + 1);
    }
    
    // Se falhou todas as vezes, limpa o usuário e encerra o loading
    user.set(null);
    isLoading.set(false);
  }
}

/**
 * Limpa o estado do usuário localmente.
 */
export function logoutUser() {
  user.set(null);
  isLoading.set(false);
}

// Inicialização automática no navegador
if (browser) {
  loadUser();
}
