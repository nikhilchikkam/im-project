import { useState } from 'react';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Link } from 'react-router-dom';

export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email || !password) {
      setError('Fields cannot be empty.');
      return;
    }

    if (!email.includes('@')) {
      setError('Invalid email format.');
      return;
    }

    // Simulate success
    setSuccess('Login successful!');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Login</h2>
      {error && <p className="text-red-600 text-sm text-center">{error}</p>}
      {success && <p className="text-green-600 text-sm text-center">{success}</p>}

      <Input
        label="Email"
        type="email"
        value={email}
        placeholder="Enter Email"
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        label="Password"
        type="password"
        value={password}
        placeholder="Enter Password"
        onChange={(e) => setPassword(e.target.value)}
      />

      <Link to="/forgot-password" className="text-blue-600 hover:underline">
        Forgot password?
      </Link>

      <Button type="submit" className="w-full">
        Login
      </Button>

      <Link to="/signup" className="text-blue-600 hover:underline">
        New User? <span className="text-blue-600 hover:underline cursor-pointer">SignUp</span>
      </Link>

      <div className="flex items-center gap-4 my-4">
        <div className="flex-grow border-t border-gray-300" />
        <span className="text-sm text-gray-500">or</span>
        <div className="flex-grow border-t border-gray-300" />
      </div>

      <div className="space-y-2">
        <button className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50">
          <img src="google-icon.png" alt="Google" className="w-5 h-5" />
          <span>Continue with Google</span>
        </button>
        <button className="w-full border border-gray-300 rounded-full py-2 hover:bg-gray-50">
          Continue with Single Sign On
        </button>
        <button className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50">
          <img src="apple-icon.png" alt="Apple" className="w-5 h-5" />
          <span>Continue with Apple</span>
        </button>
      </div>

    </form>
  );
};
