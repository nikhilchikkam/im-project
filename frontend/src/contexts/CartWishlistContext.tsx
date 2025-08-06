import React, { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { useAuth, useAuthenticatedFetch } from './AuthContext';

// Helper function for better error handling
const handleApiError = async (response: Response, defaultMessage: string): Promise<string> => {
  let errorMessage = defaultMessage;
  try {
    const errorData = await response.json();
    errorMessage = errorData.detail || errorData.message || errorMessage;
  } catch (parseError) {
    // If response is not JSON, try to get text
    try {
      const errorText = await response.text();
      errorMessage = errorText || errorMessage;
    } catch (textError) {
      // If all else fails, use status text
      errorMessage = response.statusText || errorMessage;
    }
  }
  return errorMessage;
};

interface CartItem {
  id: number;
  gtin: string;
  quantity: number;
  added_at: string;
  product: {
    name: string;
    normalized_name?: string;
    image_urls: string[] | null;
    product_type: string;
    description: string;
  };
}

interface WishlistItem {
  id: number;
  gtin: string;
  added_at: string;
  group_id?: number | null;
  groups?: { id: number; name: string }[];
  product: {
    name: string;
    normalized_name?: string;
    image_urls: string[] | null;
    product_type: string;
    family_title?: string;
    description: string;
    is_smart_snack: boolean | null;
    nova_label: string | null;
    is_good_choice: string | null;
  };
}

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
  user_role: string;
}

interface CartWishlistContextType {
  cartItems: CartItem[];
  wishlistItems: WishlistItem[];
  wishlistGroups: WishlistGroup[];
  cartCount: number;
  wishlistCount: number;
  loading: boolean;
  addToCart: (gtin: string, quantity?: number) => Promise<void>;
  removeFromCart: (gtin: string) => Promise<void>;
  updateCartQuantity: (gtin: string, quantity: number) => Promise<void>;
  clearCart: () => Promise<void>;
  addToWishlist: (gtin: string) => Promise<void>;
  removeFromWishlist: (gtin: string) => Promise<any>;
  clearWishlist: () => Promise<void>;
  isInCart: (gtin: string) => boolean;
  isInWishlist: (gtin: string) => boolean;
  getCartQuantity: (gtin: string) => number;
  refreshCart: () => Promise<void>;
  refreshWishlist: () => Promise<void>;
  // Wishlist Groups functions
  fetchWishlistGroups: () => Promise<void>;
  createWishlistGroup: (name: string, description?: string, isPublic?: boolean) => Promise<WishlistGroup | null>;
  updateWishlistGroup: (groupId: number, name?: string, description?: string, isPublic?: boolean) => Promise<boolean>;
  deleteWishlistGroup: (groupId: number) => Promise<boolean>;
  addItemsToGroup: (groupId: number, gtins: string[]) => Promise<boolean>;
}

const CartWishlistContext = createContext<CartWishlistContextType | undefined>(undefined);

export const useCartWishlist = () => {
  const context = useContext(CartWishlistContext);
  if (context === undefined) {
    throw new Error('useCartWishlist must be used within a CartWishlistProvider');
  }
  return context;
};

interface CartWishlistProviderProps {
  children: ReactNode;
}

export const CartWishlistProvider: React.FC<CartWishlistProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const { authenticatedFetch } = useAuthenticatedFetch();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [wishlistGroups, setWishlistGroups] = useState<WishlistGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  const cartCount = cartItems.reduce((total, item) => total + item.quantity, 0);
  const wishlistCount = wishlistItems.length;

  const refreshCart = useCallback(async () => {
    if (!user) return;

    try {
      const response = await authenticatedFetch('/api/cart');

      if (response.ok) {
        const data = await response.json();
        setCartItems(data.items || []);
      } else {
        console.error('Failed to refresh cart:', response.status);
      }
    } catch (error) {
      console.error('Failed to refresh cart:', error);
    }
  }, [user?.id]);

  const refreshWishlist = useCallback(async () => {
    if (!user) return;

    try {
      const response = await authenticatedFetch('/api/wishlist');

      if (response.ok) {
        const data = await response.json();
        setWishlistItems(data.items || []);
      } else {
        console.error('Failed to refresh wishlist:', response.status);
      }
    } catch (error) {
      console.error('Failed to refresh wishlist:', error);
    }
  }, [user?.id]);

  const addToCart = async (gtin: string, quantity: number = 1) => {
    if (!user) {
      alert('Please log in to add items to cart');
      return;
    }

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/cart/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gtin, quantity }),
      });

      if (response.ok) {
        await refreshCart();
      } else {
        const errorMessage = await handleApiError(response, 'Failed to add to cart');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to add to cart:', error);
      alert('Failed to add to cart');
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (gtin: string) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/cart/remove', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gtin }),
      });

      if (response.ok) {
        await refreshCart();
      } else {
        const errorMessage = await handleApiError(response, 'Failed to remove from cart');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to remove from cart:', error);
      alert('Failed to remove from cart');
    } finally {
      setLoading(false);
    }
  };

  const updateCartQuantity = async (gtin: string, quantity: number) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/cart/update', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gtin, quantity }),
      });

      if (response.ok) {
        await refreshCart();
      } else {
        const errorMessage = await handleApiError(response, 'Failed to update cart quantity');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to update cart quantity:', error);
      alert('Failed to update cart quantity');
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/cart/clear', {
        method: 'DELETE',
      });

      if (response.ok) {
        setCartItems([]);
      } else {
        const errorMessage = await handleApiError(response, 'Failed to clear cart');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to clear cart:', error);
      alert('Failed to clear cart');
    } finally {
      setLoading(false);
    }
  };

  const addToWishlist = async (gtin: string) => {
    if (!user) {
      alert('Please log in to add items to wishlist');
      return;
    }

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/wishlist/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gtin }),
      });

      if (response.ok) {
        await refreshWishlist();
      } else {
        const errorMessage = await handleApiError(response, 'Failed to add to wishlist');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      alert('Failed to add to wishlist');
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (gtin: string) => {
    if (!user) return null;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/wishlist/remove', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gtin }),
      });

      if (response.ok) {
        const data = await response.json();
        await refreshWishlist();
        
        // Return the response data for the caller to handle
        return data;
      } else {
        const errorMessage = await handleApiError(response, 'Failed to remove from wishlist');
        alert(errorMessage);
        return null;
      }
    } catch (error) {
      console.error('Failed to remove from wishlist:', error);
      alert('Failed to remove from wishlist');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const clearWishlist = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/wishlist/clear', {
        method: 'DELETE',
      });

      if (response.ok) {
        setWishlistItems([]);
      } else {
        const errorMessage = await handleApiError(response, 'Failed to clear wishlist');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to clear wishlist:', error);
      alert('Failed to clear wishlist');
    } finally {
      setLoading(false);
    }
  };

  const isInCart = (gtin: string): boolean => {
    return cartItems.some(item => item.gtin === gtin);
  };

  const isInWishlist = (gtin: string): boolean => {
    return wishlistItems.some(item => item.gtin === gtin);
  };

  const getCartQuantity = (gtin: string): number => {
    const item = cartItems.find(item => item.gtin === gtin);
    return item ? item.quantity : 0;
  };

  // Wishlist Groups functions
  const fetchWishlistGroups = useCallback(async () => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/wishlist-groups');

      if (response.ok) {
        const data = await response.json();
        setWishlistGroups(data);
      } else {
        const errorMessage = await handleApiError(response, 'Failed to fetch wishlist groups');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Failed to fetch wishlist groups:', error);
      alert('Failed to fetch wishlist groups');
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const createWishlistGroup = async (
    name: string, 
    description?: string, 
    isPublic: boolean = false
  ): Promise<WishlistGroup | null> => {
    if (!user) return null;

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/wishlist-groups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          description: description?.trim() || null,
          is_public: isPublic
        })
      });

      if (response.ok) {
        const newGroup = await response.json();
        setWishlistGroups(prev => [newGroup, ...prev]);
        return newGroup;
      } else {
        const errorMessage = await handleApiError(response, 'Failed to create wishlist group');
        alert(errorMessage);
        return null;
      }
    } catch (error) {
      console.error('Failed to create wishlist group:', error);
      alert('Failed to create wishlist group');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateWishlistGroup = async (groupId: number, name?: string, description?: string, isPublic?: boolean): Promise<boolean> => {
    if (!user) return false;

    setLoading(true);
    try {
      const updateData: any = {};
      if (name !== undefined) updateData.name = name;
      if (description !== undefined) updateData.description = description;
      if (isPublic !== undefined) updateData.is_public = isPublic;

      const response = await authenticatedFetch(`/api/wishlist-groups/${groupId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (response.ok) {
        await fetchWishlistGroups();
        return true;
      } else {
        const errorMessage = await handleApiError(response, 'Failed to update wishlist group');
        alert(errorMessage);
        return false;
      }
    } catch (error) {
      console.error('Failed to update wishlist group:', error);
      alert('Failed to update wishlist group');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const deleteWishlistGroup = async (groupId: number): Promise<boolean> => {
    if (!user) return false;

    setLoading(true);
    try {
      const response = await authenticatedFetch(`/api/wishlist-groups/${groupId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setWishlistGroups(prev => prev.filter(group => group.id !== groupId));
        return true;
      } else {
        const errorMessage = await handleApiError(response, 'Failed to delete wishlist group');
        alert(errorMessage);
        return false;
      }
    } catch (error) {
      console.error('Failed to delete wishlist group:', error);
      alert('Failed to delete wishlist group');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const addItemsToGroup = async (groupId: number, gtins: string[]): Promise<boolean> => {
    if (!user) return false;

    setLoading(true);
    try {
      const response = await authenticatedFetch(`/api/wishlist-groups/${groupId}/add-items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gtins })
      });

      if (response.ok) {
        // Refresh the groups to update item counts
        await fetchWishlistGroups();
        return true;
      } else {
        const errorMessage = await handleApiError(response, 'Failed to add items to group');
        alert(errorMessage);
        return false;
      }
    } catch (error) {
      console.error('Failed to add items to group:', error);
      alert('Failed to add items to group');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value: CartWishlistContextType = {
    cartItems,
    wishlistItems,
    wishlistGroups,
    cartCount,
    wishlistCount,
    loading,
    addToCart,
    removeFromCart,
    updateCartQuantity,
    clearCart,
    addToWishlist,
    removeFromWishlist,
    clearWishlist,
    isInCart,
    isInWishlist,
    getCartQuantity,
    refreshCart,
    refreshWishlist,
    // Wishlist Groups functions
    fetchWishlistGroups,
    createWishlistGroup,
    updateWishlistGroup,
    deleteWishlistGroup,
    addItemsToGroup,
  };

  useEffect(() => {
    if (user && !isInitialized) {
      refreshCart();
      refreshWishlist();
      fetchWishlistGroups();
      setIsInitialized(true);
    } else if (!user) {
      setCartItems([]);
      setWishlistItems([]);
      setWishlistGroups([]);
      setIsInitialized(false);
    }
  }, [user, isInitialized]);

  return (
    <CartWishlistContext.Provider value={value}>
      {children}
    </CartWishlistContext.Provider>
  );
}; 