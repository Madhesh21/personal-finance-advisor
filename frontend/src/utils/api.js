/**
 * apiFetch — lightweight fetch wrapper that automatically injects
 * the JWT Authorization header from localStorage.
 */

const API_BASE = 'http://localhost:5000';

function getToken() {
  return localStorage.getItem('finverde_token');
}

export async function apiFetch(path, options = {}) {
  const token      = getToken();
  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  return response;
}
