import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useCartWishlist } from '../../contexts/CartWishlistContext';
import LoginPrompt from '../../components/common/LoginPrompt';
import WishlistGroupCard from '../../features/wishlist/WishlistGroupCard';
import CreateWishlistGroupModal from '../../features/wishlist/CreateWishlistGroupModal';
import { Button } from '../../components/ui/Button';

interface WishlistGroup {
  id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  member_count: number;
  item_count: number;
  is_owner: boolean;
}

const WishlistGroupsPage: React.FC = () => {
  const { user } = useAuth();
  const [wishlistGroups, setWishlistGroups] = useState<WishlistGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = import.meta.env.VITE_API_URL || '';

  const fetchWishlistGroups = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/wishlist-groups/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setWishlistGroups(data.groups || []);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch wishlist groups');
      }
    } catch (error) {
      console.error('Failed to fetch wishlist groups:', error);
      setError('Failed to fetch wishlist groups');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchWishlistGroups();
    }
  }, [user]);

  const handleCreateGroup = async (name: string, description: string, isPublic: boolean) => {
    try {
      const response = await fetch(`${apiUrl}/api/wishlist-groups/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          name,
          description,
          is_public: isPublic,
        }),
      });

      if (response.ok) {
        await fetchWishlistGroups();
        setShowCreateModal(false);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create wishlist group');
      }
    } catch (error) {
      console.error('Failed to create wishlist group:', error);
      setError('Failed to create wishlist group');
    }
  };

  const handleDeleteGroup = async (groupId: number) => {
    if (!confirm('Are you sure you want to delete this wishlist group? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/wishlist-groups/${groupId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (response.ok) {
        await fetchWishlistGroups();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete wishlist group');
      }
    } catch (error) {
      console.error('Failed to delete wishlist group:', error);
      setError('Failed to delete wishlist group');
    }
  };

  if (!user) {
    return (
      <LoginPrompt
        title="Access Your Wishlists"
        description="Sign in to view and manage your wishlist groups"
        icon={
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        }
        primaryColor="bg-blue-600"
        primaryColorHover="hover:bg-blue-700"
        linkColor="text-blue-600"
        linkColorHover="hover:text-blue-700"
      />
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Hi, {user.first_name || user.email}</h1>
            <p className="text-gray-600 mt-1">Your wishlists</p>
          </div>
          <div className="flex space-x-4">
            <Button
              onClick={() => window.location.href = '/products'}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>Find Products</span>
            </Button>
            <Button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>Add</span>
            </Button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
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
                <button
                  onClick={() => setError(null)}
                  className="inline-flex text-red-400 hover:text-red-600"
                >
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Wishlist Groups Grid */}
        {wishlistGroups.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No wishlists</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating your first wishlist.</p>
            <div className="mt-6">
              <Button onClick={() => setShowCreateModal(true)}>
                Create Wishlist
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {wishlistGroups.map((group) => (
              <WishlistGroupCard
                key={group.id}
                group={group}
                onDelete={handleDeleteGroup}
              />
            ))}
          </div>
        )}

        {/* Floating Add Button */}
        <button
          onClick={() => setShowCreateModal(true)}
          className="fixed bottom-6 right-6 bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>

        {/* Create Wishlist Group Modal */}
        {showCreateModal && (
          <CreateWishlistGroupModal
            onClose={() => setShowCreateModal(false)}
            onCreate={handleCreateGroup}
          />
        )}
      </div>
    </div>
  );
};

export default WishlistGroupsPage; 