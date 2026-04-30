import { goto } from '$app/navigation';
import { toasts } from '$lib/stores/toast';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

const BASE_URL = `${PUBLIC_API_BASE_URL}/api/v1`;

// Armazena o token CSRF atual em memória
let currentCsrfToken: string | null = null;

async function fetchApi(path: string, options: RequestInit = {}): Promise<any> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Se houver um token CSRF e a requisição não for GET/HEAD, adiciona o header
  if (currentCsrfToken && options.method && !['GET', 'HEAD', 'OPTIONS'].includes(options.method.toUpperCase())) {
    headers['x-csrf-token'] = currentCsrfToken;
  }

  // Tratamento especial para formulários onde não queremos sobrescrever o Content-Type gerado pelo navegador
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  const mergedOptions: RequestInit = {
    ...options,
    credentials: 'include',
    headers,
  };

  try {
    const response = await fetch(`${BASE_URL}${path}`, mergedOptions);

    // Atualiza o token CSRF se o backend enviar um novo
    const newCsrfToken = response.headers.get('x-csrf-token');
    if (newCsrfToken) {
      currentCsrfToken = newCsrfToken;
    }

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
      // Não exibe toast para 403 CSRF (geralmente silencioso ou retentado) se for endpoint específico, 
      // mas vamos deixar genérico por agora
      const detail = errorData.detail || 'Ocorreu um erro na sua solicitação.';
      toasts.error(detail);
      throw new Error(detail);
    }

    // Se a resposta não tiver corpo (ex: 204 No Content), retorna nulo
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error: any) {
    console.error('API Fetch Error:', error);
    if (error.message !== 'Unauthorized') {
      // toasts.error('Não foi possível conectar ao servidor. Verifique sua conexão.');
    }
    throw error;
  }
}

export const api = {
  get: (path: string, options?: RequestInit) => fetchApi(path, { ...options, method: 'GET' }),
  post: <T>(path: string, data: T, options?: RequestInit) =>
    fetchApi(path, { ...options, method: 'POST', body: JSON.stringify(data) }),
  put: <T>(path: string, data: T, options?: RequestInit) =>
    fetchApi(path, { ...options, method: 'PUT', body: JSON.stringify(data) }),
  delete: (path: string, options?: RequestInit) => fetchApi(path, { ...options, method: 'DELETE' }),
  postForm: (path: string, formData: URLSearchParams | FormData, options?: RequestInit) => {
    const isUrlEncoded = formData instanceof URLSearchParams;
    const customOptions = {
      ...options,
      headers: {
        ...options?.headers,
        ...(isUrlEncoded ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}),
      },
      body: formData,
    };
    return fetchApi(path, { ...customOptions, method: 'POST' });
  },
  // Método auxiliar para obter o primeiro token (chamado após login/app load)
  fetchCsrfToken: async () => {
    try {
      const res = await fetch(`${BASE_URL}/auth/csrf-token`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        currentCsrfToken = data.csrf_token;
      }
    } catch (e) {
      console.warn("Could not pre-fetch CSRF token");
    }
  }
};
