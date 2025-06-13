import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NavbarAfter from '../components/NavbarAfter';
import WishlistList from '../features/wishlist/WishlistList';

const DEFAULT_IMAGE = 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=400&q=80';
const AVATARS = [
  'https://randomuser.me/api/portraits/men/32.jpg',
  'https://randomuser.me/api/portraits/women/44.jpg',
  'https://randomuser.me/api/portraits/men/45.jpg',
];

const WishlistPage = () => {
  const [wishlistName, setWishlistName] = useState('My first wishlist');
  const [wishlists, setWishlists] = useState<any[]>([]);
  const [showCreate, setShowCreate] = useState(true);
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setWishlistName(e.target.value);
  };

  const handleCreate = () => {
    setWishlists([
      ...wishlists,
      {
        name: wishlistName,
        image: DEFAULT_IMAGE,
        avatars: AVATARS,
        extraCount: 4,
      },
    ]);
    setShowCreate(false);
  };

  const handleAddNew = () => {
    setShowCreate(true);
    setWishlistName('');
  };

  const handleOpenWishlist = (index: number) => {
    navigate(`/wishlist/${index}`);
  };

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      <div className="flex items-start justify-between px-16 pt-8">
        {/* Left: Welcome message and wishlists */}
        <div className="flex flex-col flex-1 items-start justify-start mt-8">
          <h1 className="text-4xl font-bold mb-2">Hi, John</h1>
          <p className="text-lg text-gray-700 mb-8">Your wishlists</p>
          {/* Show wishlists if any and not in create mode */}
          {wishlists.length > 0 && !showCreate && (
            <WishlistList wishlists={wishlists} onAddNew={handleAddNew} onOpenWishlist={handleOpenWishlist} />
          )}
          {/* Create wishlist form */}
          {showCreate && (
            <div className="mt-8 bg-white rounded-xl shadow p-8 min-w-[380px] flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-1 text-center">You don't have any wishlist yet!</h2>
              <p className="text-gray-400 mb-6 text-center">Create your first one.</p>
              <input
                type="text"
                className="border rounded-lg px-4 py-2 w-full mb-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                value={wishlistName}
                onChange={handleInputChange}
                placeholder="My first wishlist"
              />
              <button
                className={`w-full py-2 rounded-lg text-white text-lg font-semibold transition ${wishlistName.trim() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-300 cursor-not-allowed'}`}
                onClick={handleCreate}
                disabled={!wishlistName.trim()}
              >
                Create
              </button>
            </div>
          )}
        </div>
        {/* Right: Top buttons */}
        <div className="flex-1 flex flex-col items-center justify-start pt-2 w-full">
          <div className="flex justify-end w-full mb-8 gap-4">
            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-lg text-base transition">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 104.5 4.5a7.5 7.5 0 0012.15 12.15z" /></svg>
              Find Products
            </button>
            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-lg text-base transition">
              <span className="text-xl font-bold">+</span> Add
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WishlistPage; 