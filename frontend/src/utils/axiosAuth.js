/**
 * axiosAuth — pre-configured axios instance that automatically injects
 * the JWT Authorization header from localStorage for every request.
 *
 * Usage: import axiosAuth from '../utils/axiosAuth';
 *        axiosAuth.get('/api/transactions')
 */

import axios from 'axios';

const axiosAuth = axios.create({
  // Use absolute URL so it works regardless of Vite proxy config
  baseURL: 'http://localhost:5000',
});

// Inject Bearer token before every request
axiosAuth.interceptors.request.use((config) => {
  const token = localStorage.getItem('finverde_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Redirect to /signin on 401 responses
axiosAuth.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('finverde_token');
      localStorage.removeItem('finverde_user');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);

export default axiosAuth;
