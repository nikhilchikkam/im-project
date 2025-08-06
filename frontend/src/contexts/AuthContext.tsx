import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import TokenRefreshToast from '../components/ui/TokenRefreshToast';

interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  company_name?: string;
  phone?: string;
  business_id?: string;
  auth_provider: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (accessToken: string, refreshToken: string, userData: User) => void;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
  isTokenExpired: (token: string) => boolean;
  startAutoRefresh: () => void;
  stopAutoRefresh: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Custom hook for making authenticated API calls with automatic token refresh
export const useAuthenticatedFetch = () => {
  const { refreshAccessToken, logout, isTokenExpired } = useAuth();
  const apiUrl = import.meta.env.VITE_API_URL || '';

  const authenticatedFetch = useCallback(async (
    url: string, 
    options: RequestInit = {}
  ): Promise<Response> => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      throw new Error('No access token available');
    }

    // Prepend base URL if url is relative
    const fullUrl = url.startsWith('http') ? url : `${apiUrl}${url}`;

    // Check if token is expired before making the request
    if (isTokenExpired(accessToken)) {
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        logout();
        throw new Error('Token refresh failed');
      }
    }

    // Add authorization header
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    };

    const response = await fetch(fullUrl, {
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
        const retryResponse = await fetch(fullUrl, {
          ...options,
          headers: retryHeaders,
        });
        return retryResponse;
      } else {
        logout();
        throw new Error('Authentication failed');
      }
    }

    return response;
  }, [refreshAccessToken, logout, isTokenExpired, apiUrl]);

  return { authenticatedFetch };
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefreshInterval, setAutoRefreshInterval] = useState<number | null>(null);
  const [lastActivity, setLastActivity] = useState<number>(Date.now());
  const [toast, setToast] = useState<{
    isVisible: boolean;
    message: string;
    type: 'info' | 'success' | 'error';
  }>({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Check for existing tokens on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (accessToken && refreshToken) {
        try {
          // Verify token and get user info
          const apiUrl = import.meta.env.VITE_API_URL || '';
          const meUrl = apiUrl ? `${apiUrl}/api/auth/me` : '/api/auth/me';
          
          const response = await fetch(meUrl, {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
            // Add timeout for production reliability
            signal: AbortSignal.timeout(10000), // 10 second timeout
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
            // Start auto-refresh for existing session
            setTimeout(() => startAutoRefresh(), 1000);
          } else {
            // Token might be expired, try to refresh
            const refreshed = await refreshAccessToken();
            if (refreshed) {
              // Get user data after successful refresh
              const userResponse = await fetch(meUrl, {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                },
                signal: AbortSignal.timeout(10000),
              });
              if (userResponse.ok) {
                const userData = await userResponse.json();
                setUser(userData);
                // Start auto-refresh for existing session
                setTimeout(() => startAutoRefresh(), 1000);
              }
            } else {
              // Clear invalid tokens
              localStorage.removeItem('accessToken');
              localStorage.removeItem('refreshToken');
            }
          }
        } catch (error) {
          if (error instanceof Error && error.name === 'AbortError') {
            console.error('Auth initialization timeout');
          } else {
            console.error('Auth initialization error:', error);
          }
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = (accessToken: string, refreshToken: string, userData: User) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setUser(userData);
    // Start auto-refresh when user logs in
    setTimeout(() => startAutoRefresh(), 1000);
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
    stopAutoRefresh();
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (!refreshToken) {
      console.warn('No refresh token available');
      return false;
    }

    try {
      // Use relative URL for production compatibility
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const refreshUrl = apiUrl ? `${apiUrl}/api/auth/refresh` : '/api/auth/refresh';
      
      const response = await fetch(refreshUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
        // Add timeout for production reliability
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.access_token);
        
        // Update refresh token if a new one is provided
        if (data.refresh_token) {
          localStorage.setItem('refreshToken', data.refresh_token);
        }
        
        // Update user data if provided
        if (data.user) {
          setUser(data.user);
        }
        
        console.log('Token refresh successful');
        return true;
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Token refresh failed:', response.status, errorData);
        
        // Clear invalid tokens
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
        return false;
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('Token refresh timeout');
      } else {
        console.error('Token refresh error:', error);
      }
      return false;
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp;
      // Add 30 second buffer to refresh before actual expiration
      return Date.now() >= (exp * 1000) - 30000;
    } catch (e) {
      return true; // Assume expired if parsing fails
    }
  };

  // Get token expiration time in milliseconds
  const getTokenExpirationTime = (token: string): number => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000; // Convert to milliseconds
    } catch (e) {
      return 0;
    }
  };

  // Debug function to log token info (only in development)
  const debugTokenInfo = () => {
    // Only show debug info in development
    if (import.meta.env.PROD) {
      console.log('Debug functions are disabled in production');
      return;
    }

    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (accessToken) {
      try {
        const payload = JSON.parse(atob(accessToken.split('.')[1]));
        const expiresAt = new Date(payload.exp * 1000);
        const timeUntilExpiration = payload.exp * 1000 - Date.now();
        
        console.log('Access Token Info:');
        console.log('  - Expires at:', expiresAt.toLocaleString());
        console.log('  - Time until expiration:', Math.round(timeUntilExpiration / 1000), 'seconds');
        console.log('  - Token type:', payload.type);
        console.log('  - User ID:', payload.sub);
        console.log('  - Full payload:', payload);
      } catch (e) {
        console.log('Error parsing access token:', e);
      }
    } else {
      console.log('No access token found');
    }
    
    if (refreshToken) {
      try {
        const payload = JSON.parse(atob(refreshToken.split('.')[1]));
        const expiresAt = new Date(payload.exp * 1000);
        
        console.log('Refresh Token Info:');
        console.log('  - Expires at:', expiresAt.toLocaleString());
        console.log('  - Token type:', payload.type);
        console.log('  - User ID:', payload.sub);
      } catch (e) {
        console.log('Error parsing refresh token:', e);
      }
    } else {
      console.log('No refresh token found');
    }
  };

  // Expose debug function globally for easy access (only in development)
  useEffect(() => {
    if (typeof window !== 'undefined' && !import.meta.env.PROD) {
      (window as any).debugTokenInfo = debugTokenInfo;
    }
  }, []);

  // Update last activity timestamp
  const updateActivity = () => {
    setLastActivity(Date.now());
  };

  // Start automatic token refresh
  const startAutoRefresh = () => {
    // Clear any existing interval
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
    }

    const interval = setInterval(async () => {
      const accessToken = localStorage.getItem('accessToken');
      if (!accessToken || !user) {
        return;
      }

      // Check if user has been inactive for more than 2 minutes (reduced from 5)
      const inactiveTime = Date.now() - lastActivity;
      if (inactiveTime > 2 * 60 * 1000) {
        // User is inactive, don't refresh token
        console.log('User inactive for', Math.round(inactiveTime / 1000), 'seconds, skipping refresh');
        return;
      }

      // Check if token will expire in the next 30 seconds (reduced from 5 minutes)
      const expirationTime = getTokenExpirationTime(accessToken);
      const timeUntilExpiration = expirationTime - Date.now();
      
      if (timeUntilExpiration > 0 && timeUntilExpiration < 30 * 1000) {
        console.log('Auto-refreshing token... (expires in', Math.round(timeUntilExpiration / 1000), 'seconds)');
        setToast({
          isVisible: true,
          message: 'Refreshing your session...',
          type: 'info'
        });
        
        const success = await refreshAccessToken();
        if (success) {
          setToast({
            isVisible: true,
            message: 'Session refreshed successfully!',
            type: 'success'
          });
        } else {
          console.log('Auto-refresh failed, logging out user');
          setToast({
            isVisible: true,
            message: 'Session expired. Please log in again.',
            type: 'error'
          });
          setTimeout(() => logout(), 2000);
        }
      }
    }, 30000); // Check every 30 seconds (reduced from 60)

    setAutoRefreshInterval(interval);
  };

  // Stop automatic token refresh
  const stopAutoRefresh = () => {
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      setAutoRefreshInterval(null);
    }
  };

  // Set up user activity listeners
  useEffect(() => {
    if (!user) {
      stopAutoRefresh();
      return;
    }

    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      updateActivity();
    };

    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    // Start auto-refresh when user is logged in
    startAutoRefresh();

    return () => {
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
      stopAutoRefresh();
    };
  }, [user]);

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    refreshAccessToken,
    updateUser,
    isTokenExpired,
    startAutoRefresh,
    stopAutoRefresh,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
      <TokenRefreshToast
        isVisible={toast.isVisible}
        message={toast.message}
        type={toast.type}
        onClose={() => setToast(prev => ({ ...prev, isVisible: false }))}
      />
    </AuthContext.Provider>
  );
}; 