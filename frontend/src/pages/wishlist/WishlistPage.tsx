import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LayoutGrid, List } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useCartWishlist } from '../../contexts/CartWishlistContext';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import ProductCard from '../../components/product/ProductCard';
import ProductTable from '../../components/product/ProductTable';
import HierarchyModal from '../../components/modals/HierarchyModal';
import ProductDetailsModal from '../../features/products/ProductDetailsModal';

const WishlistPage = () => {
  const { user } = useAuth();
  const { wishlistItems, wishlistCount, clearWishlist, loading, addToCart, removeFromWishlist } = useCartWishlist();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'items' | 'groups'>('items');
  const [error, setError] = useState<string | null>(null);
  const [viewType, setViewType] = useState<'card' | 'list'>('card');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);
  const [hierarchyModal, setHierarchyModal] = useState<{
    isOpen: boolean;
    gtin: string;
  }>({
    isOpen: false,
    gtin: '',
  });

  const handleHierarchyClick = (product: any) => {
    setHierarchyModal({
      isOpen: true,
      gtin: product.gtin,
    });
  };

  const closeHierarchyModal = () => {
    setHierarchyModal({
      isOpen: false,
      gtin: '',
    });
  };

  // Selection handlers
  const handleItemSelect = (gtin: string) => {
    setSelectedItems(prev => 
      prev.includes(gtin) 
        ? prev.filter(item => item !== gtin)
        : [...prev, gtin]
    );
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems([]);
      setSelectAll(false);
    } else {
      setSelectedItems(wishlistItems.map(item => item.gtin));
      setSelectAll(true);
    }
  };

  // Bulk action handlers
  const handleMoveToCart = async () => {
    try {
      for (const gtin of selectedItems) {
        await addToCart(gtin);
      }
      setSelectedItems([]);
      setSelectAll(false);
    } catch (error) {
      console.error('Failed to move items to cart:', error);
    }
  };

  const handleDeleteSelected = async () => {
    if (!confirm(`Are you sure you want to delete ${selectedItems.length} items from your wishlist?`)) {
      return;
    }

    try {
      for (const gtin of selectedItems) {
        await removeFromWishlist(gtin);
      }
      setSelectedItems([]);
      setSelectAll(false);
    } catch (error) {
      console.error('Failed to delete items:', error);
    }
  };
  
  // Redirect to login if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Your Wishlist</h2>
            <p className="text-gray-600 mb-6">You need to be logged in to view and manage your wishlist.</p>
            <div className="space-y-3">
              <Link to="/login">
                <button className="w-full bg-red-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-red-700 transition-colors">
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
              <Link to="/" className="text-red-600 hover:text-red-700 text-sm font-medium">
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
        {/* Left: Welcome message and wishlist content */}
        <div className="flex flex-col flex-1 items-start justify-start mt-8">
          <h1 className="text-4xl font-bold mb-2">Hi, {userName}</h1>
          <p className="text-lg text-gray-700 mb-8">Your wishlists</p>
          
          {/* Tabs */}
          <div className="w-full mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('items')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'items'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Items ({wishlistCount})
                </button>
                <button
                  onClick={() => setActiveTab('groups')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'groups'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Groups (0)
                </button>
              </nav>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="w-full mb-6 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
                <div className="ml-auto pl-3">
                  <div className="-mx-1.5 -my-1.5">
                    <button
                      onClick={() => setError(null)}
                      className="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100"
                    >
                      <span className="sr-only">Dismiss</span>
                      <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content */}
          <section className="max-w-6xl mx-auto px-4 pb-12">
            {activeTab === 'items' ? (
              // Items Tab
              <div className="w-full">
                {wishlistItems.length > 0 ? (
                  <div className="flex flex-col space-y-4">
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-2xl font-semibold">Your Wishlist Items</h2>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setViewType('card')}
                          className={`p-2 rounded-lg ${viewType === 'card' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                          <LayoutGrid className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => setViewType('list')}
                          className={`p-2 rounded-lg ${viewType === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                          <List className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Selection and Bulk Actions Bar */}
                    {selectedItems.length > 0 && (
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2 bg-white px-3 py-2 rounded-md border">
                              <input
                                type="checkbox"
                                checked={selectAll}
                                onChange={handleSelectAll}
                                className="w-4 h-4 text-blue-600"
                              />
                              <span className="text-sm font-medium text-gray-700">
                                {selectedItems.length} items selected
                              </span>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-600">Move items to:</span>
                              <button
                                onClick={handleMoveToCart}
                                className="bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 flex items-center space-x-1"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
                                </svg>
                              </button>
                            </div>
                            
                            <button
                              onClick={handleDeleteSelected}
                              className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 flex items-center space-x-1"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                              <span>Delete</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {viewType === 'card' ? (
                      <>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
                          {wishlistItems.map((item) => {
                            // Debug: Log the item to see what data we're getting
                            console.log('Wishlist item:', item);
                            
                            // Parse image_urls from JSON string if needed
                            let imageUrls: string[] = [];
                            if (item.product.image_urls) {
                              try {
                                const imageData = typeof item.product.image_urls === 'string' 
                                  ? JSON.parse(item.product.image_urls) 
                                  : item.product.image_urls;
                                
                                if (imageData && typeof imageData === 'object') {
                                  if (Array.isArray(imageData.externalFileLink)) {
                                    imageUrls = imageUrls.concat(imageData.externalFileLink.filter(Boolean));
                                  }
                                  if (Array.isArray(imageData.dam)) {
                                    imageUrls = imageUrls.concat(imageData.dam.filter(Boolean));
                                  }
                                }
                              } catch (error) {
                                console.error('Error parsing image_urls:', error);
                              }
                            }
                            
                            // Create product object with all necessary fields
                            const product = {
                              gtin: item.gtin,
                              normalized_name: item.product.normalized_name || item.product.name,
                              name: item.product.normalized_name || item.product.name,
                              title: item.product.normalized_name || item.product.name,
                              family_title: item.product.family_title || '',
                              description: item.product.description,
                              is_smart_snack: item.product.is_smart_snack || false,
                              nova_label: item.product.nova_label || '',
                              is_good_choice: item.product.is_good_choice || '',
                              image_urls: imageUrls
                            };
                            
                            return (
                              <ProductCard
                                key={item.id}
                                upc={item.gtin}
                                normalized_name={item.product.normalized_name || item.product.name}
                                name={item.product.normalized_name || item.product.name}
                                title={item.product.normalized_name || item.product.name}
                                category={item.product.family_title || ''}
                                description={item.product.description}
                                isSmartSnack={item.product.is_smart_snack || false}
                                novaLabel={item.product.nova_label || undefined}
                                isGoodChoice={item.product.is_good_choice || undefined}
                                imageUrls={imageUrls}
                                onEnlarge={() => setSelectedProduct(product)}
                                onHierarchy={() => handleHierarchyClick(product)}
                                isSelected={selectedItems.includes(item.gtin)}
                                onSelect={() => handleItemSelect(item.gtin)}
                                showCheckbox={true}
                              />
                            );
                          })}
                        </div>
                      </>
                    ) : (
                      <ProductTable 
                        products={wishlistItems.map(item => ({
                          id: item.gtin,
                          category: item.product.product_type || 'General',
                          itemNumber: item.gtin,
                          name: item.product.name,
                          normalized_name: item.product.name,
                          description: item.product.description || 'No description available'
                        }))}
                        selectedItems={selectedItems}
                        onItemSelect={handleItemSelect}
                        selectAll={selectAll}
                        onSelectAll={handleSelectAll}
                      />
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-center py-20 w-full">
                    <img src="/wishlist-welcome.png" alt="Empty wishlist" className="w-48 h-48 mb-8" />
                    <h2 className="text-2xl font-semibold mb-2">Your wishlist is empty!</h2>
                    <p className="text-gray-600 mb-6">Start adding products to your wishlist to see them here.</p>
                    <Link to="/products">
                      <button className="bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors">
                        Continue Shopping
                      </button>
                    </Link>
                  </div>
                )}
              </div>
            ) : (
              // Groups Tab
              <div className="w-full">
                <div className="flex flex-col items-center justify-center text-center py-20 w-full">
                  <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mb-6">
                    <svg className="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-semibold mb-2">Under Construction</h2>
                  <p className="text-gray-600 mb-6">Wishlist groups feature is coming soon!</p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md">
                    <p className="text-sm text-blue-800">
                      We're working on bringing you the ability to organize your wishlist items into groups. 
                      Stay tuned for updates!
                    </p>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>

        {/* Right: Action buttons */}
        <div className="flex flex-col space-y-4 mt-8">
          <button
            onClick={() => navigate('/products')}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Continue Shopping
          </button>
        </div>
      </div>

      {/* Create Wishlist Group Modal */}
      {/* {showCreateModal && (
        <CreateWishlistGroupModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateGroup}
        />
      )} */}
      
      {/* Product Details Modal */}
      {selectedProduct && (
        <ProductDetailsModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}

      {/* Hierarchy Modal */}
      <HierarchyModal
        isOpen={hierarchyModal.isOpen}
        onClose={closeHierarchyModal}
        gtin={hierarchyModal.gtin}
      />
    </div>
  );
};

export default WishlistPage; 