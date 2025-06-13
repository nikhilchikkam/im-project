// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import NavbarBefore from './components/NavbarBefore';

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
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        {/* Add this when SignUp is ready */}
        {/* <Route path="/signup" element={<SignupPage />} /> */}
      </Routes>
    </>
  );
};

export default App;
