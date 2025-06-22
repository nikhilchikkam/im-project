import React from 'react';
import { Modal } from './Modal';

type ExportModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onExport: (format: 'pdf' | 'csv') => void;
};

const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose, onExport }) => {
  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="sm">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-6">
          Export the list of the selected items in any of the below formats
        </h2>
        <div className="flex justify-center gap-4">
          <button 
            onClick={() => onExport('pdf')}
            className="bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 transition"
          >
            .pdf
          </button>
          <button 
            onClick={() => onExport('csv')}
            className="bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 transition"
          >
            .csv
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ExportModal; 