import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

type InputProps = {
  label: string;
  type?: string;
  placeholder?: string;
  error?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export const Input = ({ label, type = 'text', placeholder, error, value, onChange }: InputProps) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';

  return (
    <div className="flex flex-col space-y-1">
      <label className="text-sm font-medium text-[#333]">{label}</label>
      <div className="relative">
        <input
          type={isPassword ? (showPassword ? 'text' : 'password') : type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2480f8] ${
            error ? 'border-[#FF2E1F]' : 'border-[#d2d2d2]'
          }`}
        />
        {isPassword && (
          <button
            type="button"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {error && <span className="text-xs text-[#FF2E1F]">{error}</span>}
    </div>
  );
};
