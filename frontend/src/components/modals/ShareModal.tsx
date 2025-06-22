import React from 'react';
import { Modal } from './Modal';
import { Users, Mail } from 'lucide-react';

type ShareModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onShareOption: (option: 'link' | 'email') => void;
};

const ShareModal: React.FC<ShareModalProps> = ({ isOpen, onClose, onShareOption }) => {
  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="sm">
      <div className="p-4">
        <ul>
          <li
            className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-100 cursor-pointer"
            onClick={() => onShareOption('link')}
          >
            <Users className="w-5 h-5 text-gray-600" />
            <span className="font-medium text-gray-700">Share with others</span>
          </li>
          <li
            className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-100 cursor-pointer"
            onClick={() => onShareOption('email')}
          >
            <Mail className="w-5 h-5 text-gray-600" />
            <span className="font-medium text-gray-700">Email</span>
          </li>
        </ul>
      </div>
    </Modal>
  );
};

export default ShareModal; 