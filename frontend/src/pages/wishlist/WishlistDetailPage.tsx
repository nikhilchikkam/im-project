import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import Toolbar from '../../components/ui/Toolbar';
import BulkActionsBar from '../../components/common/BulkActionsBar';
import WishlistTable from '../../features/wishlist/WishlistTable';
import type { DataItem } from '../../components/ui/DataTable';

interface WishlistItem {
  id: string;
  gtin: string;
  added_at: string;
  product: {
    name: string;
    description: string;
    product_type: string;
    image_urls: string[];
  };
}

const WishlistDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [title, setTitle] = useState(`My Wishlist ${id}`);
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWishlistItems = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const response = await fetch('/api/wishlist', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setItems(data.items || []);
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Failed to fetch wishlist items');
        }
      } catch (error) {
        console.error('Failed to fetch wishlist items:', error);
        setError('Failed to fetch wishlist items');
      } finally {
        setLoading(false);
      }
    };

    fetchWishlistItems();
  }, [user]);

  const handleSelect = (itemId: string) => {
    setSelectedItems(prev => prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]);
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedItems(checked ? items.map(item => item.id) : []);
  };

  const handleBulkDelete = async () => {
    try {
      // Delete selected items
      for (const itemId of selectedItems) {
        await fetch(`/api/wishlist/${itemId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });
      }
      
      // Remove from local state
      setItems(prev => prev.filter(item => !selectedItems.includes(item.id)));
      setSelectedItems([]);
    } catch (error) {
      console.error('Failed to delete items:', error);
      setError('Failed to delete selected items');
    }
  };

  const handleAddToList = (id: string) => {
    console.log(`Adding item ${id} to another list`);
  };
  
  const handleMoreOptions = (id: string) => {
    console.log(`More options for item ${id}`);
  };

  const handleBulkMoveToCart = async () => {
    try {
      // Move selected items to cart
      for (const itemId of selectedItems) {
        await fetch('/api/cart', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
          body: JSON.stringify({
            gtin: items.find(item => item.id === itemId)?.gtin,
            quantity: 1,
          }),
        });
      }
      
      // Remove from wishlist after moving to cart
      setItems(prev => prev.filter(item => !selectedItems.includes(item.id)));
      setSelectedItems([]);
    } catch (error) {
      console.error('Failed to move items to cart:', error);
      setError('Failed to move items to cart');
    }
  };

  // Convert wishlist items to DataItem format for the table
  const tableItems: DataItem[] = items.map(item => ({
    id: item.id,
    category: item.product.product_type || 'General',
    itemNumber: item.gtin,
    product: item.product.name,
    description: item.product.description || 'No description available',
  }));

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Please log in</h2>
          <p className="text-gray-600">You need to be logged in to view this wishlist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <NavbarAfter />
      <main className="flex-1 container mx-auto px-6 py-8">
        <Toolbar
          title={title}
          onBack={() => navigate('/wishlist')}
          onTitleChange={setTitle}
          onShare={() => console.log('Share action')}
          onAddItem={() => navigate('/')}
        />
        
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {selectedItems.length > 0 && (
              <BulkActionsBar
                selectedCount={selectedItems.length}
                onDelete={handleBulkDelete}
                onClearSelection={() => setSelectedItems([])}
                onSecondaryAction={handleBulkMoveToCart}
                secondaryActionLabel="Move to Cart"
              />
            )}
            <WishlistTable
              items={tableItems}
              selectedItems={selectedItems}
              onSelect={handleSelect}
              onSelectAll={handleSelectAll}
              onAddToList={handleAddToList}
              onMoreOptions={handleMoreOptions}
            />
          </>
        )}
      </main>
    </div>
  );
};

export default WishlistDetailPage; 