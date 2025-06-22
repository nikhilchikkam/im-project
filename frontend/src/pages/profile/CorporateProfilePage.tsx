import React, { useState } from 'react';
import { 
  User, 
  Users, 
  CreditCard,
  Settings,
  HelpCircle,
  Phone,
  ArrowLeftRight,
  LogOut,
  Pencil,
  UserCircle,
  Search,
  ArrowRight
} from 'lucide-react';
import ProfilePageLayout from '../../layouts/ProfilePageLayout';
import InfoCard from '../../features/profile/InfoCard';
import { Input } from '../../components/ui/Input';
import DeleteConfirmationModal from '../../components/modals/DeleteConfirmationModal';
import UserDetailsModal from '../../components/modals/UserDetailsModal';
import type { UserData } from '../../components/modals/UserDetailsModal';

type NavItem = {
  icon: React.ReactNode;
  label: string;
  id: string;
};

const CorporateProfilePage: React.FC = () => {
  const [activeView, setActiveView] = useState('corporate-profile');

  // State for Corporate Info form
  const [corporateInfo, setCorporateInfo] = useState({
    companyName: '',
    email: '',
    password: '',
    phone: '',
    taxId: '',
  });

  // State for Address form
  const [address, setAddress] = useState({
    addressLine1: '',
    addressLine2: '',
    state: '',
    country: '',
    zip: '',
  });

  const [isDeleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [isUserDetailsModalOpen, setUserDetailsModalOpen] = useState(false);

  const handleCorporateInfoChange = (field: string, value: string) => {
    setCorporateInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleAddressChange = (field: string, value: string) => {
    setAddress(prev => ({ ...prev, [field]: value }));
  };
  
  const navItems: NavItem[] = [
    {
      icon: <User className="w-5 h-5" />,
      label: 'Corporate Profile',
      id: 'corporate-profile',
    },
    {
      icon: <CreditCard className="w-5 h-5" />,
      label: 'Manage Purchases',
      id: 'manage-purchases',
    },
    {
      icon: <Users className="w-5 h-5" />,
      label: 'Manage Users',
      id: 'manage-users',
    },
    {
      icon: <Settings className="w-5 h-5" />,
      label: 'Settings',
      id: 'settings',
    },
    {
      icon: <HelpCircle className="w-5 h-5" />,
      label: 'Help/Report',
      id: 'help-report',
    },
    {
      icon: <Phone className="w-5 h-5" />,
      label: 'Contact Mendon',
      id: 'contact-mendon',
    },
  ];

  const handleSwitchToUser = () => {
    console.log('Switching to user profile');
  };

  const handleLogout = () => {
    console.log('Logging out');
  };

  const handleSave = (section: string) => (data: any) => {
    console.log(`Saving ${section}:`, data);
  };

  const handleDeleteConfirm = () => {
    // Add actual delete logic here
    console.log("Deleting users...");
    setDeleteModalOpen(false);
  }

  const handleViewDetails = (user: UserData) => {
    setSelectedUser(user);
    setUserDetailsModalOpen(true);
  };

  const CustomSidebar = () => (
    <div className="bg-white p-4 rounded-lg shadow-sm h-full flex flex-col">
      <nav className="flex-grow pt-4">
        <ul>
          {navItems.map((item) => (
            <li key={item.id} className="mb-2">
              <button
                onClick={() => setActiveView(item.id)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition w-full text-left ${
                  activeView === item.id 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
      <div className="border-t border-gray-200 pt-4 mt-4">
        <button
          onClick={handleSwitchToUser}
          className="flex items-center gap-3 w-full text-sm text-gray-600 hover:text-gray-800 mb-4 px-4 py-2"
        >
          <ArrowLeftRight className="w-4 h-4" />
          <span>Switch to User</span>
        </button>
        <button
          onClick={handleLogout}
          className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 hover:bg-blue-700 transition"
        >
          <LogOut className="w-5 h-5" />
          <span>Log out</span>
        </button>
        <p className="text-xs text-gray-400 text-center mt-4">
          Nutrition management
        </p>
      </div>
    </div>
  );

  const ProfileSummaryCard = () => (
    <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Corporate Profile</h2>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <UserCircle className="w-16 h-16 text-gray-300" />
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Company Name</h3>
            <p className="text-gray-500">Company Domain</p>
          </div>
        </div>
        <button
          onClick={() => { /* Placeholder for edit action */ }}
          className="bg-gray-100 text-gray-600 font-semibold px-6 py-2 rounded-lg hover:bg-gray-200 transition text-sm flex items-center gap-2"
        >
          <Pencil className="w-3 h-3" />
          <span>Edit</span>
        </button>
      </div>
    </div>
  );

  const renderCorporateProfile = () => (
    <div className="space-y-8">
      <ProfileSummaryCard />
      <InfoCard title="Corporate Information" onSave={handleSave('corporateInfo')}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input label="Company Name" placeholder="Company Name" value={corporateInfo.companyName} onChange={(e) => handleCorporateInfoChange('companyName', e.target.value)} />
            <Input label="Email Address" placeholder="Email Address" type="email" value={corporateInfo.email} onChange={(e) => handleCorporateInfoChange('email', e.target.value)} />
            <Input label="Phone" placeholder="Phone" type="tel" value={corporateInfo.phone} onChange={(e) => handleCorporateInfoChange('phone', e.target.value)} />
            <Input label="Password" placeholder="Password" type="password" value={corporateInfo.password} onChange={(e) => handleCorporateInfoChange('password', e.target.value)} />
            <Input label="Tax ID" placeholder="Tax ID" value={corporateInfo.taxId} onChange={(e) => handleCorporateInfoChange('taxId', e.target.value)} />
        </div>
      </InfoCard>
      <InfoCard title="Address" onSave={handleSave('address')}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input label="Address Line" placeholder="Address Line" value={address.addressLine1} onChange={(e) => handleAddressChange('addressLine1', e.target.value)} />
            <Input label="Address Line 2" placeholder="Address Line 2" value={address.addressLine2} onChange={(e) => handleAddressChange('addressLine2', e.target.value)} />
            <Input label="State" placeholder="State" value={address.state} onChange={(e) => handleAddressChange('state', e.target.value)} />
            <Input label="Country" placeholder="Country" value={address.country} onChange={(e) => handleAddressChange('country', e.target.value)} />
            <div className="md:col-span-2">
                <Input label="Zip" placeholder="Zip" value={address.zip} onChange={(e) => handleAddressChange('zip', e.target.value)} />
            </div>
        </div>
      </InfoCard>
    </div>
  );

  const renderManagePurchases = () => {
    const billingHistory = [
        { invoice: '#003', plan: 'Individual plan', amount: '1095 USD', date: '1 December 2025' },
        { invoice: '#003', plan: 'Individual plan', amount: '1095 USD', date: '1 December 2025' },
        { invoice: '#003', plan: 'Individual plan', amount: '1095 USD', date: '1 December 2025' },
    ];
    return (
        <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                <div className="lg:col-span-3 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <span className="bg-blue-100 text-blue-600 text-sm font-semibold px-3 py-1 rounded-full">Yearly</span>
                            <p className="text-sm text-gray-500 mt-2">Renews Jun 29, 2026</p>
                        </div>
                    </div>
                    <div className="mb-4">
                        <p className="text-sm text-gray-700 mb-1">1 out of 1 users</p>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div className="bg-black h-2 rounded-full" style={{ width: '100%' }}></div>
                        </div>
                    </div>
                    <div className="flex justify-end gap-4 mt-6">
                        <button className="text-gray-700 font-semibold px-6 py-2 rounded-lg border border-gray-300 hover:bg-gray-100">Cancel</button>
                        <button className="bg-blue-600 text-white font-semibold px-6 py-2 rounded-lg hover:bg-blue-700">Change Plan</button>
                    </div>
                </div>
                <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm">
                    <h3 className="text-lg font-semibold text-gray-800">Saved Payment</h3>
                    <p className="text-sm text-gray-500 mb-4">You can edit your cards here</p>
                    <div className="flex justify-between items-center border border-gray-200 p-4 rounded-lg">
                        <div className="flex items-center gap-4">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/Visa_Inc._logo.svg" alt="Visa" className="h-4"/>
                            <div>
                                <p className="font-semibold text-sm">Visa ending in 1234</p>
                                <p className="text-xs text-gray-500">Expiry 09/2023</p>
                            </div>
                        </div>
                        <button className="p-2 rounded-full bg-gray-100 hover:bg-gray-200">
                            <Pencil className="w-4 h-4 text-gray-600"/>
                        </button>
                    </div>
                </div>
            </div>
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Billing history</h2>
                <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="p-4 text-sm font-semibold text-gray-600 uppercase">Invoice</th>
                                <th className="p-4 text-sm font-semibold text-gray-600 uppercase">Amount</th>
                                <th className="p-4 text-sm font-semibold text-gray-600 uppercase">Date</th>
                                <th className="p-4"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {billingHistory.map((item, index) => (
                                <tr key={index} className="border-t border-gray-200">
                                    <td className="p-4">
                                        <p className="font-semibold text-gray-800">{item.invoice}</p>
                                        <p className="text-sm text-gray-500">{item.plan}</p>
                                    </td>
                                    <td className="p-4 font-semibold text-gray-800">{item.amount}</td>
                                    <td className="p-4 text-gray-600">{item.date}</td>
                                    <td className="p-4 text-right">
                                        <a href="#" className="font-semibold text-blue-600 hover:underline flex items-center justify-end gap-2">
                                            View invoice <span aria-hidden="true">&rarr;</span>
                                        </a>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
  }

  const renderManageUsers = () => {
    const users: UserData[] = [
      { 
        id: 'WED23456', name: 'John Doe', email: 'johndoe@gmail.com', role: 'Manager', 
        avatar: 'https://randomuser.me/api/portraits/men/68.jpg',
        division: 'East division', joinedDate: '3 June 2024', phone: '5854819934',
        address: { line1: '300 Jay Rd', city: 'Rochester', state: 'NY', zip: '14623' },
        accessLevel: 'manager'
      },
      { 
        id: 'WED45678', name: 'Jane Doe', email: 'janedoe@gmail.com', role: 'Supervisor', 
        avatar: 'https://randomuser.me/api/portraits/women/69.jpg',
        division: 'West division', joinedDate: '15 May 2023', phone: '5551234567',
        address: { line1: '123 Main St', city: 'Someplace', state: 'CA', zip: '90210' },
        accessLevel: 'employee'
      },
      { 
        id: 'WED34526', name: 'Peter Jones', email: 'peterjones@gmail.com', role: 'Chef', 
        avatar: 'https://randomuser.me/api/portraits/men/70.jpg',
        division: 'North division', joinedDate: '1 Jan 2022', phone: '9876543210',
        address: { line1: '456 Side Ave', city: 'Anytown', state: 'TX', zip: '75001' },
        accessLevel: 'employee'
      },
    ];

    return (
      <div className="bg-white p-8 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Team Users</h2>
          <button 
            onClick={() => setDeleteModalOpen(true)}
            className="text-red-600 font-semibold px-6 py-2 rounded-lg border border-red-300 hover:bg-red-50"
          >
            Delete
          </button>
        </div>
        <div className="relative mb-6">
          <input
            type="text"
            placeholder="Search User"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <ArrowRight className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-50 border-y border-gray-200">
              <tr>
                <th className="p-4 w-12"><input type="checkbox" className="rounded" /></th>
                <th className="p-4 text-sm font-semibold text-gray-600 uppercase">Employee ID</th>
                <th className="p-4 text-sm font-semibold text-gray-600 uppercase">Employee Name</th>
                <th className="p-4 text-sm font-semibold text-gray-600 uppercase">Role</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-gray-200 hover:bg-blue-50">
                  <td className="p-4 w-12"><input type="checkbox" className="rounded" /></td>
                  <td className="p-4 text-gray-800 font-medium">{user.id}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full" />
                      <div>
                        <p className="font-semibold text-gray-800">{user.name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-gray-600">{user.role}</td>
                  <td className="p-4 text-right">
                    <button onClick={() => handleViewDetails(user)} className="font-semibold text-blue-600 hover:underline flex items-center justify-end gap-2">
                      View Details <span aria-hidden="true">&rarr;</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <UserDetailsModal 
          isOpen={isUserDetailsModalOpen}
          onClose={() => setUserDetailsModalOpen(false)}
          user={selectedUser}
        />
        <DeleteConfirmationModal 
            isOpen={isDeleteModalOpen}
            onClose={() => setDeleteModalOpen(false)}
            onConfirm={handleDeleteConfirm}
        />
      </div>
    );
  };

  const renderContent = () => {
    switch (activeView) {
      case 'corporate-profile':
        return renderCorporateProfile();
      case 'manage-purchases':
        return renderManagePurchases();
      case 'manage-users':
        return renderManageUsers();
      default:
        return renderCorporateProfile();
    }
  };

  const sidebar = <CustomSidebar />;

  return (
    <ProfilePageLayout sidebar={sidebar}>
      {renderContent()}
    </ProfilePageLayout>
  );
};

export default CorporateProfilePage; 