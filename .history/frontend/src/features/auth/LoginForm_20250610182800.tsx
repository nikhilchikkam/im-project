import { useState } from 'react';
import { Input } from './Input';
import { Button } from './Button';

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

      <div className="flex justify-end text-sm text-blue-600 cursor-pointer hover:underline">
        Forgot password
      </div>

      <Button type="submit" className="w-full">
        Login
      </Button>

      <div className="text-sm text-center">
        New User? <span className="text-blue-600 hover:underline cursor-pointer">SignUp</span>
      </div>
    </form>
  );
};
