import React from 'react';
import { Bookmark, PlusCircle } from 'lucide-react';
import { Modal } from '../../components/modals/Modal';

type Wishlist = {
  id: string;
  name: string;
  isSaved: boolean;
};

const mockWishlists: Wishlist[] = [
  { id: '1', name: 'Saved', isSaved: true },
  { id: '2', name: 'My wishlist', isSaved: false },
  { id: '3', name: 'My wishlist', isSaved: false },
];

type AddToWishlistModalProps = {
  isOpen: boolean;
  onClose: () => void;
  productName: string | null;
  onAddToWishlist: (wishlistId: string) => void;
};

const AddToWishlistModal: React.FC<AddToWishlistModalProps> = ({ isOpen, onClose, productName, onAddToWishlist }) => {
  if (!isOpen || !productName) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="md">
      <div className="flex items-center mb-6">
        <img src="https://i.imgur.com/4QfKuz1.png" alt={productName} className="w-16 h-16 rounded-md mr-4" />
        <div>
          <h2 className="text-xl font-semibold">{productName}</h2>
          <p className="text-gray-500">Select a wishlist to save this item</p>
        </div>
      </div>
      <div className="space-y-3">
        {mockWishlists.map((wishlist) => (
          <div 
            key={wishlist.id} 
            className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 cursor-pointer"
            onClick={() => onAddToWishlist(wishlist.id)}
          >
            <div className="flex items-center">
              <img src="https://via.placeholder.com/48" alt={wishlist.name} className="w-12 h-12 rounded-md mr-4" />
              <div>
                <h3 className="font-semibold">{wishlist.name}</h3>
                <p className="text-sm text-gray-500">Private</p>
              </div>
            </div>
            {wishlist.isSaved ? (
              <Bookmark className="w-6 h-6 text-blue-600" fill="currentColor" />
            ) : (
              <PlusCircle className="w-6 h-6 text-blue-600" />
            )}
          </div>
        ))}
      </div>
    </Modal>
  );
};

export default AddToWishlistModal; 