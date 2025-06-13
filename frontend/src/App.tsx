// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import AuthLandingPage from './pages/AuthLandingPage';
import LoginPage from './pages/LoginPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ProductsPage from './pages/LandingPage';
import PricingPage from './pages/PricingPage';
import ResourcesPage from './pages/ResourcesPage';
import ContactPage from './pages/ContactPage';
import LandingPage from './pages/LandingPage';
import SignupPage from './pages/SignupPage';
import HomePage from './pages/HomePage';
import WishlistPage from './pages/WishlistPage';
import WishlistDetailPage from './pages/WishlistDetailPage';
import CartPage from './pages/CartPage';
import UserProfilePage from './pages/UserProfilePage';
// import SignupPage from './pages/SignupPage'; // Enable when needed

const App = () => {
  return (
    <Routes>
      
      <Route path="/" element={<LandingPage />} />

      <Route path="/auth" element={<AuthLandingPage />} />

      
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/signup" element={<SignupPage />} />

      
      <Route path="/products" element={<ProductsPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/resources" element={<ResourcesPage />} />
      <Route path="/contact" element={<ContactPage />} />

      <Route path="/home" element={<HomePage />} />
      <Route path="/wishlist" element={<WishlistPage />} />
      <Route path="/wishlist/:id" element={<WishlistDetailPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/profile" element={<UserProfilePage />} />
    </Routes>
  );
};

export default App;
