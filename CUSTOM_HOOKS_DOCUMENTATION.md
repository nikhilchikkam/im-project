# Custom Hooks Documentation

This document provides a comprehensive overview of all custom hooks used in the Nutrigence frontend application.

## Overview

The Nutrigence frontend uses several custom hooks to manage state, authentication, and API interactions. These hooks are built on top of React's built-in hooks and provide a clean, reusable interface for common functionality.

## 🔐 Authentication Hooks

### `useAuth()`

**Location**: `frontend/src/contexts/AuthContext.tsx`

**Purpose**: Provides authentication state and methods throughout the application.

**Returns**:
```typescript
{
  user: User | null;
  loading: boolean;
  login: (accessToken: string, refreshToken: string, userData: User) => void;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
  isTokenExpired: (token: string) => boolean;
  startAutoRefresh: () => void;
  stopAutoRefresh: () => void;
}
```

**Usage Example**:
```typescript
const { user, login, logout, loading } = useAuth();

if (loading) {
  return <div>Loading...</div>;
}

if (!user) {
  return <LoginForm />;
}
```

**Key Features**:
- Automatic token refresh
- User session management
- JWT token validation
- Auto-refresh timer management

### `useAuthenticatedFetch()`

**Location**: `frontend/src/contexts/AuthContext.tsx`

**Purpose**: Provides a fetch wrapper that automatically handles authentication headers and token refresh.

**Returns**:
```typescript
{
  authenticatedFetch: (url: string, options?: RequestInit) => Promise<Response>;
}
```

**Usage Example**:
```typescript
const { authenticatedFetch } = useAuthenticatedFetch();

const fetchUserData = async () => {
  try {
    const response = await authenticatedFetch('/api/user/profile');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to fetch user data:', error);
  }
};
```

**Key Features**:
- Automatic token inclusion in headers
- Token expiration checking
- Automatic token refresh on 401 errors
- Retry mechanism for failed requests

## 🛒 Cart & Wishlist Hooks

### `useCartWishlist()`

**Location**: `frontend/src/contexts/CartWishlistContext.tsx`

**Purpose**: Manages cart and wishlist state and operations.

**Returns**:
```typescript
{
  // Cart operations
  cartItems: CartItem[];
  cartCount: number;
  addToCart: (gtin: string, quantity?: number) => Promise<boolean>;
  removeFromCart: (gtin: string) => Promise<boolean>;
  updateCartQuantity: (gtin: string, quantity: number) => Promise<boolean>;
  clearCart: () => Promise<boolean>;
  refreshCart: () => Promise<void>;
  
  // Wishlist operations
  wishlistItems: WishlistItem[];
  wishlistCount: number;
  addToWishlist: (gtin: string) => Promise<boolean>;
  removeFromWishlist: (gtin: string) => Promise<boolean>;
  clearWishlist: () => Promise<boolean>;
  refreshWishlist: () => Promise<void>;
  
  // Wishlist groups
  wishlistGroups: WishlistGroup[];
  createWishlistGroup: (name: string, description?: string) => Promise<boolean>;
  updateWishlistGroup: (groupId: number, name: string, description?: string) => Promise<boolean>;
  deleteWishlistGroup: (groupId: number) => Promise<boolean>;
  addItemsToGroup: (groupId: number, gtins: string[]) => Promise<boolean>;
  
  // State
  loading: boolean;
  isInitialized: boolean;
}
```

**Usage Example**:
```typescript
const { 
  cartItems, 
  addToCart, 
  wishlistItems, 
  addToWishlist,
  loading 
} = useCartWishlist();

const handleAddToCart = async (productId: string) => {
  const success = await addToCart(productId, 1);
  if (success) {
    // Show success message
  }
};
```

**Key Features**:
- Synchronized cart and wishlist state
- Group-based wishlist organization
- Real-time updates across components
- Loading states for operations

## 🔧 Utility Hooks

### Token Management Utilities

**Location**: `frontend/src/utils/authUtils.ts`

**Functions**:
- `isTokenExpired(token: string): boolean` - Checks if JWT token is expired
- `refreshAccessToken(): Promise<boolean>` - Refreshes access token using refresh token
- `authenticatedFetch(url: string, options?: RequestInit): Promise<Response>` - Standalone authenticated fetch

### Fetch Interceptor

**Location**: `frontend/src/utils/fetchInterceptor.ts`

**Purpose**: Global fetch interceptor that automatically handles token refresh for all API calls.

**Features**:
- Intercepts all fetch requests
- Automatically adds authentication headers
- Handles token refresh on 401 errors
- Maintains original fetch behavior for non-API calls

## 🎯 Hook Usage Patterns

### 1. Authentication Flow

```typescript
// In a component that requires authentication
const { user, loading } = useAuth();
const { authenticatedFetch } = useAuthenticatedFetch();

useEffect(() => {
  if (user) {
    // User is authenticated, fetch protected data
    fetchProtectedData();
  }
}, [user]);
```

### 2. Cart/Wishlist Integration

```typescript
// In a product component
const { addToCart, addToWishlist, isInCart, isInWishlist } = useCartWishlist();

const handleAddToCart = () => {
  addToCart(product.gtin);
};

const handleAddToWishlist = () => {
  addToWishlist(product.gtin);
};
```

### 3. API Calls with Authentication

```typescript
// Making authenticated API calls
const { authenticatedFetch } = useAuthenticatedFetch();

const fetchData = async () => {
  try {
    const response = await authenticatedFetch('/api/protected-endpoint');
    const data = await response.json();
    // Handle data
  } catch (error) {
    // Handle error (authentication errors are handled automatically)
  }
};
```

## 🔄 State Management

### Context Providers

The application uses React Context for global state management:

1. **AuthProvider** - Wraps the entire app and provides authentication state
2. **CartWishlistProvider** - Manages cart and wishlist state

### Provider Setup

```typescript
// In App.tsx or main.tsx
function App() {
  return (
    <AuthProvider>
      <CartWishlistProvider>
        {/* Your app components */}
      </CartWishlistProvider>
    </AuthProvider>
  );
}
```

## 🚨 Error Handling

### Authentication Errors

- Token expiration is handled automatically
- 401 errors trigger automatic token refresh
- Failed refresh redirects to login page

### API Errors

- Network errors are caught and logged
- User-friendly error messages are displayed
- Loading states prevent multiple simultaneous requests

## 🔧 Customization

### Adding New Hooks

To add a new custom hook:

1. Create the hook in the appropriate context file or utils directory
2. Export it from the context or utils file
3. Add TypeScript interfaces for return types
4. Document the hook's purpose and usage

### Extending Existing Hooks

Existing hooks can be extended by:
- Adding new methods to the context
- Expanding the return object
- Adding new state variables

## 📝 Best Practices

1. **Always use TypeScript interfaces** for hook return types
2. **Handle loading states** in components using hooks
3. **Use error boundaries** for unexpected errors
4. **Keep hooks focused** on a single responsibility
5. **Document complex logic** with comments
6. **Test hooks** with React Testing Library

## 🔍 Debugging

### Common Issues

1. **Hook called outside provider**: Ensure components are wrapped in the appropriate providers
2. **Token refresh loops**: Check token expiration logic
3. **State not updating**: Verify dependency arrays in useEffect hooks

### Debug Tools

- Use React DevTools to inspect context state
- Check browser network tab for API calls
- Monitor localStorage for token storage
- Use console.log for debugging hook state changes
