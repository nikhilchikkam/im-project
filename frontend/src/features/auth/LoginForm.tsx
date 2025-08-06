import { useState } from 'react';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Link } from 'react-router-dom';

export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    if (!email) {
      setError('Email is required.');
      setIsLoading(false);
      return;
    }

    if (!email.includes('@')) {
      setError('Invalid email format.');
      setIsLoading(false);
      return;
    }

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/auth/magic-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Magic link sent! Check your email and click the link to log in.');
      } else {
        setError(data.detail || 'Failed to send magic link.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      
      console.log('Starting Google OAuth request...');
      console.log('Frontend VITE_API_URL:', apiUrl);
      
      // Use XMLHttpRequest to completely bypass any interceptors
      const xhr = new XMLHttpRequest();
      xhr.open('GET', `${apiUrl}/api/auth/google/url`, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      
      xhr.onload = function() {
        if (xhr.status === 200) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('Frontend received data:', data);
            console.log('URL before navigation:', data.url);
            console.log('URL type:', typeof data.url);
            console.log('URL length:', data.url.length);
            
            // Try using window.open instead of window.location.href
            const newWindow = window.open(data.url, '_self');
            if (!newWindow) {
              console.log('window.open failed, falling back to location.href');
              window.location.href = data.url;
            }
          } catch (err) {
            console.error('JSON parse error:', err);
            setError('Invalid response from server');
          }
        } else {
          console.error('XHR error:', xhr.status, xhr.responseText);
          setError('Failed to get Google OAuth URL');
        }
      };
      
      xhr.onerror = function() {
        console.error('XHR network error');
        setError('Network error. Please try again.');
      };
      
      xhr.send();
      
    } catch (err) {
      console.error('Google login error:', err);
      setError('Network error. Please try again.');
    }
  };

  // Comment out Apple login handler and imports if not used elsewhere
  // const handleAppleLogin = async () => {
  //   try {
  //     const apiUrl = import.meta.env.VITE_API_URL || '';
  //     const response = await fetch(`${apiUrl}/api/auth/apple/url`);
  //     const data = await response.json();
      
  //     if (response.ok) {
  //       // Redirect to Apple OAuth
  //       window.location.href = data.url;
  //     } else {
  //       setError('Failed to get Apple OAuth URL');
  //     }
  //   } catch (err) {
  //     setError('Network error. Please try again.');
  //   }
  // };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Login</h2>
      <p className="text-sm text-gray-600 text-center">
        Enter your email and we'll send you a secure login link
      </p>
      
      {error && <p className="text-red-600 text-sm text-center">{error}</p>}
      {success && <p className="text-green-600 text-sm text-center">{success}</p>}

      <Input
        label="Email"
        type="email"
        value={email}
        placeholder="Enter your email"
        onChange={(e) => setEmail(e.target.value)}
        disabled={isLoading}
      />

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? 'Sending...' : 'Send Login Link'}
      </Button>

      <div className="flex items-center gap-4 my-4">
        <div className="flex-grow border-t border-gray-300" />
        <span className="text-sm text-gray-500">or</span>
        <div className="flex-grow border-t border-gray-300" />
      </div>

      <div className="space-y-2">
        <button 
          type="button" 
          onClick={handleGoogleLogin}
          className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50"
        >
          <img src="/google-icon.png" alt="Google" className="w-5 h-5" />
          <span>Continue with Google</span>
        </button>
        {/*
        <button 
          type="button" 
          onClick={handleAppleLogin}
          className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50"
        >
          <img src="/apple-icon.png" alt="Apple" className="w-5 h-5" />
          <span>Continue with Apple</span>
        </button>
        */}
      </div>

      <div className="text-center text-sm mt-4">
        <Link to="/signup" className="text-blue-600 hover:underline">
          New User? <span className="text-blue-600 hover:underline cursor-pointer">Sign Up</span>
        </Link>
      </div>
    </form>
  );
};
