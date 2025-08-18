import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  ChevronDown,
  MessageSquare,
  ArrowUp,
  ArrowDown,
  Clock,
  Rocket,
  Compass,
  Mail,
  Menu,
  X,
  Plus,
  BookOpen,
  FileText,
  Calendar,
  Users,
  Flame,
  Target,
  Apple,
  Building2,
  GraduationCap,
  Heart,
  Shield,
  BarChart3,
  Database,
  Zap,
  Globe,
  ShoppingCart,
  Utensils,
  Pill,
  School,
  Store,
  Factory,
  Bookmark,
  Plane,
  Sparkles,
  Mic,
  Palette,
  Briefcase,
  RefreshCw,
  GitBranch,
  Activity,
  ChefHat,
  Calculator
} from 'lucide-react';

const ProductHuntPage = () => {
  const navigate = useNavigate();
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Mock product data in Product Hunt format
  const todaysProducts = [
    {
      id: 1,
      name: "Nutrigence",
      description: "Smart food intelligence platform for nutrition compliance",
      icon: "Shield",
      tags: ["Food & Beverage", "Healthcare", "B2B"],
      upvotes: 527,
      bookmarks: 89,
      isVoted: false
    },
    {
      id: 2,
      name: "SmartSnack Finder",
      description: "AI-powered tool to identify USDA Smart Snack compliant foods",
      icon: "Sparkles",
      tags: ["AI", "Education", "Nutrition"],
      upvotes: 390,
      bookmarks: 67,
      isVoted: false
    },
    {
      id: 3,
      name: "FoodCompliance Pro",
      description: "Comprehensive nutrition guideline compliance checker",
      icon: "BarChart3",
      tags: ["Healthcare", "Compliance", "Analytics"],
      upvotes: 383,
      bookmarks: 72,
      isVoted: false
    },
    {
      id: 4,
      name: "TeamNutrition Hub",
      description: "Collaborative platform for food service teams",
      icon: "Users",
      tags: ["Collaboration", "Food Service", "Team Management"],
      upvotes: 271,
      bookmarks: 47,
      isVoted: false
    }
  ];

  const yesterdaysProducts = [
    {
      id: 5,
      name: "Flight Deals",
      description: "Describe your trip, get the best flight deals",
      icon: "Plane",
      tags: ["Travel", "Artificial Intelligence", "Ticketing"],
      upvotes: 420,
      bookmarks: 18,
      isVoted: false
    },
    {
      id: 6,
      name: "Jaaz",
      description: "AI-powered food recommendation engine",
      icon: "Zap",
      tags: ["AI", "Food & Beverage", "Recommendations"],
      upvotes: 362,
      bookmarks: 26,
      isVoted: false
    },
    {
      id: 7,
      name: "Harmony AI Voice Assistant",
      description: "Voice-controlled nutrition planning assistant",
      icon: "Mic",
      tags: ["AI", "Voice", "Productivity"],
      upvotes: 243,
      bookmarks: 23,
      isVoted: false
    },
    {
      id: 8,
      name: "StickerX",
      description: "Create custom nutrition labels and stickers",
      icon: "Palette",
      tags: ["Design", "Food Service", "Compliance"],
      upvotes: 236,
      bookmarks: 27,
      isVoted: false
    },
    {
      id: 9,
      name: "GoPerfect - Real-Time Hiring",
      description: "Hire nutrition experts and food service professionals",
      icon: "Briefcase",
      tags: ["Hiring", "Food Service", "HR"],
      upvotes: 187,
      bookmarks: 8,
      isVoted: false,
      promoted: true
    }
  ];

  const lastWeeksProducts = [
    {
      id: 10,
      name: "Toddler Vacation",
      description: "Plan healthy meals for family vacations",
      icon: "Heart",
      tags: ["Travel", "Family", "Nutrition"],
      upvotes: 156,
      bookmarks: 12,
      isVoted: false
    },
    {
      id: 11,
      name: "NutriSync",
      description: "Sync nutrition data across all your devices",
      icon: "RefreshCw",
      tags: ["Sync", "Mobile", "Health"],
      upvotes: 134,
      bookmarks: 19,
      isVoted: false
    },
    {
      id: 12,
      name: "FoodFlow",
      description: "Streamline food service operations",
      icon: "GitBranch",
      tags: ["Operations", "Food Service", "Automation"],
      upvotes: 98,
      bookmarks: 15,
      isVoted: false
    }
  ];

  const lastMonthsProducts = [
    {
      id: 13,
      name: "HealthTracker Pro",
      description: "Advanced health and nutrition tracking platform",
      icon: "Activity",
      tags: ["Health", "Tracking", "Analytics"],
      upvotes: 89,
      bookmarks: 22,
      isVoted: false
    },
    {
      id: 14,
      name: "MenuMaster",
      description: "Create and manage restaurant menus with nutrition info",
      icon: "ChefHat",
      tags: ["Restaurant", "Menu", "Management"],
      upvotes: 76,
      bookmarks: 14,
      isVoted: false
    },
    {
      id: 15,
      name: "DietDash",
      description: "Quick dietary assessment and recommendations",
      icon: "Calculator",
      tags: ["Diet", "Assessment", "Health"],
      upvotes: 65,
      bookmarks: 11,
      isVoted: false
    }
  ];

  const trendingThreads = [
    {
      id: 1,
      icon: "🍎",
      forum: "p/nutrition",
      title: "How we built Nutrigence: From idea to 10,000+ food products",
      upvotes: 15,
      comments: 7
    },
    {
      id: 2,
      icon: "🏥",
      forum: "p/healthcare",
      title: "My hypotheses for healthcare food compliance failed. What would you do next?",
      upvotes: 20,
      comments: 14
    },
    {
      id: 3,
      icon: "🏫",
      forum: "p/education",
      title: "Create compliant school menus in just 2 clicks. This is the killer app of Nutrigence",
      upvotes: 10,
      comments: 7
    },
    {
      id: 4,
      icon: "💰",
      forum: "p/funding",
      title: "How we raised $500k before launch (step-by-step, with some hacks)",
      upvotes: 38,
      comments: 17
    }
  ];

  const handleVote = (productId: number, productList: any[]) => {
    // Toggle vote state for the product
    const updatedProducts = productList.map(product => 
      product.id === productId 
        ? { ...product, isVoted: !product.isVoted, upvotes: product.isVoted ? product.upvotes - 1 : product.upvotes + 1 }
        : product
    );
    // In a real app, you'd update state here
  };

  // Product Section Component
  const ProductSection = ({ title, products, productList }: { title: string, products: any[], productList: string }) => (
    <div className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
      
      {/* Products List */}
      <div className="space-y-6">
        {products.map((product, index) => (
          <div key={product.id} className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg transition-colors">
            {/* Product Number */}
            <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
              {index + 1}
            </div>

            {/* Product Icon */}
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                {(() => {
                  const IconComponent = (() => {
                                         switch(product.icon) {
                       case 'Shield': return Shield;
                       case 'Sparkles': return Sparkles;
                       case 'BarChart3': return BarChart3;
                       case 'Users': return Users;
                       case 'Plane': return Plane;
                       case 'Zap': return Zap;
                       case 'Mic': return Mic;
                       case 'Palette': return Palette;
                       case 'Briefcase': return Briefcase;
                       case 'Heart': return Heart;
                       case 'RefreshCw': return RefreshCw;
                       case 'GitBranch': return GitBranch;
                       case 'Activity': return Activity;
                       case 'ChefHat': return ChefHat;
                       case 'Calculator': return Calculator;
                       default: return Shield;
                     }
                  })();
                  return <IconComponent className="h-6 w-6 text-gray-600" />;
                })()}
              </div>
            </div>

            {/* Product Info */}
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {product.name}
              </h3>
              <p className="text-gray-600 mb-2">
                {product.description}
              </p>
              <div className="flex flex-wrap gap-2 mb-2">
                {product.tags.map((tag: string, tagIndex: number) => (
                  <span 
                    key={tagIndex}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              {product.promoted && (
                <span className="inline-block px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded">
                  Promoted
                </span>
              )}
            </div>

            {/* Vote Section */}
            <div className="flex-shrink-0 flex flex-col items-center space-y-1">
              <button
                onClick={() => handleVote(product.id, products)}
                className={`p-2 rounded-lg transition-colors ${
                  product.isVoted 
                    ? 'bg-red-100 text-red-600' 
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                }`}
              >
                <ArrowUp className="h-5 w-5" />
              </button>
              <span className="text-sm font-medium text-gray-900">
                {product.upvotes}
              </span>
              <button className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
                <ArrowDown className="h-5 w-5" />
              </button>
            </div>

            {/* Bookmarks */}
            <div className="flex-shrink-0 flex items-center space-x-1 text-gray-500">
              <Bookmark className="h-4 w-4" />
              <span className="text-sm">{product.bookmarks}</span>
            </div>
          </div>
        ))}
      </div>

      {/* See All Button */}
      <div className="text-center mt-6">
        <button className="border border-gray-300 bg-white text-gray-700 px-6 py-2 rounded-md font-medium hover:bg-gray-50 transition-colors">
          See all of {title.toLowerCase()}
        </button>
      </div>
    </div>
  );

  const toggleDropdown = (dropdownName: string) => {
    setActiveDropdown(activeDropdown === dropdownName ? null : dropdownName);
  };

  const closeDropdown = () => {
    setActiveDropdown(null);
  };

  // Handle clicking outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      // Check if click is outside any dropdown
      if (!target.closest('[data-dropdown]')) {
        setActiveDropdown(null);
      }
    };

    if (activeDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeDropdown]);

  return (
    <div className="min-h-screen bg-white">
      {/* Header - Product Hunt Style */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left side - Logo and Navigation */}
            <div className="flex items-center space-x-8">
              {/* Logo */}
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">N</span>
                </div>
                <span className="text-xl font-bold text-gray-900">Nutrigence</span>
              </div>

              {/* Search Bar */}
              <div className="hidden md:block relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search (ctrl + k)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-64 pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-red-500 focus:border-red-500"
                />
              </div>

              {/* Navigation Menu */}
              <nav className="hidden md:flex items-center space-x-8">
                                 {/* Launches Dropdown */}
                 <div className="relative" data-dropdown>
                  <button
                    onClick={() => toggleDropdown('launches')}
                    className={`flex items-center space-x-1 font-medium transition-colors ${
                      activeDropdown === 'launches' ? 'text-red-600' : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <span>Launches</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>
                  
                                     {activeDropdown === 'launches' && (
                     <div data-dropdown className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center mr-3">
                          <Clock className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <div className="font-medium">Coming soon</div>
                          <div className="text-xs text-gray-500">Upcoming launches to watch</div>
                        </div>
                      </a>
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-red-100 rounded flex items-center justify-center mr-3">
                          <Rocket className="h-4 w-4 text-red-600" />
                        </div>
                        <div>
                          <div className="font-medium">Launch archive</div>
                          <div className="text-xs text-gray-500">Most-loved launches by the community</div>
                        </div>
                      </a>
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center mr-3">
                          <Compass className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium">Launch Guide</div>
                          <div className="text-xs text-gray-500">Checklists and pro tips for launching</div>
                        </div>
                      </a>
                    </div>
                  )}
                </div>

                                 {/* Products Dropdown */}
                 <div className="relative" data-dropdown>
                  <button
                    onClick={() => toggleDropdown('products')}
                    className={`flex items-center space-x-1 font-medium transition-colors ${
                      activeDropdown === 'products' ? 'text-red-600' : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <span>Products</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>
                  
                                     {activeDropdown === 'products' && (
                     <div data-dropdown className="absolute top-full left-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 py-4 z-50">
                      {/* Shoutouts Leaderboard */}
                      <div className="px-4 pb-3 border-b border-gray-100">
                        <div className="flex items-center mb-2">
                          <Target className="h-4 w-4 text-gray-600 mr-2" />
                          <span className="font-medium text-sm">Shoutouts Leaderboard</span>
                        </div>
                        <p className="text-xs text-gray-500">The most-loved products on Nutrigence</p>
                      </div>

                      {/* Product Landscapes */}
                      <div className="px-4 py-3 border-b border-gray-100">
                        <div className="font-medium text-sm mb-2">Product Landscapes</div>
                        <div className="flex flex-wrap gap-2">
                          {['AI nutrition tools', 'Compliance software', 'Food service platforms', 'Healthcare analytics', 'School nutrition', 'Restaurant tech'].map((tag) => (
                            <span key={tag} className="px-2 py-1 bg-gray-100 text-xs text-gray-700 rounded hover:bg-gray-200 cursor-pointer">
                              {tag}
                            </span>
                          ))}
                          <span className="px-2 py-1 text-xs text-red-600 hover:text-red-700 cursor-pointer">
                            See more
                          </span>
                        </div>
                      </div>

                      {/* Categories Grid */}
                      <div className="grid grid-cols-2 gap-0">
                        <div className="px-4 py-2">
                          <div className="font-medium text-sm text-gray-900 mb-2">Work & Productivity</div>
                          <div className="space-y-1 text-sm">
                            {['Food Service Management', 'Nutrition Analysis', 'Compliance Tracking', 'Team Collaboration', 'Menu Planning', 'Inventory Management'].map((item) => (
                              <div key={item} className="text-gray-600 hover:text-gray-900 cursor-pointer py-1">
                                {item}
                              </div>
                            ))}
                          </div>
                        </div>
                        <div className="px-4 py-2">
                          <div className="font-medium text-sm text-gray-900 mb-2">Industry Solutions</div>
                          <div className="space-y-1 text-sm">
                            {['Healthcare & Hospitals', 'Schools & Education', 'Restaurants & Cafes', 'Retail & Grocery', 'Manufacturing', 'Distribution'].map((item) => (
                              <div key={item} className="text-gray-600 hover:text-gray-900 cursor-pointer py-1">
                                {item}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                                 {/* News Dropdown */}
                 <div className="relative" data-dropdown>
                  <button
                    onClick={() => toggleDropdown('news')}
                    className={`flex items-center space-x-1 font-medium transition-colors ${
                      activeDropdown === 'news' ? 'text-red-600' : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <span>News</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>
                  
                                     {activeDropdown === 'news' && (
                     <div data-dropdown className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center mr-3">
                          <Mail className="h-4 w-4 text-purple-600" />
                        </div>
                        <div>
                          <div className="font-medium">Newsletter</div>
                          <div className="text-xs text-gray-500">The best of Nutrigence, every day</div>
                        </div>
                      </a>
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-pink-100 rounded flex items-center justify-center mr-3">
                          <BookOpen className="h-4 w-4 text-pink-600" />
                        </div>
                        <div>
                          <div className="font-medium">Stories</div>
                          <div className="text-xs text-gray-500">Food industry news, interviews, and tips</div>
                        </div>
                      </a>
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center mr-3">
                          <FileText className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <div className="font-medium">Changelog</div>
                          <div className="text-xs text-gray-500">New Nutrigence features and releases</div>
                        </div>
                      </a>
                    </div>
                  )}
                </div>

                                 {/* Forums Dropdown */}
                 <div className="relative" data-dropdown>
                  <button
                    onClick={() => toggleDropdown('forums')}
                    className={`flex items-center space-x-1 font-medium transition-colors ${
                      activeDropdown === 'forums' ? 'text-red-600' : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <span>Forums</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>
                  
                                     {activeDropdown === 'forums' && (
                     <div data-dropdown className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-pink-100 rounded flex items-center justify-center mr-3">
                          <MessageSquare className="h-4 w-4 text-pink-600" />
                        </div>
                        <div>
                          <div className="font-medium">Forums</div>
                          <div className="text-xs text-gray-500">Ask questions, find support, and connect</div>
                        </div>
                      </a>
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-red-100 rounded flex items-center justify-center mr-3">
                          <Flame className="h-4 w-4 text-red-600" />
                        </div>
                        <div>
                          <div className="font-medium">Streaks</div>
                          <div className="text-xs text-gray-500">The most active community members</div>
                        </div>
                      </a>
                      <a href="#" className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">
                        <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center mr-3">
                          <Calendar className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <div className="font-medium">Events</div>
                          <div className="text-xs text-gray-500">Meet others online and in-person</div>
                        </div>
                      </a>
                    </div>
                  )}
                </div>

                <a href="#" className="text-gray-600 hover:text-gray-900 font-medium">Advertise</a>
              </nav>
            </div>

            {/* Right side - Actions */}
            <div className="flex items-center space-x-4">
              <button className="hidden md:flex items-center space-x-2 text-gray-600 hover:text-gray-900">
                <Mail className="h-4 w-4" />
                <span className="font-medium">Subscribe</span>
              </button>
              <button 
                onClick={() => navigate('/login')}
                className="bg-red-500 text-white px-4 py-2 rounded-md font-medium hover:bg-red-600"
              >
                Sign in
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Main Content Area */}
          <div className="flex-1">
            {/* Welcome Section */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-8">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center mr-3">
                  <span className="text-orange-600 text-lg">☁️</span>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Welcome to Nutrigence!</h2>
                  <p className="text-gray-600">The place to discover and launch new food intelligence tools.</p>
                </div>
              </div>
            </div>

            {/* Product Sections */}
            <ProductSection 
              title="Top Products Launching Today" 
              products={todaysProducts}
              productList="todaysProducts"
            />
            
            <ProductSection 
              title="Yesterday's Top Products" 
              products={yesterdaysProducts}
              productList="yesterdaysProducts"
            />
            
            <ProductSection 
              title="Last Week's Top Products" 
              products={lastWeeksProducts}
              productList="lastWeeksProducts"
            />
            
            <ProductSection 
              title="Last Month's Top Products" 
              products={lastMonthsProducts}
              productList="lastMonthsProducts"
            />


          </div>

          {/* Right Sidebar */}
          <div className="w-80 flex-shrink-0">
            {/* Trending Forum Threads */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Trending Forum Threads</h3>
              
              <div className="space-y-4">
                {trendingThreads.map((thread) => (
                  <div key={thread.id} className="border-b border-gray-100 pb-4 last:border-b-0">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-gray-100 rounded flex items-center justify-center text-xs">
                        {thread.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs text-gray-500 mb-1">
                          {thread.forum}
                        </div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 leading-tight">
                          {thread.title}
                        </h4>
                        <div className="text-xs text-gray-500">
                          Upvote ({thread.upvotes}) • {thread.comments}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2 mt-6">
                <button className="flex-1 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50">
                  View all
                </button>
                <button className="flex-1 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 flex items-center justify-center space-x-1">
                  <Plus className="h-4 w-4" />
                  <span>Start new thread</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Click outside to close dropdowns */}
      {activeDropdown && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={closeDropdown}
        />
      )}
    </div>
  );
};

export default ProductHuntPage;
