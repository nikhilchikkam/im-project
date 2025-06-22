import React from 'react';

type DeleteConfirmationModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
};

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 z-50 flex justify-center items-center">
      <div className="bg-white p-8 rounded-lg shadow-xl text-center">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Are you absolutely sure?</h3>
        <p className="text-gray-600 mb-8">This will delete the account and remove data from the platform.</p>
        <div className="flex justify-center gap-4">
          <button
            onClick={onClose}
            className="font-semibold px-6 py-2 rounded-lg border border-gray-300 hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="font-semibold px-6 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal; 