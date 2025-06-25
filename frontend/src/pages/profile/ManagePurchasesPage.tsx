import React from 'react';
import { 
  User, 
  CreditCard,
  Settings,
  HelpCircle,
  Phone,
  ArrowLeftRight,
  LogOut,
  Pencil
} from 'lucide-react';
import ProfilePageLayout from '../../layouts/ProfilePageLayout';

// --- Reusable Sidebar ---
// Note: In a larger app, this sidebar could be extracted into its own shared component.
type NavItem = {
  icon: React.ReactNode;
  label: string;
  id: string;
  isActive?: boolean;
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
      isActive: true,
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

const CustomSidebar = () => (
    <div className="bg-white p-4 rounded-lg shadow-sm h-full flex flex-col">
      <nav className="flex-grow pt-4">
        <ul>
          {navItems.map((item) => (
            <li key={item.id} className="mb-2">
              <button
                className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition w-full text-left ${
                  item.isActive 
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

const ManagePurchasesPage: React.FC = () => {
  const sidebar = <CustomSidebar />;

  const billingHistory = [
    { invoice: '#003', plan: 'Individual plan', amount: '1095 USD', date: '1 December 2025' },
    { invoice: '#003', plan: 'Individual plan', amount: '1095 USD', date: '1 December 2025' },
    { invoice: '#003', plan: 'Individual plan', amount: '1095 USD', date: '1 December 2025' },
  ];

  return (
    <ProfilePageLayout sidebar={sidebar}>
      <div className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Current Plan Card */}
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

          {/* Saved Payment Card */}
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
    </ProfilePageLayout>
  );
};

export default ManagePurchasesPage; 