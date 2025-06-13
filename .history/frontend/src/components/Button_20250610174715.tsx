import React from 'react';
import clsx from 'clsx';

type ButtonProps = {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  onClick?: () => void;
  isActive?: boolean;
};

const base = 'relative rounded-xl font-medium transition-colors focus:outline-none focus-visible:ring-2';
const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};
const variants = {
  primary: 'bg-[#2480f8] text-white hover:bg-[#185abc]',
  secondary: 'bg-[#34A853] text-white hover:bg-green-700',
  outline: 'border border-[#2480f8] text-[#2480f8] hover:bg-blue-50',
  ghost: 'text-[#2480f8] hover:bg-blue-50',
};

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled,
  onClick,
  isActive = false,
}: ButtonProps) => (
  <div className="flex flex-col items-center space-y-1">
    {isActive && (
      <span className="w-2 h-2 bg-[#2480f8] rounded-full mb-1" />
    )}
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        base,
        sizes[size],
        variants[variant],
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {children}
    </button>
  </div>
);
