import React from 'react';
import { Link } from 'react-router-dom';

interface LoginPromptProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  primaryColor: string;
  primaryColorHover: string;
  linkColor: string;
  linkColorHover: string;
}

const LoginPrompt: React.FC<LoginPromptProps> = ({
  title,
  description,
  icon,
  primaryColor,
  primaryColorHover,
  linkColor,
  linkColorHover
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className={`w-16 h-16 ${primaryColor} rounded-full flex items-center justify-center mx-auto mb-4`}>
            {icon}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600 mb-6">{description}</p>
          <div className="space-y-3">
            <Link to="/login">
              <button className={`w-full ${primaryColor} text-white font-semibold py-3 px-6 rounded-lg ${primaryColorHover} transition-colors`}>
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
            <Link to="/" className={`${linkColor} ${linkColorHover} text-sm font-medium`}>
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPrompt; 