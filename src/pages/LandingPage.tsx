import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowRight, PieChart, TrendingUp, Users, Shield, Smartphone, DollarSign, Zap } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";
import { Card, CardContent } from "@/components/Card";

export default function LandingPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const startDemo = async () => {
    setLoading(true);
    try {
      // Call the demo seed endpoint
      const response = await api.post("/demo/seed");
      
      if (response.data.ok) {
        toast.success("Demo environment ready!");
        // Navigate to dashboard
        navigate("/dashboard-demo", { 
          state: { 
            demoCustomerId: response.data.customer_id,
            isDemo: true 
          } 
        });
      } else {
        throw new Error("Failed to initialize demo");
      }
    } catch (error: any) {
      console.error("Demo initialization error:", error);
      toast.error("Demo initialization failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-fade-in">
            Navigate Your
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-primary-600">
              Financial Future
            </span>
          </h1>
          
          <p className="text-xl text-dark-900 mb-8 max-w-3xl mx-auto">
            Houston Financial Navigator helps residents find financial aid programs and understand their spending patterns. 
            Get personalized insights and discover local assistance programs tailored to your needs.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <button
              onClick={startDemo}
              disabled={loading}
              className="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 disabled:opacity-60 disabled:cursor-not-allowed gaming-glow"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Setting up demo...</span>
                </div>
              ) : (
                <>
                  <span>Start Demo</span>
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
            
            <Link
              to="/register"
              className="px-8 py-4 border-2 border-dark-400 text-white font-semibold rounded-lg hover:border-primary-500 hover:bg-dark-200 transition-all duration-200"
            >
              Create Account
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card hoverable className="animate-slide-up">
            <CardContent className="p-8">
              <div className="bg-primary-500/20 rounded-lg p-3 w-fit mb-4">
                <PieChart className="h-8 w-8 text-primary-500" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Smart Financial Dashboard</h3>
              <p className="text-dark-900">
                Visualize your spending patterns with interactive charts showing income vs expenses, 
                spending by category, and balance trends over time.
              </p>
            </CardContent>
          </Card>

          <Card hoverable className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <CardContent className="p-8">
              <div className="bg-accent-emerald/20 rounded-lg p-3 w-fit mb-4">
                <Users className="h-8 w-8 text-accent-emerald" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Local Aid Programs</h3>
              <p className="text-dark-900">
                AI-powered chatbot helps you discover rent, utility, food, and homebuyer assistance 
                programs available in Houston and Harris County.
              </p>
            </CardContent>
          </Card>

          <Card hoverable className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <CardContent className="p-8">
              <div className="bg-purple-500/20 rounded-lg p-3 w-fit mb-4">
                <TrendingUp className="h-8 w-8 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Real-time Insights</h3>
              <p className="text-dark-900">
                Connect with Capital One's Nessie sandbox API for real-time financial data and 
                personalized spending analysis.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Benefits Section */}
        <Card className="p-8 md:p-12 mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-4">Why Choose Houston Financial Navigator?</h2>
            <p className="text-dark-900 max-w-2xl mx-auto">
              Designed specifically for Houston residents, our platform combines cutting-edge technology 
              with local expertise to help you make informed financial decisions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex items-start space-x-4">
              <Shield className="h-6 w-6 text-primary-500 mt-1" />
              <div>
                <h4 className="font-semibold text-white mb-2">Secure & Private</h4>
                <p className="text-dark-900">Your financial data is protected with bank-level security and encryption.</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <Smartphone className="h-6 w-6 text-primary-500 mt-1" />
              <div>
                <h4 className="font-semibold text-white mb-2">Mobile Optimized</h4>
                <p className="text-dark-900">Access your financial insights anywhere, anytime on any device.</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <DollarSign className="h-6 w-6 text-primary-500 mt-1" />
              <div>
                <h4 className="font-semibold text-white mb-2">Free to Use</h4>
                <p className="text-dark-900">Get started with our comprehensive financial tools at no cost.</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <Users className="h-6 w-6 text-primary-500 mt-1" />
              <div>
                <h4 className="font-semibold text-white mb-2">Local Focus</h4>
                <p className="text-dark-900">Tailored specifically for Houston and Harris County residents.</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Call to Action */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Take Control of Your Finances?</h2>
          <p className="text-dark-900 mb-8 max-w-2xl mx-auto">
            Start your journey to financial wellness today. Try our demo to see how Houston Financial Navigator 
            can help you understand your spending and find local assistance programs.
          </p>
          
          <button
            onClick={startDemo}
            disabled={loading}
            className="px-10 py-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed gaming-glow"
          >
            {loading ? "Setting up demo..." : "Start Your Demo Now"}
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-dark-200/80 backdrop-blur-sm border-t border-dark-400 text-white py-12 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-6 h-6 bg-gradient-to-br from-primary-500 to-primary-600 rounded flex items-center justify-center">
                  <Zap className="w-4 h-4 text-white" />
                </div>
                <span className="text-lg font-semibold">Houston Financial Navigator</span>
              </div>
              <p className="text-dark-900">
                Empowering Houston residents with financial insights and local assistance programs.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white">Features</h4>
              <ul className="space-y-2 text-dark-900">
                <li><a href="#" className="hover:text-primary-500 transition-colors">Financial Dashboard</a></li>
                <li><a href="#" className="hover:text-primary-500 transition-colors">AI Chat Assistant</a></li>
                <li><a href="#" className="hover:text-primary-500 transition-colors">Local Aid Programs</a></li>
                <li><a href="#" className="hover:text-primary-500 transition-colors">Spending Analysis</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white">Resources</h4>
              <ul className="space-y-2 text-dark-900">
                <li><Link to="/learn" className="hover:text-primary-500 transition-colors">Learn</Link></li>
                <li><a href="#" className="hover:text-primary-500 transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-primary-500 transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-primary-500 transition-colors">Privacy Policy</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white">Get Started</h4>
              <ul className="space-y-2 text-dark-900">
                <li><Link to="/register" className="hover:text-primary-500 transition-colors">Sign Up</Link></li>
                <li><Link to="/login" className="hover:text-primary-500 transition-colors">Sign In</Link></li>
                <li><Link to="/chat" className="hover:text-primary-500 transition-colors">Try Chat</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-dark-400 mt-8 pt-8 text-center text-dark-900">
            <p>&copy; 2025 Houston Financial Navigator. Built for HackRice 25.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}