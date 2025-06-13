import { AuthLayout } from '../features/auth/AuthLayout';
import { LoginForm } from '../features/auth/LoginForm';

const LoginPage = () => (
  <AuthLayout>
    <LoginForm />
  </AuthLayout>
);

export default LoginPage;
