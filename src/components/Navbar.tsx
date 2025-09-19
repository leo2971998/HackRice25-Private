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
    <nav className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 text-black hover:text-blue-600 transition-colors">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-black">Houston Financial Navigator</h1>
              <p className="text-xs text-black">Smart Financial Management</p>
            </div>
          </Link>

          <div className="flex items-center space-x-6 text-sm text-black">
            <NavLink
              to="/chat"
              className={({isActive}) => `transition-colors ${isActive ? "text-blue-600 font-medium" : "text-black hover:text-blue-600"}`}
            >
              Chat
            </NavLink>
            <NavLink
              to="/learn"
              className={({isActive}) => `transition-colors ${isActive ? "text-blue-600 font-medium" : "text-black hover:text-blue-600"}`}
            >
              Learn
            </NavLink>
            {user && (
              <>
                <NavLink
                  to="/dashboard"
                  className={({isActive}) => `transition-colors ${isActive ? "text-blue-600 font-medium" : "text-black hover:text-blue-600"}`}
                >
                  Dashboard
                </NavLink>
                <NavLink
                  to="/trustagent"
                  className={({isActive}) => `transition-colors ${isActive ? "text-blue-600 font-medium" : "text-black hover:text-blue-600"}`}
                >
                  TrustAgent
                </NavLink>
              </>
            )}
            {user?.role === "admin" && (
              <NavLink
                to="/admin"
                className={({isActive}) => `transition-colors ${isActive ? "text-blue-600 font-medium" : "text-black hover:text-blue-600"}`}
              >
                Admin
              </NavLink>
            )}

            <div className="hidden md:flex items-center space-x-2 text-sm text-black">
              <TrendingUp className="w-4 h-4" />
              <span>Real-time Analysis</span>
            </div>

            <div className="border-l border-gray-200 pl-6 flex items-center gap-4">
              {!loading && (
                user ? (
                  <div className="flex items-center gap-3">
                    <span className="text-black font-medium">
                      {user.first_name || user.email}
                    </span>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-1 text-black hover:text-blue-600 transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="text-black hover:text-blue-600 transition-colors"
                    >
                      Sign In
                    </Link>
                    <Link
                      to="/register"
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-all duration-200 text-sm shadow-lg"
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