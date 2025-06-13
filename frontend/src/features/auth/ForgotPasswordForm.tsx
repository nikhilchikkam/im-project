import { useState } from 'react';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';


export const ForgotPasswordForm = () => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes('@')) return;
    setSent(true);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Forgot Password</h2>

      {!sent ? (
        <>
          <Input
            label="Email"
            type="email"
            value={email}
            placeholder="Enter Email"
            onChange={(e) => setEmail(e.target.value)}
          />
          <Button type="submit" className="w-full">
            Get Link
          </Button>
        </>
      ) : (
        <p className="text-green-600 text-center">Password reset link sent to inbox.</p>
      )}

      <div className="text-sm text-center">
        New User? <span className="text-blue-600 hover:underline cursor-pointer">SignUp</span>
      </div>
    </form>
  );
};
