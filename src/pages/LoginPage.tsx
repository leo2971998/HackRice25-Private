// src/pages/LoginPage.tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login, me } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import toast from "react-hot-toast";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();
  const { setUser } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const loginResponse = await login({ email, password });
      const user = await me();
      setUser(user);
      
      // Route based on user role
      if (user.role === "admin") {
        nav("/admin");
        toast.success("Welcome back, Admin!");
      } else if (!user.nessie_customer_id) {
        nav("/onboarding");
        toast.success("Welcome back!");
      } else {
        nav("/dashboard");
        toast.success("Welcome back!");
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center py-12 px-4 bg-dark-100 min-h-[calc(100vh-8rem)]">
      <div className="max-w-2xl w-full bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-dark-900">Sign in to your Houston Financial Navigator account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-white">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-dark-800 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white placeholder-dark-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-dark-800 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white placeholder-dark-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-primary-500 to-primary-600 text-white py-3 px-4 rounded-lg font-semibold disabled:opacity-60 disabled:cursor-not-allowed hover:from-primary-600 hover:to-primary-700 transition-all duration-200 shadow-lg"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Signing in...</span>
              </div>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-dark-900">
            Don't have an account?{" "}
            <Link to="/register" className="text-primary-500 hover:text-primary-400 font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}