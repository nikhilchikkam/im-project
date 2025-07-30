import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ProfilePageLayout from '../../layouts/ProfilePageLayout';
import ProfileSidebar from '../../features/profile/ProfileSidebar';
import type { NavItem, SwitchItem } from '../../features/profile/ProfileSidebar';
import InfoCard from '../../features/profile/InfoCard';
import { User, ShoppingCart, Heart, Settings, HelpCircle } from 'lucide-react';

const UserProfilePage = () => {
  const { user, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);

  // Redirect to login if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Your Profile</h2>
            <p className="text-gray-600 mb-6">You need to be logged in to view and manage your profile.</p>
            <div className="space-y-3">
              <Link to="/login">
                <button className="w-full bg-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-purple-700 transition-colors">
                  Log In
                </button>
              </Link>
              <Link to="/signup">
                <button className="w-full bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors">
                  Create Account
                </button>
              </Link>
            </div>
            <div className="mt-6 pt-6 border-t border-gray-200">
              <Link to="/" className="text-purple-600 hover:text-purple-700 text-sm font-medium">
                ← Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const userNavItems: NavItem[] = [
    { icon: <User />, label: 'User Profile', path: '/profile' },
    { icon: <ShoppingCart />, label: 'Manage Cart', path: '/cart' },
    { icon: <Heart />, label: 'Manage Wishlist', path: '/wishlist' },
    { icon: <Settings />, label: 'Settings', path: '/profile/settings' },
    { icon: <HelpCircle />, label: 'Help/Report', path: '/profile/help' },
  ];

  const switchItem: SwitchItem = {
    label: 'Switch to Admin',
    onClick: () => console.log('Switching to Admin...'),
  };

  const sidebar = (
    <ProfileSidebar
      navItems={userNavItems}
      switchItem={switchItem}
      onLogout={logout}
    />
  );

  return (
    <ProfilePageLayout sidebar={sidebar}>
      <div className="space-y-8">
        <InfoCard title="User Profile" onSave={() => {}}>
            <div className="flex items-center gap-6">
                <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center">
                    <User className="w-12 h-12 text-gray-400" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold">
                        {user.first_name && user.last_name 
                          ? `${user.first_name} ${user.last_name}`
                          : user.email
                        }
                    </h2>
                    <p className="text-gray-500">
                        {user.company_name || 'Individual Account'}
                    </p>
                    <p className="text-sm text-gray-400 mt-1">
                        {user.is_verified ? '✓ Verified Account' : '⚠ Unverified Account'}
                    </p>
                </div>
            </div>
        </InfoCard>

        <InfoCard title="Personal Information" onSave={() => {}}>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField 
              label="First Name" 
              id="first-name" 
              value={user.first_name || ''} 
              disabled={!isEditing} 
            />
            <InputField 
              label="Last Name" 
              id="last-name" 
              value={user.last_name || ''} 
              disabled={!isEditing} 
            />
            <InputField 
              label="Email Address" 
              id="email" 
              type="email" 
              value={user.email} 
              disabled={true} 
            />
            <InputField 
              label="Phone" 
              id="phone" 
              type="tel" 
              value={user.phone || ''} 
              disabled={!isEditing} 
              colSpan={2} 
            />
            <InputField 
              label="Business ID" 
              id="business-id" 
              value={user.business_id || ''} 
              disabled={!isEditing} 
              colSpan={2} 
            />
          </form>
        </InfoCard>

        {user.company_name && (
          <InfoCard title="Company Information" onSave={() => {}}>
            <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField 
                label="Company Name" 
                id="company-name" 
                value={user.company_name} 
                disabled={true} 
                colSpan={2}
              />
            </form>
          </InfoCard>
        )}

        <InfoCard title="Account Information" onSave={() => {}}>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField 
              label="Account Type" 
              id="account-type" 
              value={user.company_name ? 'Company Account' : 'Individual Account'} 
              disabled={true} 
            />
            <InputField 
              label="Authentication Provider" 
              id="auth-provider" 
              value={user.auth_provider} 
              disabled={true} 
            />
            <InputField 
              label="Account Status" 
              id="account-status" 
              value={user.is_verified ? 'Verified' : 'Unverified'} 
              disabled={true} 
            />
            <InputField 
              label="Member Since" 
              id="created-at" 
              value={new Date(user.created_at).toLocaleDateString()} 
              disabled={true} 
            />
          </form>
        </InfoCard>
      </div>
    </ProfilePageLayout>
  );
};

// Helper component for form fields
const InputField = ({ label, id, type = 'text', value = '', disabled, colSpan = 1 }: { label: string; id: string; type?: string; value?: string; disabled: boolean; colSpan?: number }) => (
    <div className={`col-span-${colSpan}`}>
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
            {label}
        </label>
        <input
            type={type}
            id={id}
            value={value}
            disabled={disabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500"
        />
    </div>
);

export default UserProfilePage; 