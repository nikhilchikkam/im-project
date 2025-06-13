// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import NavbarBefore from './components/NavbarBefore';
import AuthLanding from './pages/AuthLandingPage';
import PricingPage from './pages/PricingPage'; 
import ProductsPage from './pages/ProductsPage'; 
import ResourcesPage from './pages/ResourcesPage'; 
import ContactPage from './pages/ContactPage'; 

const App = () => {
  return (
    <>
      <Routes>
        <Route path="/" element={
          <>
            <NavbarBefore />
            <main className="p-6">Welcome to Nutrigence 👋</main>
          </>
        } />
        <Route path="/auth" element={<AuthLanding />} />

        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/contact" element={<ContactPage />} />
        {/* Add this when SignUp is ready */}
        {/* <Route path="/signup" element={<SignupPage />} /> */}
      </Routes>
    </>
  );
};

export default App;
