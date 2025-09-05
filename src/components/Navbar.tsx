import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/Auth";
import { logout } from "@/api/auth";
import { DollarSign, LogOut, Zap, TrendingUp } from "lucide-react";
import toast from "react-hot-toast";

export default function Navbar() {
  const { user, setUser, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      navigate("/");
      toast.success("Logged out successfully");
    } catch (error) {
      toast.error("Logout failed");
    }
  };

  return (
    <nav className="border-b border-dark-400 bg-dark-200/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 hover:text-primary-500 transition-colors">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Houston Financial Navigator</h1>
              <p className="text-xs text-dark-900">Smart Financial Management</p>
            </div>
          </Link>

          <div className="flex items-center space-x-6 text-sm">
            <NavLink 
              to="/chat" 
              className={({isActive}) => `hover:text-primary-500 transition-colors ${isActive ? "text-primary-500 font-medium" : "text-dark-900"}`}
            >
              Chat
            </NavLink>
            <NavLink 
              to="/learn" 
              className={({isActive}) => `hover:text-primary-500 transition-colors ${isActive ? "text-primary-500 font-medium" : "text-dark-900"}`}
            >
              Learn
            </NavLink>
            {user && (
              <NavLink 
                to="/dashboard" 
                className={({isActive}) => `hover:text-primary-500 transition-colors ${isActive ? "text-primary-500 font-medium" : "text-dark-900"}`}
              >
                Dashboard
              </NavLink>
            )}
            <NavLink 
              to="/admin" 
              className={({isActive}) => `hover:text-primary-500 transition-colors ${isActive ? "text-primary-500 font-medium" : "text-dark-900"}`}
            >
              Admin
            </NavLink>

            <div className="hidden md:flex items-center space-x-2 text-sm text-dark-900">
              <TrendingUp className="w-4 h-4" />
              <span>Real-time Analysis</span>
            </div>

            <div className="border-l border-dark-400 pl-6 flex items-center gap-4">
              {!loading && (
                user ? (
                  <div className="flex items-center gap-3">
                    <span className="text-white font-medium">
                      {user.first_name || user.email}
                    </span>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-1 text-dark-900 hover:text-primary-500 transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                ) : (
                  <>
                    <Link 
                      to="/login" 
                      className="text-dark-900 hover:text-primary-500 transition-colors"
                    >
                      Sign In
                    </Link>
                    <Link 
                      to="/register" 
                      className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white px-3 py-1.5 rounded-lg transition-all duration-200 text-sm shadow-lg"
                    >
                      Sign Up
                    </Link>
                  </>
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}