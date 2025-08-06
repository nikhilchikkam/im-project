import React, { useRef, useEffect, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { createPortal } from 'react-dom';

interface DropdownOption {
  value: string;
  label: string;
  checked?: boolean;
}

interface DropdownProps {
  options: DropdownOption[];
  selectedValues: string[];
  onSelectionChange: (value: string) => void;
  placeholder: string;
  multiple?: boolean;
  maxHeight?: string;
  className?: string;
  dropdownWidth?: number;
  showCount?: boolean;
}

const Dropdown: React.FC<DropdownProps> = ({
  options,
  selectedValues,
  onSelectionChange,
  placeholder,
  multiple = true,
  maxHeight = 'max-h-60',
  className = '',
  dropdownWidth,
  showCount = true,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0, width: 0 });
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  // Calculate position when dropdown opens or scrolls
  useEffect(() => {
    if (isOpen && triggerRef.current) {
              const updatePosition = () => {
          const rect = triggerRef.current!.getBoundingClientRect();
          setPosition({
            top: rect.bottom + window.scrollY + 4, // Keep scroll offset for absolute positioning
            left: rect.left + window.scrollX,
            width: rect.width,
          });
        };

      // Update position immediately
      updatePosition();

      // Add scroll listener to update position on scroll
      window.addEventListener('scroll', updatePosition, { passive: true });
      window.addEventListener('resize', updatePosition, { passive: true });

      return () => {
        window.removeEventListener('scroll', updatePosition);
        window.removeEventListener('resize', updatePosition);
      };
    }
  }, [isOpen]);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          triggerRef.current && !triggerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const getDisplayText = () => {
    if (selectedValues.length === 0) {
      return placeholder;
    }
    
    if (!showCount) {
      return placeholder;
    }
    
    if (selectedValues.length === 1) {
      const option = options.find(opt => opt.value === selectedValues[0]);
      return option ? option.label : placeholder;
    }
    
    return `${selectedValues.length} selected`;
  };

  const handleOptionClick = (value: string) => {
    onSelectionChange(value);
    if (!multiple) {
      setIsOpen(false);
    }
  };

  return (
    <>
      {/* Trigger Button */}
      <div className={`relative ${className}`}>
        <button
          ref={triggerRef}
          type="button"
          className={`flex items-center justify-between w-full rounded-xl px-3 py-2 md:px-6 md:py-3 text-base md:text-lg font-medium min-w-[180px] md:min-w-[220px] transition-all
            ${selectedValues.length > 0 ? 'bg-white border border-blue-400 text-black shadow' : 'bg-[#eaeaea] text-gray-400'}`}
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className="flex-1 text-left truncate">{getDisplayText()}</span>
          <ChevronDown 
            className={`w-5 h-5 ml-2 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} 
          />
        </button>
      </div>

      {/* Dropdown Menu Portal */}
      {isOpen && typeof window !== 'undefined' && createPortal(
        <div
          ref={dropdownRef}
          className="absolute bg-white border border-gray-200 rounded-lg shadow-lg z-[9999]"
          style={{
            top: position.top,
            left: position.left,
            width: dropdownWidth || Math.max(position.width, 220), // Use custom width or default
            minWidth: dropdownWidth ? `${dropdownWidth}px` : '220px',
            maxWidth: dropdownWidth ? `${dropdownWidth}px` : '400px',
          }}
        >
          <div className={`py-2 overflow-y-auto ${maxHeight}`}>
            {options.map((option) => (
              <div
                key={option.value}
                className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer transition-colors"
                onClick={() => handleOptionClick(option.value)}
              >
                {multiple && (
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option.value)}
                    readOnly
                    className="mr-3 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                )}
                <span className="flex-1 text-gray-700 text-sm">{option.label}</span>
              </div>
            ))}
          </div>
        </div>,
        document.body
      )}
    </>
  );
};

export default Dropdown; 