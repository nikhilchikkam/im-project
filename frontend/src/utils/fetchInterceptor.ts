/**
 * Global fetch interceptor for automatic token refresh
 */

import { isTokenExpired, refreshAccessToken } from './authUtils';

// Store the original fetch function
const originalFetch = window.fetch;

// Create a custom fetch function that handles token refresh
const fetchWithTokenRefresh = async (
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> => {
  // Check if this is an API call to our backend
  const url = typeof input === 'string' ? input : input.toString();
  const isApiCall = url.startsWith('/api/') || url.includes('localhost:5173/api/');
  
  if (!isApiCall) {
    // For non-API calls, use the original fetch
    return originalFetch(input, init);
  }

  // Get the current access token
  const accessToken = localStorage.getItem('accessToken');
  
  if (!accessToken) {
    // No token available, proceed with original request
    return originalFetch(input, init);
  }

  // Check if token is expired
  if (isTokenExpired(accessToken)) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      // Token refresh failed, redirect to login
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('Token refresh failed');
    }
  }

  // Add authorization header if not already present
  const headers = new Headers(init?.headers);
  if (!headers.has('Authorization')) {
    const newToken = localStorage.getItem('accessToken');
    if (newToken) {
      headers.set('Authorization', `Bearer ${newToken}`);
    }
  }

  // Make the request
  const response = await originalFetch(input, {
    ...init,
    headers,
  });

  // If we get a 401, try to refresh the token and retry once
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry the request with the new token
      const retryHeaders = new Headers(init?.headers);
      const newToken = localStorage.getItem('accessToken');
      if (newToken) {
        retryHeaders.set('Authorization', `Bearer ${newToken}`);
      }
      
      const retryResponse = await originalFetch(input, {
        ...init,
        headers: retryHeaders,
      });
      
      return retryResponse;
    } else {
      // Refresh failed, redirect to login
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('Authentication failed');
    }
  }

  return response;
};

// Replace the global fetch function
window.fetch = fetchWithTokenRefresh;

// Export the original fetch for cases where we don't want the interceptor
export { originalFetch as fetch }; 