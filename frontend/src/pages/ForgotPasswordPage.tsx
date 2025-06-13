import { AuthLayout } from '../features/auth/AuthLayout';
import { ForgotPasswordForm } from '../features/auth/ForgotPasswordForm';

const LoginPage = () => (
  <AuthLayout>
    <ForgotPasswordForm />
  </AuthLayout>
);

export default LoginPage;
