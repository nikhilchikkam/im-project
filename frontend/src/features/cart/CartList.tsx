import React from 'react';

const CartList = ({ items }: { items: any[] }) => {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Your Cart Items</h2>
      {/* This will be replaced with actual item rendering logic */}
      <p>{items.length} items in your cart.</p>
    </div>
  );
};

export default CartList; 