import { goto } from '$app/navigation';
import { toasts } from '$lib/stores/toast';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

const BASE_URL = `${PUBLIC_API_BASE_URL}/api/v1`;

async function fetchApi(path: string, options: RequestInit = {}) {
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
      goto('/login');
      toasts.error('Sua sessão expirou. Por favor, faça login novamente.');
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
  } catch (error) {
    console.error('API Fetch Error:', error);
    if (!(error instanceof Error && error.message === 'Unauthorized')) {
      toasts.error('Não foi possível conectar ao servidor. Verifique sua conexão.');
    }
    throw error;
  }
}

export const api = {
  get: (path: string, options?: RequestInit) => fetchApi(path, { ...options, method: 'GET' }),
  post: (path: string, data: any, options?: RequestInit) =>
    fetchApi(path, { ...options, method: 'POST', body: JSON.stringify(data) }),
  put: (path: string, data: any, options?: RequestInit) =>
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
