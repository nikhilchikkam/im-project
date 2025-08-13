import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useCartWishlist } from '../../contexts/CartWishlistContext';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import ProductCard from '../../components/product/ProductCard';
import ProductTable from '../../components/product/ProductTable';
import { LayoutGrid, List, ArrowLeft } from 'lucide-react';
import LoginRequiredModal from '../../components/common/LoginRequiredModal';

const WishlistGroupDetailPage: React.FC = () => {
  const { groupId } = useParams<{ groupId: string }>();
  const { user, loading: authLoading } = useAuth();
  const { addItemsToGroup, loading } = useCartWishlist();
  const navigate = useNavigate();
  
  const [groupDetails, setGroupDetails] = useState<any>(null);
  const [groupItems, setGroupItems] = useState<any[]>([]);
  const [viewType, setViewType] = useState<'card' | 'list'>('card');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch group details and items
  useEffect(() => {
    if (!user || !groupId) return;

    const fetchGroupDetails = async () => {
      try {
        const response = await fetch(`/api/wishlist-groups/${groupId}`);
        if (response.ok) {
          const data = await response.json();
          setGroupDetails(data);
        } else {
          setError('Failed to load group details');
        }
      } catch (error) {
        console.error('Error fetching group details:', error);
        setError('Failed to load group details');
      }
    };

    const fetchGroupItems = async () => {
      try {
        const response = await fetch(`/api/wishlist-groups/${groupId}/items`);
        if (response.ok) {
          const data = await response.json();
          setGroupItems(data.items || []);
        } else {
          setError('Failed to load group items');
        }
      } catch (error) {
        console.error('Error fetching group items:', error);
        setError('Failed to load group items');
      }
    };

    fetchGroupDetails();
    fetchGroupItems();
  }, [user, groupId]);

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
      setSelectedItems(groupItems.map(item => item.gtin));
      setSelectAll(true);
    }
  };

  // Show loading while auth is initializing
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show login prompt if not authenticated
  if (!user) {
    return (
      <LoginRequiredModal
        isOpen={true}
        onClose={() => window.history.back()}
        title="Login Required"
        description="You need to be logged in to view this wishlist group."
      />
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/wishlist-groups')}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Back to Groups
          </button>
        </div>
      </div>
    );
  }

  if (!groupDetails) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavbarAfter />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/wishlist-groups')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Groups</span>
            </button>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{groupDetails.name}</h1>
            {groupDetails.description && (
              <p className="text-gray-600 mb-4">{groupDetails.description}</p>
            )}
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <span>{groupItems.length} items</span>
              <span>{groupDetails.member_count} members</span>
              {groupDetails.is_public && (
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                  Public
                </span>
              )}
              <span>Created {new Date(groupDetails.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Group Items</h2>
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
          </div>

          <div className="p-6">
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
                    <button
                      onClick={() => {
                        // TODO: Implement remove from group functionality
                        alert('Remove from group functionality coming soon!');
                      }}
                      className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 flex items-center space-x-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      <span>Remove from Group</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Items Display */}
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : groupItems.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                  <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h2 className="text-2xl font-semibold mb-2">No items in this group</h2>
                <p className="text-gray-600 mb-6">This group is empty. Add items from your wishlist to get started.</p>
                <Link to="/wishlist">
                  <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    Go to Wishlist
                  </button>
                </Link>
              </div>
            ) : viewType === 'card' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {groupItems.map((item) => {
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
                      isSelected={selectedItems.includes(item.gtin)}
                      onSelect={() => handleItemSelect(item.gtin)}
                      showCheckbox={true}
                    />
                  );
                })}
              </div>
            ) : (
              <ProductTable 
                products={groupItems.map(item => ({
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
        </div>
      </div>
    </div>
  );
};

export default WishlistGroupDetailPage; 