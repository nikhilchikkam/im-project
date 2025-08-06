import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Toast } from '../../components/ui/Toast';
import { useAuth } from '../../contexts/AuthContext';

const GoogleOAuthPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Check for tokens in URL parameters (from backend redirect)
        const accessToken = searchParams.get('access_token');
        const refreshToken = searchParams.get('refresh_token');
        const userId = searchParams.get('user_id');
        const email = searchParams.get('email');
        const firstName = searchParams.get('first_name');
        const lastName = searchParams.get('last_name');
        const userExisted = searchParams.get('user_existed') === 'true';

        // Check for error in URL parameters
        const error = searchParams.get('error');

        console.log('OAuth callback params:', { 
          accessToken: !!accessToken, 
          refreshToken: !!refreshToken, 
          userId, 
          email, 
          error 
        });

        if (error) {
          setError(`OAuth authentication failed: ${error}`);
          setIsLoading(false);
          return;
        }

        if (accessToken && refreshToken && userId && email) {
          // Create user object from URL parameters
          const user = {
            id: parseInt(userId),
            email: email,
            first_name: firstName || undefined,
            last_name: lastName || undefined,
            company_name: undefined,
            phone: undefined,
            business_id: undefined,
            auth_provider: 'google',
            is_verified: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };

          // Call the login function to update AuthContext and trigger data fetching
          login(accessToken, refreshToken, user);
          
          // Show success message
          if (userExisted) {
            setToast({ message: 'Welcome back! Your existing account has been linked to Google.', type: 'success' });
          } else {
            setToast({ message: 'Account created successfully with Google!', type: 'success' });
          }
          
          // Redirect to products page after successful login
          setTimeout(() => {
            navigate('/products');
          }, 1500); // Small delay to ensure context updates are processed
        } else {
          setError('Invalid OAuth response. Please try again.');
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError('Network error. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    handleOAuthCallback();
  }, [searchParams, navigate, login]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Completing Google sign-in...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="w-full bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </>
  );
};

export default GoogleOAuthPage; 