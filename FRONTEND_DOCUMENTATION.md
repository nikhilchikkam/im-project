# Frontend Documentation
## Nutrigence React Application

### 📋 Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Technology Stack](#technology-stack)
4. [Component Architecture](#component-architecture)
5. [State Management](#state-management)
6. [Routing & Navigation](#routing--navigation)
7. [Authentication System](#authentication-system)
8. [API Integration](#api-integration)
9. [Performance Optimizations](#performance-optimizations)
10. [Styling & UI](#styling--ui)
11. [Development Workflow](#development-workflow)
12. [Testing & Debugging](#testing--debugging)

---

## Overview

The Nutrigence frontend is a modern React application built with TypeScript, providing an intuitive interface for food product search, comparison, and team collaboration. The application features advanced filtering, wishlist management, and real-time synchronization with the backend.

### 🎯 Key Features
- **Product Search & Filtering**: Advanced search with nutrition-based filters
- **Wishlist Management**: Group-based organization with team collaboration
- **Shopping Cart**: Persistent cart with quantity management
- **User Authentication**: Multiple login methods (email, OAuth, magic links)
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Updates**: Live synchronization with backend data

---

## Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── apple-icon.png
│   ├── auth-bg.png
│   ├── cart.png
│   ├── nutrigence_logo.PNG
│   └── vite.svg
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common/        # Shared components
│   │   │   ├── BulkActionsBar.tsx
│   │   │   ├── LoginPrompt.tsx
│   │   │   └── LoginRequiredModal.tsx
│   │   ├── home/          # Home page components
│   │   │   ├── GuidelineDropdownPortal.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── MobileFilterDrawer.tsx
│   │   │   ├── ProductFilterBar.tsx
│   │   │   ├── ProductResults.tsx
│   │   │   └── ProductSearchBar.tsx
│   │   ├── modals/        # Modal components
│   │   │   ├── DeleteConfirmationModal.tsx
│   │   │   ├── ExportModal.tsx
│   │   │   ├── HierarchyGraph.tsx
│   │   │   ├── HierarchyModal.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── RemoveWishlistItemModal.tsx
│   │   │   ├── ShareModal.tsx
│   │   │   └── UserDetailsModal.tsx
│   │   ├── navigation/    # Navigation components
│   │   │   ├── NavbarAfter.tsx
│   │   │   └── NavbarBefore.tsx
│   │   ├── product/       # Product-related components
│   │   │   ├── NutritionSummaryCard.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   └── ProductTable.tsx
│   │   └── ui/            # Base UI components
│   │       ├── Button.tsx
│   │       ├── DataTable.tsx
│   │       ├── Dropdown.tsx
│   │       ├── Input.tsx
│   │       ├── Pagination.tsx
│   │       ├── Toast.tsx
│   │       ├── TokenRefreshToast.tsx
│   │       └── Toolbar.tsx
│   ├── contexts/          # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── CartWishlistContext.tsx
│   ├── features/          # Feature-specific components
│   │   ├── auth/          # Authentication components
│   │   │   ├── AuthLayout.tsx
│   │   │   ├── ForgotPasswordForm.tsx
│   │   │   ├── LoginForm.tsx
│   │   │   ├── MagicLinkForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── cart/          # Shopping cart components
│   │   │   ├── CartBulkActionsBar.tsx
│   │   │   ├── CartList.tsx
│   │   │   ├── CartTable.tsx
│   │   │   └── CartToolbar.tsx
│   │   ├── pricing/       # Pricing components
│   │   │   ├── PricingCard.tsx
│   │   │   ├── PricingSection.tsx
│   │   │   └── PricingToggle.tsx
│   │   ├── products/      # Product detail components
│   │   │   ├── NutritionFactsCard.tsx
│   │   │   ├── NutritionSummaryCard.tsx
│   │   │   ├── ProductDescription.tsx
│   │   │   ├── ProductDetailsModal.tsx
│   │   │   ├── ProductHeader.tsx
│   │   │   └── ProductTagsSection.tsx
│   │   ├── profile/       # User profile components
│   │   │   ├── InfoCard.tsx
│   │   │   └── ProfileSidebar.tsx
│   │   └── wishlist/      # Wishlist components
│   │       ├── AddToWishlistModal.tsx
│   │       ├── AddWishlistButton.tsx
│   │       ├── EditGroupModal.tsx
│   │       ├── WishlistBulkActionsBar.tsx
│   │       ├── WishlistCard.tsx
│   │       ├── WishlistList.tsx
│   │       ├── WishlistTable.tsx
│   │       └── WishlistToolbar.tsx
│   ├── layouts/           # Layout components
│   │   ├── ProductDetailsLayout.tsx
│   │   └── ProfilePageLayout.tsx
│   ├── pages/             # Page components
│   │   ├── auth/          # Authentication pages
│   │   │   ├── AppleOAuthPage.tsx
│   │   │   ├── AuthLandingPage.tsx
│   │   │   ├── ForgotPasswordPage.tsx
│   │   │   ├── GoogleOAuthPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── MagicLinkVerificationPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   └── VerifyPage.tsx
│   │   ├── cart/          # Cart pages
│   │   │   ├── CartDetailPage.tsx
│   │   │   └── CartPage.tsx
│   │   ├── checkout/      # Checkout pages
│   │   │   └── SubscriptionPage.tsx
│   │   ├── info/          # Static pages
│   │   │   ├── ContactPage.tsx
│   │   │   ├── PricingPage.tsx
│   │   │   └── ResourcesPage.tsx
│   │   ├── profile/       # Profile pages
│   │   │   ├── CorporateProfilePage.tsx
│   │   │   ├── ManagePurchasesPage.tsx
│   │   │   └── UserProfilePage.tsx
│   │   ├── wishlist/      # Wishlist pages
│   │   │   ├── WishlistGroupDetailPage.tsx
│   │   │   ├── WishlistGroupsPage.tsx
│   │   │   └── WishlistPage.tsx
│   │   ├── HomePage.tsx
│   │   ├── HomePageNuts.tsx
│   │   ├── LandingPage.tsx
│   │   └── ProductHuntPage.tsx
│   ├── utils/             # Utility functions
│   │   ├── authUtils.ts
│   │   └── fetchInterceptor.ts
│   ├── App.css
│   ├── App.tsx            # Main application component
│   ├── index.css
│   └── main.tsx           # Application entry point
├── .env.production        # Production environment variables
├── eslint.config.js       # ESLint configuration
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── postcss.config.js      # PostCSS configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite build configuration
```

---

## Technology Stack

### 🛠️ Core Technologies
- **React**: 19.1.0 - Modern React with hooks and functional components
- **TypeScript**: ~5.8.3 - Type safety and better developer experience
- **Vite**: 6.3.5 - Fast build tool and development server
- **React Router**: 7.6.2 - Client-side routing

### 🎨 Styling & UI
- **Tailwind CSS**: 3.4.1 - Utility-first CSS framework
- **Lucide React**: 0.514.0 - Modern icon library
- **Embla Carousel**: 8.6.0 - Touch-friendly carousel component
- **CLSX**: 2.1.1 - Conditional className utility

### 📊 Data Visualization
- **D3.js**: 3.1.2 - Data visualization for hierarchy graphs
- **Neovis.js**: 2.1.0 - Neo4j graph visualization

### 🚀 Development Tools
- **ESLint**: 9.25.0 - Code linting and formatting
- **PostCSS**: 8.5.4 - CSS processing
- **Autoprefixer**: 10.4.21 - CSS vendor prefixing

---

## Component Architecture

### 🏗️ Component Patterns

#### 1. Functional Components with Hooks
All components use modern React patterns with functional components and hooks:

```typescript
// Example: ProductCard.tsx
const ProductCard: React.FC<ProductCardProps> = ({
  upc,
  title,
  normalized_name,
  name,
  category,
  description,
  isSmartSnack,
  novaLabel,
  isGoodChoice,
  imageUrl,
  imageUrls,
  onFavorite,
  onAddToCart,
  onEnlarge,
  onHierarchy,
  onRemove,
  isSelected,
  onSelect,
  showCheckbox,
  className,
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());
  const { addToCart, addToWishlist, isInCart, isInWishlist } = useCartWishlist();
  
  // Component logic here...
  
  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      {/* Component JSX */}
    </div>
  );
};
```

#### 2. Props Interface Definition
Strong TypeScript typing for all component props:

```typescript
interface ProductCardProps {
  upc: string;
  title?: string;
  normalized_name?: string;
  name?: string;
  category?: string;
  description?: string;
  isSmartSnack?: boolean;
  novaLabel?: string;
  isGoodChoice?: string;
  imageUrl?: string;
  imageUrls?: string[] | { [key: string]: string[] };
  onFavorite?: () => void;
  onAddToCart?: () => void;
  onEnlarge?: () => void;
  onHierarchy?: () => void;
  onRemove?: () => void;
  isSelected?: boolean;
  onSelect?: () => void;
  showCheckbox?: boolean;
  className?: string;
}
```

#### 3. Component Composition
Building complex UIs from simple, reusable components:

```typescript
// Example: HomePage composition
const HomePage = () => {
  return (
    <div>
      <NavbarAfter />
      <ProductFilterBar />
      <ProductResults 
        products={products}
        loading={loading}
        viewType={viewType}
      />
      <Pagination />
    </div>
  );
};
```

### 🎯 Component Categories

#### Common Components
- **BulkActionsBar**: Bulk operations for cart/wishlist items
- **LoginPrompt**: Authentication prompts for protected features
- **LoginRequiredModal**: Modal for login requirements

#### Home Page Components
- **ProductFilterBar**: Advanced filtering interface
- **ProductResults**: Product display with card/table views
- **ProductSearchBar**: Search functionality with debouncing
- **MobileFilterDrawer**: Mobile-optimized filter interface

#### Modal Components
- **DeleteConfirmationModal**: Confirmation dialogs
- **ExportModal**: Data export functionality
- **HierarchyGraph**: Product hierarchy visualization
- **ShareModal**: Sharing functionality

#### UI Components
- **Button**: Reusable button component with variants
- **Input**: Form input component
- **Dropdown**: Dropdown menu component
- **Pagination**: Pagination controls
- **Toast**: Notification system

---

## State Management

### 🔄 Context API Implementation

#### AuthContext
Global authentication state management:

```typescript
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (accessToken: string, refreshToken: string, userData: User) => void;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
  isTokenExpired: (token: string) => boolean;
  startAutoRefresh: () => void;
  stopAutoRefresh: () => void;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefreshInterval, setAutoRefreshInterval] = useState<number | null>(null);
  
  // Complex authentication logic
  const login = (accessToken: string, refreshToken: string, userData: User) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setUser(userData);
    setTimeout(() => startAutoRefresh(), 1000);
  };
  
  // ... other methods
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### CartWishlistContext
Shopping functionality state management:

```typescript
interface CartWishlistContextType {
  cartItems: CartItem[];
  wishlistItems: WishlistItem[];
  wishlistGroups: WishlistGroup[];
  cartCount: number;
  wishlistCount: number;
  loading: boolean;
  addToCart: (gtin: string, quantity?: number) => Promise<void>;
  removeFromCart: (gtin: string) => Promise<void>;
  addToWishlist: (gtin: string) => Promise<void>;
  removeFromWishlist: (gtin: string) => Promise<any>;
  // ... more methods
}
```

### 📊 Local State Management

#### Component State
```typescript
// Example: HomePage state management
const HomePage = () => {
  // UI State
  const [showFilters, setShowFilters] = useState(false);
  const [viewType, setViewType] = useState<'card' | 'list'>('card');
  const [showGuidelineDropdown, setShowGuidelineDropdown] = useState(false);
  const [showMobileFilter, setShowMobileFilter] = useState(false);
  
  // Data State
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filter State
  const [selectedCategories, setSelectedCategories] = useState<string[]>(categories.slice());
  const [selectedGuidelines, setSelectedGuidelines] = useState<string[]>([]);
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Pagination State
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [total, setTotal] = useState(0);
  
  // Selection State
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);
};
```

---

## Routing & Navigation

### 🗺️ Route Configuration

#### App.tsx Route Structure
```typescript
const App = () => {
  return (
    <AuthProvider>
      <CartWishlistProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/product-hunt" element={<ProductHuntPage />} />
          <Route path="/auth" element={<AuthLandingPage />} />
          
          {/* Authentication Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/auth/verify" element={<MagicLinkVerificationPage />} />
          <Route path="/auth/google" element={<GoogleOAuthPage />} />
          <Route path="/login/apple" element={<AppleOAuthPage />} />
          
          {/* Info Pages */}
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/contact" element={<ContactPage />} />
          
          {/* App Routes */}
          <Route path="/products" element={<HomePage />} />
          <Route path="/products-nuts" element={<HomePageNuts />} />
          <Route path="/wishlist" element={<WishlistPage />} />
          <Route path="/wishlist-groups" element={<WishlistGroupsPage />} />
          <Route path="/wishlist-groups/:groupId" element={<WishlistGroupDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/cart/detail" element={<CartDetailPage />} />
          <Route path="/profile" element={<UserProfilePage />} />
          <Route path="/profile/corporate" element={<CorporateProfilePage />} />
          <Route path="/subscription" element={<SubscriptionPage />} />
        </Routes>
      </CartWishlistProvider>
    </AuthProvider>
  );
};
```

### 🔐 Protected Routes

#### Authentication-Based Routing
```typescript
const WishlistPage = () => {
  const { user } = useAuth();
  
  if (!user) {
    return (
      <LoginPrompt
        title="Sign in to view wishlist"
        description="You need to be logged in to view your wishlist"
        icon="❤️"
        primaryColor="red"
        primaryColorHover="red"
        linkColor="red"
        linkColorHover="red"
      />
    );
  }
  
  return (
    // Wishlist content
  );
};
```

### 🧭 Navigation Hooks

#### useNavigate
```typescript
const navigate = useNavigate();

// Simple navigation
navigate('/pricing');

// Navigation with state
navigate('/wishlist', { state: { from: 'products' } });

// Conditional navigation
navigate(isNutsVersion ? '/products' : '/products-nuts');
```

#### useSearchParams
```typescript
const [searchParams] = useSearchParams();

// Reading parameters
const tab = searchParams.get('tab');
const token = searchParams.get('token');

// Setting parameters
const newSearchParams = new URLSearchParams(searchParams);
newSearchParams.set('tab', 'groups');
navigate(`?${newSearchParams.toString()}`);
```

---

## Authentication System

### 🔐 Authentication Methods

#### 1. Email/Password Login
Traditional login with JWT tokens:
```typescript
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (response.ok) {
      const data = await response.json();
      login(data.access_token, data.refresh_token, data.user);
      navigate('/products');
    }
  } catch (error) {
    setError('Login failed');
  }
};
```

#### 2. Magic Link Authentication
Passwordless authentication via email:
```typescript
const handleMagicLink = async (email: string) => {
  try {
    const response = await fetch('/api/auth/magic-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    
    if (response.ok) {
      setMessage('Magic link sent to your email');
    }
  } catch (error) {
    setError('Failed to send magic link');
  }
};
```

#### 3. OAuth Integration
Google and Apple OAuth:
```typescript
const handleGoogleOAuth = () => {
  window.location.href = '/api/auth/google/url';
};

const handleAppleOAuth = () => {
  window.location.href = '/api/auth/apple/url';
};
```

### 🔄 Token Management

#### Automatic Token Refresh
```typescript
const refreshAccessToken = useCallback(async (): Promise<boolean> => {
  const now = Date.now();
  if (now - lastRefreshAttemptRef.current < REFRESH_COOLDOWN) {
    return false;
  }
  
  lastRefreshAttemptRef.current = now;
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(`${apiUrl}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('refreshToken', data.refresh_token);
      }
      return true;
    } else {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      return false;
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
}, []);
```

#### Token Expiration Check
```typescript
const isTokenExpired = useCallback((token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp;
    // Add 30 second buffer to refresh before actual expiration
    return Date.now() >= (exp * 1000) - 30000;
  } catch (e) {
    return true; // Assume expired if parsing fails
  }
}, []);
```

---

## API Integration

### 🌐 API Configuration

#### Environment Variables
```typescript
// .env.production
VITE_API_URL=https://nutrigence.app/im-project-backend

// Development
VITE_API_URL=http://localhost:8000
```

#### API Base URL
```typescript
const apiUrl = import.meta.env.VITE_API_URL || '';
```

### 🔧 Authenticated Fetch

#### useAuthenticatedFetch Hook
```typescript
export const useAuthenticatedFetch = () => {
  const { refreshAccessToken, logout, isTokenExpired } = useAuth();
  const apiUrl = import.meta.env.VITE_API_URL || '';

  const authenticatedFetch = useCallback(async (
    url: string, 
    options: RequestInit = {}
  ): Promise<Response> => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      throw new Error('No access token available');
    }

    // Prepend base URL if url is relative
    const fullUrl = url.startsWith('http') ? url : `${apiUrl}${url}`;

    // Check if token is expired before making the request
    if (isTokenExpired(accessToken)) {
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        logout();
        throw new Error('Token refresh failed');
      }
    }

    // Add authorization header
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    };

    const response = await fetch(fullUrl, {
      ...options,
      headers,
    });

    // If we get a 401, try to refresh the token and retry once
    if (response.status === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry the request with the new token
        const retryHeaders = {
          ...options.headers,
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        };
        const retryResponse = await fetch(fullUrl, {
          ...options,
          headers: retryHeaders,
        });
        return retryResponse;
      } else {
        logout();
        throw new Error('Authentication failed');
      }
    }

    return response;
  }, [refreshAccessToken, logout, isTokenExpired, apiUrl]);

  return { authenticatedFetch };
};
```

### 📡 API Endpoints

#### Products API
```typescript
const fetchProducts = async (params: ProductSearchParams) => {
  const searchParams = new URLSearchParams();
  
  if (params.searchTerm) searchParams.set('search_term', params.searchTerm);
  if (params.classTitle) searchParams.set('class_title', params.classTitle);
  if (params.familyTitle) {
    params.familyTitle.forEach(title => searchParams.append('family_title', title));
  }
  if (params.isSmartSnack !== undefined) searchParams.set('is_smart_snack', params.isSmartSnack.toString());
  if (params.isGoodChoice) searchParams.set('is_good_choice', params.isGoodChoice);
  if (params.recommendedOk) searchParams.set('recommended_ok', params.recommendedOk);
  if (params.limit) searchParams.set('limit', params.limit.toString());
  if (params.offset) searchParams.set('offset', params.offset.toString());
  
  const response = await authenticatedFetch(`/api/products?${searchParams.toString()}`);
  return response.json();
};
```

#### Cart API
```typescript
const addToCart = async (gtin: string, quantity: number = 1) => {
  const response = await authenticatedFetch('/api/cart/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gtin, quantity }),
  });
  return response.json();
};

const getCart = async () => {
  const response = await authenticatedFetch('/api/cart');
  return response.json();
};
```

#### Wishlist API
```typescript
const addToWishlist = async (gtin: string, groupId?: number) => {
  const response = await authenticatedFetch('/api/wishlist/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gtin, group_id: groupId }),
  });
  return response.json();
};

const getWishlist = async () => {
  const response = await authenticatedFetch('/api/wishlist');
  return response.json();
};
```

---

## Performance Optimizations

### ⚡ Memoization Strategies

#### useMemo for Expensive Computations
```typescript
// Image filtering optimization
const workingImages = React.useMemo(() => {
  return finalImages.filter(url => !failedImages.has(url));
}, [finalImages, failedImages]);

// Prevents unnecessary filtering on every render
// Only recalculates when finalImages or failedImages change
```

#### useCallback for Function Stability
```typescript
// Stable function references
const refreshCart = useCallback(async () => {
  if (!user) return;
  try {
    const response = await authenticatedFetch('/api/cart');
    if (response.ok) {
      const data = await response.json();
      setCartItems(data.items || []);
    }
  } catch (error) {
    console.error('Failed to refresh cart:', error);
  }
}, [user?.id]);

// Prevents unnecessary re-renders of child components
// Only recreates function when user.id changes
```

### 🔄 Debouncing

#### Search Input Debouncing
```typescript
useEffect(() => {
  const handler = setTimeout(() => {
    setSearchTerm(searchInput);
    setPage(1);
  }, 400);
  return () => clearTimeout(handler);
}, [searchInput]);

// Prevents excessive API calls while typing
// Waits 400ms after user stops typing before searching
```

### 🖼️ Image Optimization

#### Lazy Loading and Error Handling
```typescript
const handleImageError = (imageUrl: string) => {
  setFailedImages(prev => new Set([...prev, imageUrl]));
};

// Uses functional state update to avoid stale closures
// Prevents unnecessary re-renders
```

### 📦 Code Splitting

#### Route-Based Code Splitting
```typescript
// Lazy load components for better performance
const ProductDetailsModal = React.lazy(() => import('./ProductDetailsModal'));
const HierarchyModal = React.lazy(() => import('./HierarchyModal'));
```

---

## Styling & UI

### 🎨 Tailwind CSS Integration

#### Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
}
```

#### Component Styling
```typescript
// Example: Button component with variants
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  disabled = false,
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`;
  
  return (
    <button className={classes} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
};
```

### 📱 Responsive Design

#### Mobile-First Approach
```typescript
// Example: Responsive product grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {products.map(product => (
    <ProductCard key={product.gtin} {...product} />
  ))}
</div>
```

#### Mobile Filter Drawer
```typescript
const MobileFilterDrawer = () => {
  return (
    <div className="lg:hidden">
      <button
        onClick={() => setShowMobileFilter(true)}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-md"
      >
        <Filter className="w-4 h-4" />
        <span>Filters</span>
      </button>
      
      {/* Mobile filter drawer */}
      {showMobileFilter && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Drawer content */}
        </div>
      )}
    </div>
  );
};
```

---

## Development Workflow

### 🛠️ Local Development Setup

#### Prerequisites
- Node.js 20.x
- npm or yarn package manager

#### Installation
```bash
cd frontend
npm install
```

#### Development Server
```bash
npm run dev
```
- Starts development server at `http://localhost:5173`
- Hot module replacement enabled
- TypeScript compilation on save

#### Build Commands
```bash
# Development build
npm run build

# Production build
npm run build

# Preview production build
npm run preview

# Start production server
npm start
```

### 🔧 Development Scripts

#### package.json Scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview",
    "start": "serve -s dist -l 8080"
  }
}
```

### 📝 Code Standards

#### TypeScript Configuration
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### ESLint Configuration
```javascript
// eslint.config.js
import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2021,
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
];
```

---

## Testing & Debugging

### 🐛 Debugging Tools

#### React DevTools
- **Component Inspector**: Inspect component hierarchy and props
- **State Debugger**: Monitor component state changes
- **Profiler**: Performance analysis and optimization

#### Browser DevTools
- **Network Tab**: Monitor API calls and responses
- **Console**: Error logging and debugging
- **Application Tab**: Local storage and session management

#### VS Code Extensions
- **ES7+ React/Redux/React-Native snippets**
- **TypeScript Importer**
- **Tailwind CSS IntelliSense**
- **ESLint**

### 🔍 Common Debugging Scenarios

#### Authentication Issues
```typescript
// Debug token expiration
const debugToken = (token: string) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    console.log('Token payload:', payload);
    console.log('Expiration:', new Date(payload.exp * 1000));
    console.log('Is expired:', isTokenExpired(token));
  } catch (e) {
    console.error('Invalid token:', e);
  }
};
```

#### API Call Debugging
```typescript
// Debug API calls
const debugApiCall = async (url: string, options: RequestInit) => {
  console.log('API Call:', { url, options });
  
  try {
    const response = await fetch(url, options);
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    const data = await response.json();
    console.log('Response data:', data);
    
    return response;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

### 📊 Performance Monitoring

#### Bundle Analysis
```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer dist
```

#### Performance Metrics
```typescript
// Monitor component render performance
const useRenderCount = (componentName: string) => {
  const renderCount = useRef(0);
  renderCount.current += 1;
  
  useEffect(() => {
    console.log(`${componentName} rendered ${renderCount.current} times`);
  });
};
```

---

## 🎯 Key Takeaways

### 🏗️ Architecture Excellence
1. **Modern React Patterns**: 100% functional components with hooks
2. **Type Safety**: Comprehensive TypeScript integration
3. **Performance Optimized**: Strategic use of memoization and debouncing
4. **Scalable Design**: Modular component architecture

### 🔧 Technical Implementation
1. **State Management**: Efficient Context API usage
2. **Authentication**: Robust JWT token management with auto-refresh
3. **API Integration**: Automatic token handling and error recovery
4. **UI/UX**: Responsive design with Tailwind CSS

### 📈 Performance Features
1. **Code Splitting**: Route-based lazy loading
2. **Image Optimization**: Lazy loading and error handling
3. **Debouncing**: Search input optimization
4. **Memoization**: Expensive computation optimization

### 🚀 Development Experience
1. **Hot Reload**: Fast development with Vite
2. **Type Safety**: Comprehensive TypeScript integration
3. **Code Quality**: ESLint and Prettier integration
4. **Debugging**: Excellent debugging tools and practices

---

*This frontend documentation provides a comprehensive overview of the React application architecture, implementation details, and development practices. For specific component details, refer to the individual component files and their inline documentation.*

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: Frontend Development Team
