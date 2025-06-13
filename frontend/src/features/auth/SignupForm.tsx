import { useState } from 'react';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Link } from 'react-router-dom';

export const SignupForm = () => {
  // Form state
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    companyName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    businessId: '',
  });
  const [errors, setErrors] = useState<any>({});
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState<'individual' | 'company'>('company');
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'verify' | 'code' | 'error'>('idle');
  const [globalError, setGlobalError] = useState('');

  // Helper for field change
  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev: any) => ({ ...prev, [field]: '' }));
    setGlobalError('');
  };

  // Validation logic
  const validate = () => {
    const newErrors: any = {};
    if (step === 'company') {
      if (!form.companyName) newErrors.companyName = 'Company name is required.';
      if (!form.email) newErrors.email = 'Email is required.';
      else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) newErrors.email = 'Invalid Email';
      if (!form.phone) newErrors.phone = 'Phone number is required.';
      if (!form.businessId) newErrors.businessId = 'Business Reg Number/Tax ID/SSN is required.';
    } else {
      if (!form.firstName) newErrors.firstName = 'First name is required.';
      if (!form.lastName) newErrors.lastName = 'Last name is required.';
      if (!form.email) newErrors.email = 'Email is required.';
      else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) newErrors.email = 'Invalid Email';
      if (!form.password) newErrors.password = 'Password is required.';
      else if (form.password.length < 8) newErrors.password = 'Password must contain atleast 8 characters';
      if (form.password !== form.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
      if (!form.businessId) newErrors.businessId = 'Business Reg Number/Tax ID/SSN is required.';
    }
    return newErrors;
  };

  // Simulate backend responses for demo
  const simulateBackend = () => {
    // Demo error states
    if (form.email === 'joe@gmail.com') {
      setGlobalError('This email already exists. Login');
      setErrors((prev: any) => ({ ...prev, email: 'This email already exists' }));
      return false;
    }
    if (form.companyName === 'Machine') {
      setGlobalError('Our records show that this company is already registered with us. Login?');
      setErrors((prev: any) => ({ ...prev, companyName: 'An account under this company name already exists.' }));
      return false;
    }
    if (form.phone === '5854839834') {
      setGlobalError('This Phone number is associated with an existing account. Login?');
      setErrors((prev: any) => ({ ...prev, phone: 'This phone number is already associated with an account.' }));
      return false;
    }
    if (form.businessId === '12DFRT555') {
      setGlobalError('Invalid Business Reg Number/Tax ID/ SSN.');
      setErrors((prev: any) => ({ ...prev, businessId: 'Invalid Business Reg Number/Tax ID/ SSN.' }));
      return false;
    }
    return true;
  };

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setGlobalError('');
    setSuccess('');
    setStatus('idle');
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    if (!simulateBackend()) {
      setStatus('error');
      return;
    }
    // Simulate success
    if (step === 'company') {
      setStatus('success');
      setSuccess('Account set up request submission successful. You will receive login credentials to your registered Email Id after your account is set up.');
    } else {
      setStatus('verify');
      setSuccess('Verification link sent to Inbox. Click on the link to verify your account');
    }
  };

  // For code verification step (individual)
  const handleCodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('success');
    setSuccess('Account set up request submission successful. You will receive login credentials to your registered Email Id after your account is set up.');
  };

  // UI rendering
  if (status === 'success') {
    return (
      <div className="text-center space-y-6">
        <h2 className="text-2xl font-bold">Create an Account</h2>
        <p className="text-green-600">{success}</p>
        <Link to="/login">
          <Button className="mt-6 w-60">Login</Button>
        </Link>
      </div>
    );
  }
  if (status === 'verify') {
    return (
      <div className="text-center space-y-6">
        <h2 className="text-2xl font-bold">Create an Account</h2>
        <p className="text-green-600">{success}</p>
        <form onSubmit={handleCodeSubmit} className="space-y-4">
          <div className="bg-blue-50 p-6 rounded-lg inline-block">
            <div className="mb-2 font-semibold">Verification</div>
            <div className="mb-2 text-sm">We have sent a code to <span className="font-medium">{form.email}</span>. Enter it below.</div>
            <div className="flex gap-2 justify-center mb-4">
              {[1,2,3,4,5,6].map((n) => (
                <input key={n} className="w-10 h-10 border rounded text-center" maxLength={1} />
              ))}
            </div>
            <Button type="submit" className="w-full">Login</Button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Create an Account</h2>
      {globalError && <div className="text-red-600 text-center text-sm font-medium mb-2">{globalError}</div>}
      {step === 'company' ? (
        <>
          <Input
            label="Company Name"
            value={form.companyName}
            placeholder="Company Name"
            onChange={e => handleChange('companyName', e.target.value)}
            error={errors.companyName}
          />
          <Input
            label="Email"
            type="email"
            value={form.email}
            placeholder="Enter Email"
            onChange={e => handleChange('email', e.target.value)}
            error={errors.email}
          />
          <Input
            label="Phone Number"
            value={form.phone}
            placeholder="Phone Number"
            onChange={e => handleChange('phone', e.target.value)}
            error={errors.phone}
          />
          <Input
            label="Business Reg Number/Tax ID/SSN"
            value={form.businessId}
            placeholder="Business Reg Number/Tax ID/SSN"
            onChange={e => handleChange('businessId', e.target.value)}
            error={errors.businessId}
          />
          <div className="text-xs text-blue-700 underline cursor-pointer mb-2">Why do we ask this?</div>
          <Button type="submit" className="w-full">Request Account setup</Button>
        </>
      ) : (
        <>
          <Input
            label="First Name"
            value={form.firstName}
            placeholder="First Name"
            onChange={e => handleChange('firstName', e.target.value)}
            error={errors.firstName}
          />
          <Input
            label="Last Name"
            value={form.lastName}
            placeholder="Last Name"
            onChange={e => handleChange('lastName', e.target.value)}
            error={errors.lastName}
          />
          <Input
            label="Email"
            type="email"
            value={form.email}
            placeholder="Enter Email"
            onChange={e => handleChange('email', e.target.value)}
            error={errors.email}
          />
          <Input
            label="Password"
            type="password"
            value={form.password}
            placeholder="Password"
            onChange={e => handleChange('password', e.target.value)}
            error={errors.password}
          />
          <Input
            label="Re-enter Password"
            type="password"
            value={form.confirmPassword}
            placeholder="Re-enter Password"
            onChange={e => handleChange('confirmPassword', e.target.value)}
            error={errors.confirmPassword}
          />
          <Input
            label="Business Reg Number/Tax ID/SSN"
            value={form.businessId}
            placeholder="Business Reg Number/Tax ID/SSN"
            onChange={e => handleChange('businessId', e.target.value)}
            error={errors.businessId}
          />
          <div className="text-xs text-blue-700 underline cursor-pointer mb-2">Why do we ask this?</div>
          <Button type="submit" className="w-full">Signup</Button>
        </>
      )}
      <div className="flex items-center gap-4 my-4">
        <div className="flex-grow border-t border-gray-300" />
        <span className="text-sm text-gray-500">or</span>
        <div className="flex-grow border-t border-gray-300" />
      </div>
      <div className="space-y-2">
        <button type="button" className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50">
          <img src="google-icon.png" alt="Google" className="w-5 h-5" />
          <span>Continue with Google</span>
        </button>
        <button type="button" className="w-full border border-gray-300 rounded-full py-2 hover:bg-gray-50">
          Continue with Single Sign On
        </button>
        <button type="button" className="w-full border border-gray-300 rounded-full py-2 flex items-center justify-center gap-2 hover:bg-gray-50">
          <img src="apple-icon.png" alt="Apple" className="w-5 h-5" />
          <span>Continue with Apple</span>
        </button>
      </div>
      <div className="text-center text-sm mt-4">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-600 hover:underline cursor-pointer">Login</Link>
      </div>
      <div className="text-center text-xs mt-2">
        <button type="button" className="underline text-blue-700" onClick={() => setStep(step === 'company' ? 'individual' : 'company')}>
          {step === 'company' ? 'Sign up as an individual' : 'Sign up as a company'}
        </button>
      </div>
    </form>
  );
}; 