import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import NavbarAfter from '../../components/navigation/NavbarAfter';
// We'll use CartList when there are items.
// import CartList from '../../features/cart/CartList'; 

const CartPage = () => {
  const [cartItems, setCartItems] = useState<any[]>([]); // To be replaced with real data
  const userName = "John"; // This would come from user state

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      <div className="flex items-start justify-between px-16 pt-8">
        {/* Left: Welcome message and cart content */}
        <div className="flex flex-col flex-1 items-start justify-start mt-8">
          <h1 className="text-4xl font-bold mb-2">Hi, {userName}</h1>
          <p className="text-lg text-gray-700 mb-8">Your shopping cart</p>
          
          {cartItems.length > 0 ? (
            // <CartList items={cartItems} />
            <p>Your items will be listed here.</p>
          ) : (
            <div className="flex flex-col items-center justify-center text-center py-20 w-full">
              <img src="/cart.png" alt="Empty shopping cart" className="w-48 h-48 mb-8" />
              <h2 className="text-2xl font-semibold mb-2">You don't have any items in your cart yet!</h2>
              <p className="text-gray-500 mb-8">Add your first item.</p>
              <Link to="/">
                <button className="bg-blue-600 text-white font-semibold py-3 px-8 rounded-lg text-lg hover:bg-blue-700 transition">
                  Shop
                </button>
              </Link>
            </div>
          )}
        </div>
        
        {/* Right: Action buttons & Summary placeholder */}
        <div className="flex-1 flex flex-col items-end justify-start pt-2 w-full">
          {/* This section can hold a cart summary or checkout button later */}
          <div className="flex justify-end w-full mb-8 gap-4">
            <Link to="/cart/detail">
              <button className="bg-green-600 text-white font-semibold py-2 px-6 rounded-lg hover:bg-green-700 transition">
                View Cart Details
              </button>
            </Link>
            <Link to="/wishlist">
              <button className="bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg hover:bg-blue-700 transition">
                Wishlist
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage; 