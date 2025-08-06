import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { LayoutGrid, List, FolderPlus } from 'lucide-react';
import { useAuth, useAuthenticatedFetch } from '../../contexts/AuthContext';
import { useCartWishlist } from '../../contexts/CartWishlistContext';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import ProductCard from '../../components/product/ProductCard';
import ProductTable from '../../components/product/ProductTable';
import HierarchyModal from '../../components/modals/HierarchyModal';
import ProductDetailsModal from '../../features/products/ProductDetailsModal';
import EditGroupModal from '../../features/wishlist/EditGroupModal';
import RemoveWishlistItemModal from '../../components/modals/RemoveWishlistItemModal';


const WishlistPage = () => {
  const { user } = useAuth();
  const { authenticatedFetch } = useAuthenticatedFetch();
  const { wishlistItems, wishlistCount, clearWishlist, loading, addToCart, removeFromWishlist, addItemsToGroup, wishlistGroups, refreshWishlist, createWishlistGroup, updateWishlistGroup, deleteWishlistGroup, fetchWishlistGroups } = useCartWishlist();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<'items' | 'groups'>('items');

  // Set active tab based on URL parameter
  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab === 'groups') {
      setActiveTab('groups');
    } else {
      setActiveTab('items');
    }
  }, [searchParams]);
  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDescription, setNewGroupDescription] = useState('');
  const [showEditGroupModal, setShowEditGroupModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState<any>(null);
  const [selectedGroupDetails, setSelectedGroupDetails] = useState<any>(null);
  const [selectedGroupItems, setSelectedGroupItems] = useState<any[]>([]);
  const [viewingGroupDetails, setViewingGroupDetails] = useState(false);
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

  const [moveToGroupModal, setMoveToGroupModal] = useState<{
    isOpen: boolean;
    selectedGroupId: number | null;
  }>({
    isOpen: false,
    selectedGroupId: null,
  });

  const [removeItemModal, setRemoveItemModal] = useState<{
    isOpen: boolean;
    itemName: string;
    gtin: string;
    groups: { id: number; name: string }[];
  }>({
    isOpen: false,
    itemName: '',
    gtin: '',
    groups: [],
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
      console.error('Failed to delete selected items:', error);
    }
  };

  const handleMoveToGroup = async () => {
    if (!moveToGroupModal.selectedGroupId) {
      alert('Please select a group to move items to');
      return;
    }

    try {
      const success = await addItemsToGroup(moveToGroupModal.selectedGroupId, selectedItems);
      if (success) {
        setSelectedItems([]);
        setSelectAll(false);
        setMoveToGroupModal({ isOpen: false, selectedGroupId: null });
        alert(`Successfully moved ${selectedItems.length} items to the group`);
        // Refresh the wishlist to reflect the changes
        await refreshWishlist();
      }
    } catch (error) {
      console.error('Failed to move items to group:', error);
      alert('Failed to move items to group');
    }
  };

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) {
      return;
    }

    const success = await createWishlistGroup(
      newGroupName.trim(),
      newGroupDescription.trim() || undefined
    );

    if (success) {
      setShowCreateGroupModal(false);
      setNewGroupName('');
      setNewGroupDescription('');
    }
  };

  const handleEditGroup = (group: any) => {
    setEditingGroup(group);
    setShowEditGroupModal(true);
  };

  const handleSaveEditGroup = async (name: string, description: string, isPublic: boolean) => {
    if (!editingGroup) return;
    
    try {
      await updateWishlistGroup(editingGroup.id, name, description, isPublic);
      setShowEditGroupModal(false);
      setEditingGroup(null);
    } catch (error) {
      console.error('Error updating group:', error);
      alert('Failed to update group');
    }
  };

  const handleDeleteGroup = async (groupId: number) => {
    if (!confirm('Are you sure you want to delete this wishlist group? This action cannot be undone.')) {
      return;
    }

    await deleteWishlistGroup(groupId);
  };

  const handleRemoveFromGroup = async (gtin: string) => {
    if (!selectedGroupDetails) return;
    
    if (window.confirm('Are you sure you want to remove this item from the group?')) {
      try {
        // Call API to remove item from group
        const response = await fetch(`/api/wishlist-groups/${selectedGroupDetails.id}/remove-items`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          },
          body: JSON.stringify({ gtins: [gtin] })
        });

        if (response.ok) {
          // Remove item from local state
          setSelectedGroupItems(prev => prev.filter(item => item.gtin !== gtin));
          // Refresh wishlist groups to update item counts
          await fetchWishlistGroups();
        } else {
          throw new Error('Failed to remove item from group');
        }
      } catch (error) {
        console.error('Error removing item from group:', error);
        alert('Failed to remove item from group');
      }
    }
  };

  const handleRemoveItem = (item: any) => {
    const groups = item.groups || [];
    setRemoveItemModal({
      isOpen: true,
      itemName: item.product.name,
      gtin: item.gtin,
      groups: groups,
    });
  };

  const handleConfirmRemoveItem = async () => {
    const result = await removeFromWishlist(removeItemModal.gtin);
    setRemoveItemModal({
      isOpen: false,
      itemName: '',
      gtin: '',
      groups: [],
    });
    
    // Show success message with group information if available
    if (result && result.removed_from_groups && result.removed_from_groups.length > 0) {
      alert(`✅ ${result.message}\n\nThis item was also removed from:\n• ${result.removed_from_groups.join('\n• ')}`);
    } else if (result) {
      alert('✅ Item removed from wishlist successfully');
    }
  };

  const handleCancelRemoveItem = () => {
    setRemoveItemModal({
      isOpen: false,
      itemName: '',
      gtin: '',
      groups: [],
    });
  };

  const handleViewGroupItems = async (groupId: number) => {
    try {
      // Fetch group details
      const groupResponse = await fetch(`/api/wishlist-groups/${groupId}`);
      if (!groupResponse.ok) {
        throw new Error('Failed to fetch group details');
      }
      const groupData = await groupResponse.json();
      
      // Fetch group items
      const itemsResponse = await fetch(`/api/wishlist-groups/${groupId}/items`);
      if (!itemsResponse.ok) {
        throw new Error('Failed to fetch group items');
      }
      const itemsData = await itemsResponse.json();
      
      setSelectedGroupDetails(groupData);
      setSelectedGroupItems(itemsData.items || []);
      setViewingGroupDetails(true);
    } catch (error) {
      console.error('Error fetching group details:', error);
      alert('Failed to load group details');
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
                  onClick={() => {
                    setActiveTab('items');
                    navigate('/wishlist?tab=items');
                  }}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'items'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Items ({wishlistCount})
                </button>
                <button
                  onClick={() => {
                    setActiveTab('groups');
                    navigate('/wishlist?tab=groups');
                  }}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'groups'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Groups ({wishlistGroups.length})
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
            <div className="w-full">
              {activeTab === 'items' ? (
                // Items Tab Content
                wishlistItems.length > 0 ? (
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
                                <span>Cart</span>
                              </button>
                              <button
                                onClick={() => setMoveToGroupModal({ isOpen: true, selectedGroupId: null })}
                                className="bg-green-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-green-700 flex items-center space-x-1"
                              >
                                <FolderPlus className="w-4 h-4" />
                                <span>Group</span>
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
                                onRemove={() => handleRemoveItem(item)}
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
                )
                            ) : (
                // Groups Tab Content
                viewingGroupDetails && selectedGroupDetails ? (
                  // Group Details View
                  <div className="flex flex-col space-y-4">
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center space-x-4">
                        <button
                          onClick={() => {
                            setViewingGroupDetails(false);
                            setSelectedGroupDetails(null);
                            setSelectedGroupItems([]);
                          }}
                          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                          </svg>
                          <span>Back to Groups</span>
                        </button>
                        <h2 className="text-2xl font-semibold">{selectedGroupDetails.name}</h2>
                      </div>
                      <button
                        onClick={() => setShowCreateGroupModal(true)}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                      >
                        Create New Group
                      </button>
                    </div>

                    {/* Group Info */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
                      {selectedGroupDetails.description && (
                        <p className="text-gray-600 mb-2">{selectedGroupDetails.description}</p>
                      )}
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{selectedGroupItems.length} items</span>
                        <span>{selectedGroupDetails.member_count} members</span>
                        {selectedGroupDetails.is_public && (
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                            Public
                          </span>
                        )}
                        <span>Created {new Date(selectedGroupDetails.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Group Items */}
                    {selectedGroupItems.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                          <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                          </svg>
                        </div>
                        <h2 className="text-2xl font-semibold mb-2">No items in this group</h2>
                        <p className="text-gray-600 mb-6">This group is empty. Add items from your wishlist to get started.</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
                        {selectedGroupItems.map((item) => {
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
                          
                          return (
                            <div key={item.id} className="relative group">
                              <ProductCard
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
                                showCheckbox={false}
                              />
                              <button
                                onClick={() => handleRemoveFromGroup(item.gtin)}
                                className="absolute top-2 right-2 bg-red-600 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-700"
                                title="Remove from group"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ) : (
                  // Groups List View
                  wishlistGroups.length > 0 ? (
                  <div className="flex flex-col space-y-4">
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-2xl font-semibold">Your Wishlist Groups</h2>
                    </div>

                    {/* Loading State */}
                    {loading && (
                      <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      </div>
                    )}

                    {/* Groups Grid with Create Button */}
                    {!loading && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
                        {wishlistGroups.map((group) => (
                          <div key={group.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 group h-80">
                            {/* Card Header with Image Placeholder */}
                            <div className="h-32 bg-gradient-to-br from-blue-50 to-indigo-100 relative">
                              <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-16 h-16 bg-white/80 rounded-full flex items-center justify-center shadow-sm">
                                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                  </svg>
                                </div>
                              </div>
                              {/* Action buttons overlay */}
                              {group.is_owner && (
                                <div className="absolute top-2 right-2 flex space-x-1">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleEditGroup(group);
                                    }}
                                    className="bg-blue-500 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-blue-600"
                                    title="Edit group"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                    </svg>
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleDeleteGroup(group.id);
                                    }}
                                    className="bg-red-500 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                                    title="Delete group"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                  </button>
                                </div>
                              )}
                            </div>
                            
                            {/* Card Content */}
                            <div className="p-4 flex flex-col h-48">
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex-1 min-w-0">
                                  <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">{group.name}</h3>
                                  <div className="h-10 mb-2">
                                    {group.description ? (
                                      <p className="text-sm text-gray-600 line-clamp-2">{group.description}</p>
                                    ) : (
                                      <div className="h-5"></div>
                                    )}
                                  </div>
                                </div>
                              </div>
                              
                              {/* Stats Row */}
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-4 text-sm text-gray-600">
                                  <span className="flex items-center space-x-1">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                    </svg>
                                    <span>{group.item_count} items</span>
                                  </span>
                                  <span className="flex items-center space-x-1">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                                    </svg>
                                    <span>{group.member_count} members</span>
                                  </span>
                                </div>
                                {group.is_public && (
                                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                                    Public
                                  </span>
                                )}
                              </div>
                              
                              {/* Action Buttons */}
                              <div className="flex items-center justify-between mt-auto">
                                <div className="text-xs text-gray-400">
                                  Created {new Date(group.created_at).toLocaleDateString()}
                                </div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleViewGroupItems(group.id);
                                  }}
                                  className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center space-x-1"
                                >
                                  <span>View Details</span>
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                  </svg>
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        {/* Create New Group Card */}
                        <div className="bg-white rounded-xl shadow-sm border-2 border-dashed border-gray-300 hover:border-blue-400 hover:shadow-lg transition-all duration-200 group cursor-pointer h-80">
                          <div className="h-32 bg-gradient-to-br from-gray-50 to-gray-100 relative">
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center shadow-sm group-hover:bg-blue-700 transition-colors">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                </svg>
                              </div>
                            </div>
                          </div>
                          
                          <div className="p-4 text-center flex flex-col h-48">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Create New Group</h3>
                            <p className="text-sm text-gray-600 mb-4">Organize your wishlist items into groups</p>
                                                          <button
                                onClick={() => setShowCreateGroupModal(true)}
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors w-full mt-auto"
                              >
                                Create Group
                              </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-center py-20 w-full">
                    <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                    <h2 className="text-2xl font-semibold mb-2">No wishlist groups yet</h2>
                    <p className="text-gray-600 mb-6">Create your first wishlist group to get started.</p>
                    <button
                      onClick={() => setShowCreateGroupModal(true)}
                      className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Create Your First Group
                    </button>
                  </div>
                )
              )
            )}
            </div>
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

      {/* Create Group Modal */}
      {showCreateGroupModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Create New Wishlist Group</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Group Name *
                </label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter group name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newGroupDescription}
                  onChange={(e) => setNewGroupDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter description (optional)"
                  rows={3}
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateGroupModal(false);
                  setNewGroupName('');
                  setNewGroupDescription('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateGroup}
                disabled={loading || !newGroupName.trim()}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create Group'}
              </button>
            </div>
          </div>
        </div>
      )}



      {/* Move to Group Modal */}
      {moveToGroupModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Move to Wishlist Group</h2>
            <p className="text-gray-600 mb-4">Select a group to move {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} to:</p>
            
            <div className="space-y-3 mb-6 max-h-60 overflow-y-auto">
              {wishlistGroups.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No wishlist groups available. Create a group first.</p>
              ) : (
                wishlistGroups.map((group) => (
                  <label key={group.id} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name="group"
                      value={group.id}
                      checked={moveToGroupModal.selectedGroupId === group.id}
                      onChange={(e) => setMoveToGroupModal(prev => ({ ...prev, selectedGroupId: parseInt(e.target.value) }))}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{group.name}</div>
                      {group.description && (
                        <div className="text-sm text-gray-500">{group.description}</div>
                      )}
                      <div className="text-xs text-gray-400">
                        {group.item_count} items • {group.member_count} members
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setMoveToGroupModal({ isOpen: false, selectedGroupId: null })}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleMoveToGroup}
                disabled={!moveToGroupModal.selectedGroupId || loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Moving...' : 'Move to Group'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Group Modal */}
      <EditGroupModal
        isOpen={showEditGroupModal}
        onClose={() => {
          setShowEditGroupModal(false);
          setEditingGroup(null);
        }}
        onSave={handleSaveEditGroup}
        group={editingGroup}
      />

      {/* Remove Wishlist Item Modal */}
      <RemoveWishlistItemModal
        isOpen={removeItemModal.isOpen}
        onClose={handleCancelRemoveItem}
        onConfirm={handleConfirmRemoveItem}
        itemName={removeItemModal.itemName}
        groups={removeItemModal.groups}
      />
    </div>
  );
};

export default WishlistPage; 