import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useCartWishlist } from '../../contexts/CartWishlistContext';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import CartList from '../../features/cart/CartList';
import LoginPrompt from '../../components/common/LoginPrompt';

const CartPage = () => {
  const { user } = useAuth();
  const { cartItems, cartCount, clearCart, loading } = useCartWishlist();
  
  // Redirect to login if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Your Cart</h2>
            <p className="text-gray-600 mb-6">You need to be logged in to view and manage your shopping cart.</p>
            <div className="space-y-3">
              <Link to="/login">
                <button className="w-full bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors">
                  Log In
                </button>
              </Link>
              <Link to="/signup">
                <button className="w-full bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors">
                  Create Account
                </button>
              </Link>
            </div>
            <div className="mt-6 pt-6 border-t border-gray-200">
              <Link to="/" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                ← Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const userName = user.first_name || user.email.split('@')[0];

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      <div className="flex items-start justify-between px-16 pt-8">
        {/* Left: Welcome message and cart content */}
        <div className="flex flex-col flex-1 items-start justify-start mt-8">
          <h1 className="text-4xl font-bold mb-2">Hi, {userName}</h1>
          <p className="text-lg text-gray-700 mb-8">Your shopping cart ({cartCount} items)</p>
          
          {cartItems.length > 0 ? (
            <CartList items={cartItems} />
          ) : (
            <div className="flex flex-col items-center justify-center text-center py-20 w-full">
              <img src="/cart.png" alt="Empty shopping cart" className="w-48 h-48 mb-8" />
              <h2 className="text-2xl font-semibold mb-2">You don't have any items in your cart yet!</h2>
              <p className="text-gray-500 mb-8">Add your first item.</p>
              <Link to="/products">
                <button className="bg-blue-600 text-white font-semibold py-3 px-8 rounded-lg text-lg hover:bg-blue-700 transition">
                  Shop Products
                </button>
              </Link>
            </div>
          )}
        </div>
        
        {/* Right: Action buttons & Summary */}
        <div className="flex-1 flex flex-col items-end justify-start pt-2 w-full">
          {cartItems.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8 w-full max-w-sm">
              <h3 className="text-lg font-semibold mb-4">Cart Summary</h3>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Items:</span>
                  <span>{cartCount}</span>
                </div>
                <div className="flex justify-between font-semibold">
                  <span>Total:</span>
                  <span>{cartCount} items</span>
                </div>
              </div>
              <button 
                className="w-full bg-red-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-red-700 transition mb-3"
                onClick={clearCart}
                disabled={loading}
              >
                {loading ? 'Clearing...' : 'Clear Cart'}
              </button>
            </div>
          )}
          
          <div className="flex justify-end w-full mb-8 gap-4">
            <Link to="/wishlist">
              <button className="bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg hover:bg-blue-700 transition">
                View Wishlist
              </button>
            </Link>
            <Link to="/products">
              <button className="bg-green-600 text-white font-semibold py-2 px-6 rounded-lg hover:bg-green-700 transition">
                Continue Shopping
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage; 