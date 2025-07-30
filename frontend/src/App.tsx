// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { CartWishlistProvider } from './contexts/CartWishlistContext';
import AuthLandingPage from './pages/auth/AuthLandingPage';
import LoginPage from './pages/auth/LoginPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import PricingPage from './pages/info/PricingPage';
import ResourcesPage from './pages/info/ResourcesPage';
import ContactPage from './pages/info/ContactPage';
import LandingPage from './pages/LandingPage';
import SignupPage from './pages/auth/SignupPage';
import HomePage from './pages/HomePage';
import WishlistPage from './pages/wishlist/WishlistPage';
import WishlistDetailPage from './pages/wishlist/WishlistDetailPage';
import CartPage from './pages/cart/CartPage';
import UserProfilePage from './pages/profile/UserProfilePage';
import CartDetailPage from './pages/cart/CartDetailPage';
import CorporateProfilePage from './pages/profile/CorporateProfilePage';
import SubscriptionPage from './pages/checkout/SubscriptionPage';
import { MagicLinkVerificationPage } from './pages/auth/MagicLinkVerificationPage';
import { GoogleOAuthPage } from './pages/auth/GoogleOAuthPage';

const App = () => {
  return (
    <AuthProvider>
      <CartWishlistProvider>
        <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route path="/auth" element={<AuthLandingPage />} />

        {/* Authentication Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/auth/verify" element={<MagicLinkVerificationPage />} />
        <Route path="/login/google" element={<GoogleOAuthPage />} />

        {/* Info Pages */}
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/contact" element={<ContactPage />} />

        {/* App Routes */}
        <Route path="/products" element={<HomePage />} />
        <Route path="/wishlist" element={<WishlistPage />} />
        <Route path="/wishlist/:id" element={<WishlistDetailPage />} />
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

export default App;
