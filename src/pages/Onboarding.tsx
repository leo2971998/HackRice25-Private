// src/pages/Onboarding.tsx
import { useEffect, useState } from "react";
import { me, seed } from "@/api/auth";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/Auth";
import toast from "react-hot-toast";

export default function Onboarding() {
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();
  const { user, setUser } = useAuth();

  useEffect(() => {
    if (user?.nessie_customer_id) {
      nav("/dashboard");
    }
  }, [user, nav]);

  const handleSetup = async () => {
    setBusy(true);
    try {
      await seed();
      // Refresh user data to get the updated nessie_customer_id
      const updatedUser = await me();
      setUser(updatedUser);
      nav("/dashboard");
      toast.success("Demo account created successfully");
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Setup failed. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex items-center justify-center py-12 px-4 bg-dark-100 min-h-[calc(100vh-8rem)]">
      <div className="max-w-2xl w-full bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome to Houston Financial Navigator
          </h1>
          <p className="text-dark-900">
            Let's set up your personalized financial dashboard
          </p>
        </div>

        <div className="space-y-4">
          <div className="bg-dark-300/60 rounded-lg p-4 border border-dark-400">
            <h2 className="text-lg font-semibold text-white mb-2">
              What we'll create for you:
            </h2>
            <ul className="text-dark-900 space-y-1 text-sm">
              <li>• A sandbox customer profile</li>
              <li>• A checking account with sample transactions</li>
              <li>• Your personalized financial dashboard</li>
            </ul>
          </div>

          <button
            disabled={busy}
            onClick={handleSetup}
            className="w-full rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 text-white px-6 py-4 font-semibold disabled:opacity-60 disabled:cursor-not-allowed hover:from-primary-600 hover:to-primary-700 transition-all duration-200 shadow-lg"
          >
            {busy ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Setting up your account...</span>
              </div>
            ) : (
              "Create My Financial Account"
            )}
          </button>
        </div>

        <div className="text-center">
          <p className="text-sm text-dark-900">
            This will create a demo account with sample data for learning purposes
          </p>
        </div>
      </div>
    </div>
  );
}