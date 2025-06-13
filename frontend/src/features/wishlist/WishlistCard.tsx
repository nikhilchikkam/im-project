import React from 'react';

type WishlistCardProps = {
  name: string;
  image: string;
  avatars: string[];
  extraCount: number;
  onMenuClick?: () => void;
  onClick?: () => void;
};

const WishlistCard: React.FC<WishlistCardProps> = ({ name, image, avatars, extraCount, onMenuClick, onClick }) => (
  <div
    className="rounded-2xl overflow-hidden shadow bg-gray-50 w-[300px] min-h-[220px] flex flex-col justify-end relative cursor-pointer hover:shadow-md transition"
    onClick={onClick}
  >
    <img src={image} alt="wishlist" className="w-full h-[150px] object-cover" />
    <div className="flex items-center justify-between px-4 py-3 bg-gray-100">
      <div>
        <div className="text-lg font-semibold">{name}</div>
      </div>
      <div className="flex items-center -space-x-2">
        {avatars.map((a, i) => (
          <img key={i} src={a} alt="avatar" className="w-6 h-6 rounded-full border-2 border-white" style={{ zIndex: 10 - i }} />
        ))}
        <span className="ml-2 text-xs bg-blue-100 text-blue-700 rounded-full px-2 py-0.5 font-bold">+{extraCount}</span>
      </div>
      <button className="ml-2 text-gray-500 hover:text-gray-700" onClick={e => { e.stopPropagation(); onMenuClick && onMenuClick(); }}>
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
      </button>
    </div>
  </div>
);

export default WishlistCard; 