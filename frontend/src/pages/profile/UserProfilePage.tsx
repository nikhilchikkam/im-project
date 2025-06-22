import React, { useState } from 'react';
import ProfilePageLayout from '../../layouts/ProfilePageLayout';
import ProfileSidebar from '../../features/profile/ProfileSidebar';
import type { NavItem, SwitchItem } from '../../features/profile/ProfileSidebar';
import InfoCard from '../../features/profile/InfoCard';
import { User, ShoppingCart, Heart, Settings, HelpCircle } from 'lucide-react';

const UserProfilePage = () => {
  const [isEditing, setIsEditing] = useState(false);

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
      onLogout={() => console.log('Logging out...')}
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
                    <h2 className="text-2xl font-bold">User Name</h2>
                    <p className="text-gray-500">Company Name</p>
                </div>
            </div>
        </InfoCard>

        <InfoCard title="Personal Information" onSave={() => {}}>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField label="First Name" id="first-name" disabled={!isEditing} />
            <InputField label="Last Name" id="last-name" disabled={!isEditing} />
            <InputField label="Email Address" id="email" type="email" disabled={!isEditing} />
            <InputField label="Password" id="password" type="password" disabled={!isEditing} />
            <InputField label="Phone" id="phone" type="tel" disabled={!isEditing} colSpan={2} />
          </form>
        </InfoCard>

        <InfoCard title="Address" onSave={() => {}}>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField label="Address Line" id="address1" disabled={!isEditing} />
            <InputField label="Address Line 2" id="address2" disabled={!isEditing} />
            <InputField label="State" id="state" disabled={!isEditing} />
            <InputField label="Country" id="country" disabled={!isEditing} />
            <InputField label="Zip" id="zip" disabled={!isEditing} />
          </form>
        </InfoCard>
      </div>
    </ProfilePageLayout>
  );
};

// Helper component for form fields
const InputField = ({ label, id, type = 'text', disabled, colSpan = 1 }: { label: string; id: string; type?: string; disabled: boolean; colSpan?: number }) => (
    <div className={`col-span-${colSpan}`}>
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
            {label}
        </label>
        <input
            type={type}
            id={id}
            disabled={disabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500"
        />
    </div>
);

export default UserProfilePage; 