// src/App.tsx
import { Routes, Route } from 'react-router-dom';
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

const App = () => {
  return (
    <Routes>
      
      <Route path="/" element={<LandingPage />} />

      <Route path="/auth" element={<AuthLandingPage />} />

      
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/signup" element={<SignupPage />} />

      
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/resources" element={<ResourcesPage />} />
      <Route path="/contact" element={<ContactPage />} />

      <Route path="/home" element={<HomePage />} />
      <Route path="/wishlist" element={<WishlistPage />} />
      <Route path="/wishlist/:id" element={<WishlistDetailPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/cart/detail" element={<CartDetailPage />} />
      <Route path="/profile" element={<UserProfilePage />} />
      <Route path="/profile/corporate" element={<CorporateProfilePage />} />
      <Route path="/subscription" element={<SubscriptionPage />} />
    </Routes>
  );
};

export default App;
