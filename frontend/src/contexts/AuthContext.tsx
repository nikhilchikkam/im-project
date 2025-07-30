import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';

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

  const authenticatedFetch = useCallback(async (
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
        logout();
        throw new Error('Token refresh failed');
      }
    }

    // Add authorization header
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    };

    const response = await fetch(url, {
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
        
        const retryResponse = await fetch(url, {
          ...options,
          headers: retryHeaders,
        });
        
        return retryResponse;
      } else {
        // Refresh failed, logout user
        logout();
        throw new Error('Authentication failed');
      }
    }

    return response;
  }, [refreshAccessToken, logout, isTokenExpired]);

  return { authenticatedFetch };
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing tokens on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (accessToken && refreshToken) {
        try {
          // Verify token and get user info
          const response = await fetch('/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Token might be expired, try to refresh
            const refreshed = await refreshAccessToken();
            if (!refreshed) {
              // Clear invalid tokens
              localStorage.removeItem('accessToken');
              localStorage.removeItem('refreshToken');
            }
          }
        } catch (error) {
          console.error('Auth initialization error:', error);
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
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch('/api/auth/refresh', {
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
        return true;
      } else {
        // Refresh token is invalid
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
        return false;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
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

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    refreshAccessToken,
    updateUser,
    isTokenExpired,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 