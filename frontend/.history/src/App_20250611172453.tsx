// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import AuthLandingPage from './pages/AuthLandingPage';
import LoginPage from './pages/LoginPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ProductsPage from './pages/ProductsPage';
import PricingPage from './pages/PricingPage';
import ResourcesPage from './pages/ResourcesPage';
import ContactPage from './pages/ContactPage';
// import SignupPage from './pages/SignupPage'; // Enable when needed

const App = () => {
  return (
    <Routes>
      {/* 👇 Main entry point */}
      <Route path="/" element={<AuthLandingPage />} />

      {/* 👇 Auth pages */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      {/* <Route path="/signup" element={<SignupPage />} /> */}

      {/* 👇 Standalone routes if needed */}
      <Route path="/products" element={<ProductsPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/resources" element={<ResourcesPage />} />
      <Route path="/contact" element={<ContactPage />} />
    </Routes>
  );
};

export default App;
