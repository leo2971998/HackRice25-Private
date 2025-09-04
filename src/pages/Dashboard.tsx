// src/pages/Dashboard.tsx
import { useEffect, useState } from "react";
import { mySummary, logout } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

interface SummaryData {
  total_balance: number;
  accounts: any[];
  recent_transactions: any[];
  customer_id: string;
}

export default function Dashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const { user, setUser } = useAuth();
  const nav = useNavigate();

  useEffect(() => {
    if (!user) {
      nav("/login");
      return;
    }

    if (!user.nessie_customer_id) {
      nav("/onboarding");
      return;
    }

    loadSummary();
  }, [user, nav]);

  const loadSummary = async () => {
    try {
      const data = await mySummary();
      setSummary(data);
    } catch (error: any) {
      if (error?.response?.data?.error === "no_nessie_customer") {
        nav("/onboarding");
      } else {
        toast.error("Failed to load dashboard data");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      nav("/login");
      toast.success("Logged out successfully");
    } catch (error) {
      toast.error("Logout failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.first_name || user?.email}!
              </h1>
              <p className="text-gray-600 mt-1">Here's your financial overview</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Balance Card */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
          <h2 className="text-xl font-semibold mb-2">Total Balance</h2>
          <p className="text-4xl font-bold">${summary?.total_balance?.toFixed(2) || "0.00"}</p>
          <p className="text-blue-100 mt-2">Across all your accounts</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Accounts */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Your Accounts</h3>
            {summary?.accounts?.length ? (
              <div className="space-y-3">
                {summary.accounts.map((account: any) => (
                  <div key={account._id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{account.nickname}</p>
                        <p className="text-sm text-gray-600">{account.type}</p>
                      </div>
                      <p className="text-lg font-semibold text-green-600">
                        ${account.balance?.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No accounts found</p>
            )}
          </div>

          {/* Recent Transactions */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Transactions</h3>
            {summary?.recent_transactions?.length ? (
              <div className="space-y-3">
                {summary.recent_transactions.slice(0, 5).map((transaction: any, index: number) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                    <div>
                      <p className="font-medium text-gray-900">{transaction.description}</p>
                      <p className="text-sm text-gray-600">
                        {transaction.transaction_date || transaction.purchase_date}
                      </p>
                    </div>
                    <p className={`font-semibold ${
                      transaction.amount > 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {transaction.transaction_date ? "+" : "-"}${Math.abs(transaction.amount).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No transactions found</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors">
              <div className="text-blue-600 font-semibold">View Transactions</div>
            </button>
            <button className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors">
              <div className="text-green-600 font-semibold">Add Deposit</div>
            </button>
            <button className="p-4 bg-orange-50 hover:bg-orange-100 rounded-lg text-center transition-colors">
              <div className="text-orange-600 font-semibold">Make Purchase</div>
            </button>
            <button className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors">
              <div className="text-purple-600 font-semibold">Financial Insights</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}