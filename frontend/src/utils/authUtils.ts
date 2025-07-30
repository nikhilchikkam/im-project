/**
 * Utility functions for handling authentication and token management
 */

// Get API base URL from environment
const getApiBaseUrl = () => {
  return import.meta.env.VITE_API_URL || '';
};

// Simple notification function
const showNotification = (message: string, type: 'success' | 'info' | 'warning' | 'error' = 'info') => {
  // Create a simple toast notification
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-md text-white text-sm shadow-lg transition-opacity duration-300 ${
    type === 'success' ? 'bg-green-500' :
    type === 'info' ? 'bg-blue-500' :
    type === 'warning' ? 'bg-yellow-500' :
    'bg-red-500'
  }`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
};

// Check if a JWT token is expired
export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp;
    // Add 30 second buffer to refresh before actual expiration
    return Date.now() >= (exp * 1000) - 30000;
  } catch (e) {
    return true; // Assume expired if parsing fails
  }
};

// Refresh access token using refresh token
export const refreshAccessToken = async (): Promise<boolean> => {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(`${getApiBaseUrl()}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.access_token);
      // Update refresh token if a new one is provided
      if (data.refresh_token) {
        localStorage.setItem('refreshToken', data.refresh_token);
      }
      showNotification('Session refreshed successfully', 'success');
      return true;
    } else {
      // Refresh token is invalid
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      return false;
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
};

// Make an authenticated fetch request with automatic token refresh
export const authenticatedFetch = async (
  url: string, 
  options: RequestInit = {}
): Promise<Response> => {
  const accessToken = localStorage.getItem('accessToken');
  
  if (!accessToken) {
    throw new Error('No access token available');
  }

  // Check if token is expired before making the request
  if (isTokenExpired(accessToken)) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      // Clear tokens and redirect to login
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('Token refresh failed');
    }
  }

  // Add authorization header
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
  };

  const response = await fetch(`${getApiBaseUrl()}${url}`, {
    ...options,
    headers,
  });

  // If we get a 401, try to refresh the token and retry once
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry the request with the new token
      const retryHeaders = {
        ...options.headers,
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
      };
      
      const retryResponse = await fetch(`${getApiBaseUrl()}${url}`, {
        ...options,
        headers: retryHeaders,
      });
      
      return retryResponse;
    } else {
      // Refresh failed, logout user
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('Authentication failed');
    }
  }

  return response;
}; 