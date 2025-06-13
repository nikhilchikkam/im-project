import React from 'react';

type AddWishlistButtonProps = {
  onClick: () => void;
};

const AddWishlistButton: React.FC<AddWishlistButtonProps> = ({ onClick }) => (
  <button
    onClick={onClick}
    className="w-20 h-20 rounded-full border-2 border-blue-300 flex items-center justify-center text-4xl text-blue-600 bg-white shadow hover:bg-blue-50 transition"
    aria-label="Add new wishlist"
  >
    +
  </button>
);

export default AddWishlistButton; 