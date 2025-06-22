import React from 'react';
import { NavLink } from 'react-router-dom';
import { LogOut, ArrowLeftRight } from 'lucide-react';

export type NavItem = {
  icon: React.ReactNode;
  label: string;
  path: string;
};

export type SwitchItem = {
  label: string;
  onClick: () => void;
};

type ProfileSidebarProps = {
  navItems: NavItem[];
  switchItem: SwitchItem;
  onLogout: () => void;
};

const ProfileSidebar: React.FC<ProfileSidebarProps> = ({ navItems, switchItem, onLogout }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm h-full flex flex-col">
      <nav className="flex-grow">
        <ul>
          {navItems.map((item) => (
            <li key={item.label} className="mb-2">
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 font-medium hover:bg-blue-50 hover:text-blue-600 transition ${
                    isActive ? 'bg-blue-600 text-white' : ''
                  }`
                }
              >
                {item.icon}
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="border-t border-gray-200 pt-4 mt-4">
        <button
          onClick={switchItem.onClick}
          className="flex items-center gap-3 w-full text-sm text-gray-600 hover:text-gray-800 mb-4 px-4 py-2"
        >
          <ArrowLeftRight className="w-4 h-4" />
          <span>{switchItem.label}</span>
        </button>
        <button
          onClick={onLogout}
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
};

export default ProfileSidebar; 