import { Link } from 'react-router-dom';
import NavbarBefore from '../components/NavbarBefore';
import { PricingSection } from '../features/pricing/PricingSection';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      <NavbarBefore />
      {/* Hero Section */}
      <section className="text-center px-6 py-16 max-w-3xl mx-auto">
        <div className="mb-4">
          <span className="text-sm px-4 py-1 rounded-full border border-blue-600 text-blue-600">
            more analysis features coming soon
          </span>
        </div>
        <h1 className="text-4xl font-bold mb-4">
          The Easiest Way to Find Foods That <br /> Meet the Standard.
        </h1>
        <p className="text-gray-600 mb-6">
          Quickly search, compare, and select food products that align with nutrition guidelines —
          built for restaurants, distributors, retailers, and manufacturers.
        </p>
        <button className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
          Get it now
        </button>
      </section>

      {/* Summary Paragraph */}
      <div className="text-center text-gray-500 px-6 mb-16">
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
          labore et dolore magna aliqua. Lorem ipsum dolor sit amet.
        </p>
      </div>

      {/* Features Section */}
      <section className="px-6 py-16 max-w-6xl mx-auto text-center">
        <h2 className="text-2xl font-semibold mb-4">Quicker analysis</h2>
        <p className="text-gray-600 mb-10">
          Comparing doesn’t have to be hard. We offer a range of USDA-approved guidelines to compare
          the food products against.
        </p>
        <img src="/assets/comparison.png" alt="Product Comparison" className="mx-auto mb-16" />

        <h2 className="text-2xl font-semibold mb-2">Team collaboration</h2>
        <p className="text-gray-600 mb-10">
          Edit food lists whenever and wherever. We offer team collaboration to edit and make lists together.
        </p>
        <img src="../assets/collab.png" alt="Team Collaboration" className="mx-auto mb-16" />
      </section>

      {/* Pricing Teaser */}
      <section className="text-center px-6 py-16">
        <h2 className="text-2xl font-bold mb-2">Pricing</h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          We offer a range of plans. Choose based on your needs. You can downgrade or upgrade your plan later.
        </p>
        <Link to="/pricing">
          <button className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
            View Pricing
          </button>
        </Link>
      </section>

       <PricingSection />

      {/* Footer Placeholder */}
      <footer className="bg-gray-100 px-6 py-10 text-sm text-gray-500 text-center">
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
