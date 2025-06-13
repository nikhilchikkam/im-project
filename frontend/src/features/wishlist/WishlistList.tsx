import React from 'react';
import WishlistCard from './WishlistCard';
import AddWishlistButton from './AddWishlistButton';

type Wishlist = {
  name: string;
  image: string;
  avatars: string[];
  extraCount: number;
};

type WishlistListProps = {
  wishlists: Wishlist[];
  onAddNew: () => void;
  onOpenWishlist: (index: number) => void;
};

const WishlistList: React.FC<WishlistListProps> = ({ wishlists, onAddNew, onOpenWishlist }) => (
  <div className="flex items-center gap-12 mt-8">
    {wishlists.map((wl, idx) => (
      <WishlistCard key={idx} {...wl} onClick={() => onOpenWishlist(idx)} />
    ))}
    <AddWishlistButton onClick={onAddNew} />
  </div>
);

export default WishlistList; 