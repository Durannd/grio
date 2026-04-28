import { goto } from '$app/navigation';
import { toasts } from '$lib/stores/toast';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

const BASE_URL = `${PUBLIC_API_BASE_URL}/api/v1`;

async function fetchApi(path: string, options: RequestInit = {}): Promise<unknown> {
  const defaultOptions: RequestInit = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const mergedOptions: RequestInit = {
    ...options,
    ...defaultOptions,
  };

  try {
    const response = await fetch(`${BASE_URL}${path}`, mergedOptions);

    if (response.status === 401) {
      // Não redireciona se estivermos apenas verificando a sessão atual
      if (path !== '/auth/me') {
        goto('/login');
        toasts.error('Sua sessão expirou. Por favor, faça login novamente.');
      }
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      toasts.error(errorData.detail || 'Ocorreu um erro na sua solicitação.');
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Se a resposta não tiver corpo (ex: 204 No Content), retorna nulo
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error: unknown) {
    const err = error instanceof Error ? error : new Error(String(error));
    console.error('API Fetch Error:', err);
    if (!(err instanceof Error && err.message === 'Unauthorized')) {
      toasts.error('Não foi possível conectar ao servidor. Verifique sua conexão.');
    }
    throw err;
  }
}

export const api = {
  get: (path: string, options?: RequestInit) => fetchApi(path, { ...options, method: 'GET' }),
  post: <T>(path: string, data: T, options?: RequestInit) =>
    fetchApi(path, { ...options, method: 'POST', body: JSON.stringify(data) }),
  put: <T>(path: string, data: T, options?: RequestInit) =>
    fetchApi(path, { ...options, method: 'PUT', body: JSON.stringify(data) }),
  delete: (path: string, options?: RequestInit) => fetchApi(path, { ...options, method: 'DELETE' }),
  postForm: (path: string, formData: URLSearchParams, options?: RequestInit) => {
    const customOptions = {
      ...options,
      headers: {
        ...options?.headers,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    };
    return fetchApi(path, { ...customOptions, method: 'POST' });
  },
};
