import { useState } from 'react';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Link } from 'react-router-dom';

export const MagicLinkForm = () => {
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
      const response = await fetch('/api/auth/magic-link', {
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

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Login with Magic Link</h2>
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
        {isLoading ? 'Sending...' : 'Send Magic Link'}
      </Button>

      <div className="flex items-center gap-4 my-4">
        <div className="flex-grow border-t border-gray-300" />
        <span className="text-sm text-gray-500">or</span>
        <div className="flex-grow border-t border-gray-300" />
      </div>

      <div className="space-y-2">
        <Link to="/login/google" className="block">
          <button type="button" className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50">
            <img src="/google-icon.png" alt="Google" className="w-5 h-5" />
            <span>Continue with Google</span>
          </button>
        </Link>
        <Link to="/login/apple" className="block">
          <button type="button" className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50">
            <img src="/apple-icon.png" alt="Apple" className="w-5 h-5" />
            <span>Continue with Apple</span>
          </button>
        </Link>
      </div>

      <div className="text-center text-sm mt-4">
        <Link to="/signup" className="text-blue-600 hover:underline">
          New User? Sign Up
        </Link>
      </div>
    </form>
  );
}; 