import React from 'react';

type InputProps = {
  label: string;
  type?: string;
  placeholder?: string;
  error?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export const Input = ({ label, type = 'text', placeholder, error, value, onChange }: InputProps) => (
  <div className="flex flex-col space-y-1">
    <label className="text-sm font-medium text-[#333]">{label}</label>
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={`px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2480f8] ${
        error ? 'border-[#FF2E1F]' : 'border-[#d2d2d2]'
      }`}
    />
    {error && <span className="text-xs text-[#FF2E1F]">{error}</span>}
  </div>
);
