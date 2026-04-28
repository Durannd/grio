/**
 * CSRF Token Management
 * Gerencia obtenção e envio de tokens CSRF para requisições seguras
 */

import { api } from './api';

interface CSRFTokenResponse {
  csrf_token: string;
  expires_at: string;
}

let currentToken: string | null = null;
let tokenExpiresAt: Date | null = null;

/**
 * Obtém um novo token CSRF do servidor
 */
export async function getCsrfToken(): Promise<string> {
  try {
    const response = (await api.get('/auth/csrf-token')) as CSRFTokenResponse;
    currentToken = response.csrf_token;
    tokenExpiresAt = new Date(response.expires_at);
    return response.csrf_token;
  } catch (error) {
    console.error('Failed to get CSRF token:', error);
    throw error;
  }
}

/**
 * Retorna o token CSRF atual, obtendo um novo se necessário
 */
export async function getOrRefreshCsrfToken(): Promise<string> {
  if (currentToken && tokenExpiresAt && new Date() < tokenExpiresAt) {
    return currentToken;
  }
  return await getCsrfToken();
}

/**
 * Addon para requisições POST/PUT/DELETE que automaticamente adiciona CSRF token
 */
export async function postWithCsrf<T>(path: string, data: T): Promise<unknown> {
  const token = await getOrRefreshCsrfToken();
  return api.post(path, data, {
    headers: {
      'X-CSRF-Token': token,
    },
  });
}

export async function putWithCsrf<T>(path: string, data: T): Promise<unknown> {
  const token = await getOrRefreshCsrfToken();
  return api.put(path, data, {
    headers: {
      'X-CSRF-Token': token,
    },
  });
}

export async function deleteWithCsrf(path: string): Promise<unknown> {
  const token = await getOrRefreshCsrfToken();
  return api.delete(path, {
    headers: {
      'X-CSRF-Token': token,
    },
  });
}

// Pré-carregar um token quando o app inicia
export async function initializeCsrfToken(): Promise<void> {
  try {
    await getCsrfToken();
  } catch (error) {
    console.warn('Could not pre-load CSRF token:', error);
    // Não é crítico, será obtido na primeira requisição
  }
}
