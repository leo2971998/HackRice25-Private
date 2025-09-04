import { Link, NavLink } from "react-router-dom";
import { DollarSign } from "lucide-react";

export default function Navbar() {
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
	      <NavLink 
	        to="/dashboard" 
	        className={({isActive}) => `hover:text-blue-600 transition-colors ${isActive ? "text-blue-600 font-medium" : "text-gray-600"}`}
	      >
	        Dashboard
	      </NavLink>
	      <NavLink 
	        to="/admin" 
	        className={({isActive}) => `hover:text-blue-600 transition-colors ${isActive ? "text-blue-600 font-medium" : "text-gray-600"}`}
	      >
	        Admin
	      </NavLink>
	      <div className="border-l border-gray-300 pl-6">
	        <Link 
	          to="/login" 
	          className="text-gray-600 hover:text-blue-600 transition-colors mr-4"
	        >
	          Sign In
	        </Link>
	        <Link 
	          to="/register" 
	          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors text-sm"
	        >
	          Sign Up
	        </Link>
	      </div>
	    </div>
	  </div>
	</nav>
  );
}