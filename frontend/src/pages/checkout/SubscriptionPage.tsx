import React, { useState } from 'react';
import { Check, Zap } from 'lucide-react';
import NavbarBefore from '../../components/navigation/NavbarBefore';

const SubscriptionPage: React.FC = () => {
  const [membershipType, setMembershipType] = useState('annually');
  const [paymentMethod, setPaymentMethod] = useState('card');

  const inputClasses = "w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500";

  return (
    <div className="min-h-screen bg-white">
      <NavbarBefore />
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-2 gap-16">
          {/* Left Column: Form */}
          <div className="space-y-8">
            {/* Personal Details */}
            <div>
              <div className="bg-blue-600 text-white p-4 rounded-t-lg">
                <h2 className="text-lg font-semibold">1. Personal Details</h2>
              </div>
              <div className="border border-t-0 border-gray-200 p-6 rounded-b-lg">
                <p className="text-sm text-gray-500 mb-4">Billed to</p>
                <form className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                      <input type="text" placeholder="First Name" className={inputClasses} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                      <input type="text" placeholder="Last Name" className={inputClasses} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Billing Address</label>
                    <input type="text" placeholder="Billing Address" className={inputClasses} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input type="email" placeholder="Email" className={inputClasses} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                      <input type="tel" placeholder="Phone Number" className={inputClasses} />
                    </div>
                  </div>
                </form>
              </div>
            </div>

            {/* Payment Method */}
            <div>
              <div className="bg-blue-600 text-white p-4 rounded-t-lg">
                <h2 className="text-lg font-semibold">2. Payment</h2>
              </div>
              <div className="border border-t-0 border-gray-200 p-6 rounded-b-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Payment Method</h3>
                <p className="text-sm text-gray-500 mb-4">Add a new payment method to your account.</p>
                <div className="flex gap-4">
                  <button 
                    onClick={() => setPaymentMethod('card')}
                    className={`p-4 rounded-lg border-2 flex items-center justify-start w-36 ${paymentMethod === 'card' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'}`}
                  >
                    <input type="radio" name="paymentMethod" checked={paymentMethod === 'card'} readOnly className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500" />
                    <div className="ml-3 flex items-center gap-2">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/a/ac/Old_Visa_Logo.svg" alt="Visa" className="h-4" />
                        <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard" className="h-4" />
                    </div>
                  </button>
                  <button 
                    onClick={() => setPaymentMethod('paypal')}
                    className={`p-4 rounded-lg border-2 flex items-center justify-start w-36 ${paymentMethod === 'paypal' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'}`}
                  >
                    <input type="radio" name="paymentMethod" checked={paymentMethod === 'paypal'} readOnly className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500" />
                    <div className="ml-3">
                        <img src="https://www.paypalobjects.com/webstatic/mktg/Logo/pp-logo-100px.png" alt="PayPal" className="h-5" />
                    </div>
                  </button>
                </div>

                {paymentMethod === 'card' && (
                  <div className="mt-6 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Name on card</label>
                      <input type="text" className={inputClasses} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Card Number</label>
                      <div className="relative">
                        <input type="text" className={inputClasses} />
                         <div className="absolute right-3 top-1/2 -translate-y-1/2 flex gap-1">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard" className="h-4" />
                            <img src="https://upload.wikimedia.org/wikipedia/commons/a/ac/Old_Visa_Logo.svg" alt="Visa" className="h-4" />
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">MM / YY</label>
                        <input type="text" placeholder="MM / YY" className={inputClasses} />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">CVV</label>
                        <input type="text" placeholder="CVV" className={inputClasses} />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                      <div className="relative">
                        <select className={inputClasses + " appearance-none"}>
                          <option>United States</option>
                          <option>Canada</option>
                          <option>United Kingdom</option>
                        </select>
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">🇺🇸</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Zip Code</label>
                      <input type="text" className={inputClasses} />
                    </div>
                    <p className="text-xs text-gray-500 pt-2">
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                    </p>
                  </div>
                )}

                {paymentMethod === 'paypal' && (
                    <div className="mt-6">
                        <label className="flex items-center gap-3 text-gray-700">
                            <input type="checkbox" className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                            <span className="text-sm">Remember my Paypal account details</span>
                        </label>
                    </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Subscription Summary */}
          <div className="border-2 border-blue-500 rounded-lg p-8 h-fit">
            <h3 className="text-2xl font-bold text-gray-800 mb-2">Enterprise subscription</h3>
            <p className="text-sm text-gray-500">Get all access and an extra 25% off when you subscribe annually</p>
            <p className="text-sm text-gray-700 font-semibold mt-2 mb-4">Yearly subscription <span className="text-gray-500 font-normal">Renews Jun 29, 2026</span></p>
            
            <ul className="space-y-3 mb-6">
              <li className="flex items-center gap-3"><Check className="w-5 h-5 text-green-500" /> Lorem ipsum dolor sit amet.</li>
              <li className="flex items-center gap-3"><Check className="w-5 h-5 text-green-500" /> Lorem ipsum dolor sit amet.</li>
              <li className="flex items-center gap-3"><Check className="w-5 h-5 text-green-500" /> Lorem ipsum dolor sit amet.</li>
              <li className="flex items-center gap-3"><Check className="w-5 h-5 text-green-500" /> Lorem ipsum dolor sit amet.</li>
            </ul>

            <div className="border-t border-gray-200 pt-4 space-y-2">
              <div className="flex justify-between items-center text-gray-600">
                <span>Yearly subscription</span>
                <span className="font-semibold text-gray-800">$1099.99</span>
              </div>
               <div className="flex justify-between items-center text-lg font-bold text-gray-800">
                <span>Total Due today (USD)</span>
                <span>$1099.99</span>
              </div>
            </div>

            <div className="mt-8">
              <h4 className="font-semibold text-gray-700 mb-3">Membership Type</h4>
              <div className="space-y-4">
                 <div onClick={() => setMembershipType('monthly')} className={`p-4 rounded-lg border cursor-pointer ${membershipType === 'monthly' ? 'border-blue-600' : 'border-gray-300'}`}>
                    <div className="flex items-center">
                        <input type="radio" name="membership" checked={membershipType === 'monthly'} className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500" readOnly />
                        <div className="ml-3">
                            <p className="font-semibold">Pay Monthly</p>
                            <p className="text-sm text-gray-500">$34.99 / Month Per Member</p>
                        </div>
                    </div>
                 </div>
                 <div onClick={() => setMembershipType('annually')} className={`p-4 rounded-lg border cursor-pointer ${membershipType === 'annually' ? 'border-blue-600' : 'border-gray-300'}`}>
                    <div className="flex items-center justify-between">
                         <div className="flex items-center">
                            <input type="radio" name="membership" checked={membershipType === 'annually'} className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500" readOnly />
                            <div className="ml-3">
                                <p className="font-semibold">Pay Annually</p>
                                <p className="text-sm text-gray-500">$13.99 / Month Per Member</p>
                            </div>
                        </div>
                        <span className="text-sm font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded-full">Save 25%</span>
                    </div>
                 </div>
              </div>
            </div>
            
            <div className="mt-8 text-center">
              <p className="text-xs text-gray-500 mb-4">
                By Continuing you agree to our <a href="#" className="text-blue-600 underline">terms and conditions</a>.
              </p>
              <button className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2">
                <Zap className="w-5 h-5" />
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SubscriptionPage; 