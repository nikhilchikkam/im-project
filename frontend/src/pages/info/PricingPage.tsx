import { PricingSection } from '../../features/pricing/PricingSection';
import NavbarBefore from '../../components/navigation/NavbarBefore';

const PricingPage = () => {
  return (
    <div className="min-h-screen bg-white overflow-y-scrollbar-gutter-stable">
      <NavbarBefore />
      <PricingSection />
    </div>
  );
};

export default PricingPage;
