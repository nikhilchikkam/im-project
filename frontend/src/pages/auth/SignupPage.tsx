import { AuthLayout } from '../../features/auth/AuthLayout';
import { SignupForm } from '../../features/auth/SignupForm';

const SignupPage = () => (
  <AuthLayout>
    {/*
<button
  type="button"
  onClick={handleGoogleSignup}
  className="w-full flex items-center justify-center gap-2 border border-gray-300 rounded-md py-2 px-4 text-gray-700 hover:bg-gray-50 transition"
>
  <img src={googleIcon} alt="Google" className="w-5 h-5" />
  Continue with Google
</button>
<button
  type="button"
  onClick={handleAppleSignup}
  className="w-full flex items-center justify-center gap-2 border border-gray-300 rounded-md py-2 px-4 text-gray-700 hover:bg-gray-50 transition"
>
  <img src={appleIcon} alt="Apple" className="w-5 h-5" />
  Continue with Apple
</button>
*/}
    <SignupForm />
  </AuthLayout>
);

export default SignupPage; 