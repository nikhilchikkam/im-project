import React from 'react';
import { X, ChevronUp } from 'lucide-react';

// Define a type for the user data for type safety
export type UserData = {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar: string;
  division?: string;
  joinedDate?: string;
  phone?: string;
  address?: {
    line1: string;
    city: string;
    state: string;
    zip: string;
  };
  accessLevel?: 'manager' | 'employee' | 'admin';
};

type UserDetailsModalProps = {
  isOpen: boolean;
  onClose: () => void;
  user: UserData | null;
};

const UserDetailsModal: React.FC<UserDetailsModalProps> = ({ isOpen, onClose, user }) => {
  if (!isOpen || !user) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-start py-10 overflow-y-auto"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg shadow-xl w-full max-w-2xl relative"
        onClick={e => e.stopPropagation()}
      >
        <button 
          onClick={onClose} 
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          aria-label="Close modal"
        >
          <X size={24} />
        </button>
        
        <div className="p-8">
          <div className="flex items-center gap-4 mb-8">
            <img src={user.avatar} alt={user.name} className="w-16 h-16 rounded-full bg-green-100 p-1" />
            <div>
              <h3 className="text-xl font-bold text-gray-900 flex items-baseline">
                {user.name} 
                <span className="text-sm font-normal text-gray-500 ml-2">{user.division}</span>
              </h3>
              <p className="text-gray-600">{user.role}</p>
            </div>
          </div>
          
          <div className="space-y-6">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Employee Name</label>
                <input type="text" defaultValue={user.name.split(' ')[0]} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Divison/Team</label>
                <input type="text" defaultValue={user.division} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Joined on</label>
                <input type="text" defaultValue={user.joinedDate} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            {/* Contact Section */}
            <div>
                <h4 className="flex items-center gap-2 text-md font-semibold text-gray-800 mb-4 cursor-pointer">
                    <ChevronUp size={20} />
                    Contact
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone number</label>
                        <input type="text" defaultValue={user.phone} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"/>
                    </div>
                     <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input type="email" defaultValue={user.email} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"/>
                    </div>
                </div>
            </div>
            
            {/* Employee Address Section */}
             <div>
                <h4 className="flex items-center gap-2 text-md font-semibold text-gray-800 mb-4 cursor-pointer">
                    <ChevronUp size={20} />
                    Employee Address
                </h4>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
                    <input type="text" defaultValue={user.address?.line1} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"/>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                        <input type="text" defaultValue={user.address?.city} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"/>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                        <input type="text" defaultValue={user.address?.state} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"/>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Zip</label>
                        <input type="text" defaultValue={user.address?.zip} className="w-full p-2 border border-gray-200 bg-gray-50 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"/>
                    </div>
                </div>
            </div>

            {/* Manage Access Section */}
            <div>
                 <h4 className="text-md font-semibold text-gray-800 mb-4">Manage access</h4>
                 <div className="flex flex-wrap gap-x-8 gap-y-2">
                    <label className="flex items-center gap-2">
                        <input type="radio" name="accessLevel" value="manager" defaultChecked={user.accessLevel === 'manager'} className="form-radio h-4 w-4 text-blue-600" />
                        Manager
                    </label>
                     <label className="flex items-center gap-2">
                        <input type="radio" name="accessLevel" value="employee" defaultChecked={user.accessLevel === 'employee'} className="form-radio h-4 w-4 text-blue-600" />
                        Employee
                    </label>
                     <label className="flex items-center gap-2">
                        <input type="radio" name="accessLevel" value="admin" defaultChecked={user.accessLevel === 'admin'} className="form-radio h-4 w-4 text-blue-600" />
                        Admin
                    </label>
                 </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDetailsModal; 