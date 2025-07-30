import { useState } from 'react';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Link } from 'react-router-dom';

export const SignupForm = () => {
  // Form state
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    companyName: '',
    email: '',
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
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setGlobalError('');
    setSuccess('');
    setStatus('submitting');
    
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setStatus('idle');
      return;
    }

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      // Send signup request
      const response = await fetch(`${apiUrl}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: form.email,
          first_name: form.firstName,
          last_name: form.lastName,
          company_name: form.companyName,
          phone: form.phone,
          business_id: form.businessId
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('verify');
        setSuccess('Account created successfully! Magic link sent to your email to complete registration.');
      } else {
        setGlobalError(data.detail || 'Failed to create account. Please try again.');
        setStatus('error');
      }
    } catch (error) {
      setGlobalError('Network error. Please check your connection and try again.');
      setStatus('error');
    }
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
        <div className="bg-blue-50 p-6 rounded-lg inline-block max-w-md">
          <div className="mb-4 font-semibold">Check Your Email</div>
          <div className="mb-4 text-sm">
            We've sent a magic link to <span className="font-medium">{form.email}</span>.
            <br />
            Click the link in your email to complete your registration.
          </div>
          <div className="text-xs text-gray-600 mb-4">
            Didn't receive the email? Check your spam folder or try again.
          </div>
          <Button 
            onClick={() => setStatus('idle')} 
            className="w-full"
          >
            Try Again
          </Button>
        </div>
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