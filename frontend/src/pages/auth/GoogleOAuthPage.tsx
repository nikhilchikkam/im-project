import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/Button';

export const GoogleOAuthPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [error, setError] = useState('');

  useEffect(() => {
    const handleGoogleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');
      
      if (error) {
        setStatus('error');
        setError('Google authentication was cancelled or failed.');
        return;
      }

      if (!code) {
        setStatus('error');
        setError('No authorization code received from Google.');
        return;
      }

      try {
        const response = await fetch('/api/auth/google/callback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        });

        const data = await response.json();

        if (response.ok) {
          // Login the user with the received tokens
          login(data.access_token, data.refresh_token, data.user);
          setStatus('success');
          
          // Redirect to home page after a short delay
          setTimeout(() => {
            navigate('/');
          }, 2000);
        } else {
          setStatus('error');
          setError(data.detail || 'Google authentication failed.');
        }
      } catch (err) {
        setStatus('error');
        setError('Network error. Please try again.');
      }
    };

    handleGoogleCallback();
  }, [searchParams, login, navigate]);

  if (status === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900">Processing Google Login...</h2>
            <p className="mt-2 text-sm text-gray-600">
              Please wait while we complete your Google authentication.
            </p>
            <div className="mt-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900">Google Login Successful!</h2>
            <p className="mt-2 text-sm text-gray-600">
              You have been successfully logged in with Google. Redirecting to home page...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="mt-6 text-2xl font-bold text-gray-900">Google Login Failed</h2>
          <p className="mt-2 text-sm text-gray-600">{error}</p>
          <div className="mt-6 space-y-3">
            <Button
              onClick={() => navigate('/login')}
              className="w-full"
            >
              Try Again
            </Button>
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              className="w-full"
            >
              Go to Home
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}; 