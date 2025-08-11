import { useNavigate } from 'react-router-dom';
import NavbarBefore from '../components/navigation/NavbarBefore';
import { PricingSection } from '../features/pricing/PricingSection';

const LandingPage = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-white overflow-y-scrollbar-gutter-stable">
      <NavbarBefore />
      {/* Hero Section */}
      <section className="text-center px-6 py-20 max-w-3xl mx-auto">
        <div className="mb-6">
          <span className="text-sm px-4 py-1 rounded-full border border-blue-600 text-blue-600">
            more analysis features coming soon
          </span>
        </div>
        <h1 className="text-4xl font-bold mb-6">
          The Easiest Way to Find Foods That <br /> Meet the Standard.
        </h1>
        <p className="text-gray-600 mb-8">
          Quickly search, compare, and select food products that align with nutrition guidelines —
          built for restaurants, distributors, retailers, and manufacturers.
        </p>
        <button 
          onClick={() => navigate('/pricing')}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Get it now
        </button>
      </section>

      {/* Summary Paragraph */}
      <section className="text-center text-gray-500 px-6 py-16 bg-gray-50">
        <div className="max-w-2xl mx-auto">
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
            labore et dolore magna aliqua. Lorem ipsum dolor sit amet.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-20 max-w-6xl mx-auto text-center">
        <h2 className="text-2xl font-semibold mb-6">Quicker analysis</h2>
        <p className="text-gray-600 mb-12 max-w-3xl mx-auto">
          Comparing doesn't have to be hard. We offer a range of USDA-approved guidelines to compare
          the food products against.
        </p>
        <img src="comparison1.png" alt="Product Comparison" className="mx-auto mb-20" />

        <h2 className="text-2xl font-semibold mb-6">Team collaboration</h2>
        <p className="text-gray-600 mb-12 max-w-3xl mx-auto">
          Edit food lists whenever and wherever. We offer team collaboration to edit and make lists together.
        </p>
        <img src="collab.png" alt="Team Collaboration" className="mx-auto" />
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white">
        <PricingSection />
      </section>

      {/* Footer Placeholder */}
      <footer className="bg-gray-100 px-6 py-16 text-sm text-gray-500 text-center">
        <p className="font-semibold mb-2">Mendon Group Food Intelligence Platform</p>
        <p>Mendon Group. 2025. All rights reserved</p>
        <div className="flex justify-center gap-4 mt-2 flex-wrap">
          <a href="#">Terms of use</a>
          <a href="#">Privacy Policy</a>
          <a href="#">Cookie settings</a>
          <a href="#">About Us</a>
          <a href="#">Customer Reviews</a>
          <a href="#">Careers</a>
          <a href="#">FAQ</a>
          <a href="#">Contact Us</a>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
