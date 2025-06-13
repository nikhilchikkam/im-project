import { Button } from '../components/Button';
import { Link } from 'react-router-dom';

const AuthLanding = () => {
  return (
    <div className="min-h-screen px-6 py-4">
      {/* Navbar Placeholder */}
      <div className="flex justify-between items-center mb-12">
        <h1 className="text-xl font-bold">Nutrition Logo</h1>
        <div className="flex space-x-6 text-base font-medium">
          <a href="#">Products</a>
          <a href="#">Pricing</a>
          <a href="#">Resources</a>
          <a href="#">Contact us</a>
          <Link to="/signup">
            <Button size="sm">Sign up</Button>
          </Link>
        </div>
      </div>

      {/* Auth Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* Login Side */}
        <div className="bg-blue-50 p-8 rounded-xl text-center flex flex-col justify-center">
          <h2 className="text-lg font-medium mb-6">Returning User? Login</h2>
          <Link to="/login">
            <Button variant="outline" className="w-full">
              Login
            </Button>
          </Link>
        </div>

        {/* Divider on larger screens */}
        <div className="hidden md:flex justify-center">
          <div className="w-px h-full bg-gray-300" />
        </div>

        {/* Signup Side */}
        <div className="text-center flex flex-col justify-center">
          <h2 className="text-lg font-medium mb-6">New User? Create an account</h2>
          <Link to="/signup">
            <Button className="w-full">Signup</Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AuthLanding;
