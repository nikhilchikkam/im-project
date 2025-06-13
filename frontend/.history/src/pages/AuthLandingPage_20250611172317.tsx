import { useState } from 'react';
import NavbarBefore from '../components/NavbarBefore';
import NavbarAfter from '../components/NavbarAfter';
import { Button } from '../components/Button';
import { PricingSection } from '../features/pricing/PricingSection';
import { Link } from 'react-router-dom';

const AuthLandingPage = () => {
  const [section, setSection] = useState<'products' | 'pricing' | 'resources'>('products');
  const isLoggedIn = false; // replace with actual auth logic

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      {isLoggedIn ? (
        <NavbarAfter />
      ) : (
        <NavbarBefore onNavigate={(target) => setSection(target)} />
      )}

      {/* Section Toggle */}
      <main className="flex-grow">
        {section === 'products' && (
          <section className="text-center px-6 py-20">
            <h1 className="text-4xl font-bold mb-4">The Easiest Way to Find Foods That Meet the Standard.</h1>
            <p className="text-gray-600 max-w-2xl mx-auto mb-6">
              Quickly search, compare, and select food products that align with nutrition guidelines — built for restaurants, distributors, retailers, and manufacturers.
            </p>
            <Button>Get it now</Button>

            {!isLoggedIn && (
              <div className="mt-16 flex flex-col md:flex-row justify-center items-center gap-12">
                <div className="bg-blue-50 p-8 rounded-xl text-center w-80">
                  <h2 className="text-lg font-medium mb-6">Returning User? Login</h2>
                  <Link to="/login" className="w-full block">
                    <Button variant="outline" className="w-full">Login</Button>
                  </Link>
                </div>
                <div className="hidden md:block h-48 w-px bg-gray-300" />
                <div className="text-center w-80">
                  <h2 className="text-lg font-medium mb-6">New User? Create an account</h2>
                  <Link to="/signup" className="w-full block">
                    <Button className="w-full">Signup</Button>
                  </Link>
                </div>
              </div>
            )}
          </section>
        )}

        {section === 'pricing' && <PricingSection />}

        {section === 'resources' && (
          <section className="text-center px-6 py-20 text-gray-600">
            <h2 className="text-2xl font-bold mb-4">Resources</h2>
            <p>Resources and guidelines will be shared here soon.</p>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-100 px-6 py-12 text-sm text-gray-600 text-center">
        <h3 className="text-lg font-semibold mb-2">Contact Us</h3>
        <p>Need help? Reach out via email or check our FAQ.</p>
        <div className="flex justify-center mt-4 gap-6 flex-wrap text-sm">
          <a href="#">FAQ</a>
          <a href="#">Careers</a>
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
          <a href="#">Contact Support</a>
        </div>
      </footer>
    </div>
  );
};

export default AuthLandingPage;
