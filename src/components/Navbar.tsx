import { Link, NavLink, useNavigate } from "react-router-dom";
import { DollarSign, LogOut } from "lucide-react";
import { useAuth } from "@/context/Auth";
import { logout } from "@/api/auth";
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
	<nav className="sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-white/90 dark:supports-[backdrop-filter]:bg-neutral-950/90 border-b border-neutral-200 dark:border-neutral-800 shadow-sm">
	  <div className="mx-auto max-w-4xl px-4 h-16 flex items-center justify-between">
	    <Link to="/" className="font-semibold text-lg flex items-center space-x-2 hover:text-blue-600 transition-colors">
	      <DollarSign className="h-6 w-6" />
	      <span>Houston Financial Navigator</span>
	    </Link>
	    <div className="flex items-center gap-6 text-sm">
	      <NavLink 
	        to="/chat" 
	        className={({isActive}) => `hover:text-blue-600 transition-colors ${isActive ? "text-blue-600 font-medium" : "text-gray-600"}`}
	      >
	        Chat
	      </NavLink>
	      <NavLink 
	        to="/learn" 
	        className={({isActive}) => `hover:text-blue-600 transition-colors ${isActive ? "text-blue-600 font-medium" : "text-gray-600"}`}
	      >
	        Learn
	      </NavLink>
	      {user && (
	        <NavLink 
	          to="/dashboard" 
	          className={({isActive}) => `hover:text-blue-600 transition-colors ${isActive ? "text-blue-600 font-medium" : "text-gray-600"}`}
	        >
	          Dashboard
	        </NavLink>
	      )}
	      <NavLink 
	        to="/admin" 
	        className={({isActive}) => `hover:text-blue-600 transition-colors ${isActive ? "text-blue-600 font-medium" : "text-gray-600"}`}
	      >
	        Admin
	      </NavLink>
	      <div className="border-l border-gray-300 pl-6 flex items-center gap-4">
	        {!loading && (
	          user ? (
	            <div className="flex items-center gap-3">
	              <span className="text-gray-700 font-medium">
	                {user.first_name || user.email}
	              </span>
	              <button
	                onClick={handleLogout}
	                className="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition-colors"
	              >
	                <LogOut className="h-4 w-4" />
	                <span>Sign Out</span>
	              </button>
	            </div>
	          ) : (
	            <>
	              <Link 
	                to="/login" 
	                className="text-gray-600 hover:text-blue-600 transition-colors"
	              >
	                Sign In
	              </Link>
	              <Link 
	                to="/register" 
	                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors text-sm"
	              >
	                Sign Up
	              </Link>
	            </>
	          )
	        )}
	      </div>
	    </div>
	  </div>
	</nav>
  );
}