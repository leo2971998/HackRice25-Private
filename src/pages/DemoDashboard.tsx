import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Download, TrendingUp, TrendingDown, Calendar, DollarSign } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

interface DemoSummaryData {
  total_balance: number;
  accounts: any[];
  recent_transactions: any[];
  customer_id: string;
}

export default function DemoDashboard() {
  const [summary, setSummary] = useState<DemoSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  
  const { demoCustomerId, isDemo } = location.state || {};

  useEffect(() => {
    if (!isDemo || !demoCustomerId) {
      navigate("/");
      return;
    }
    loadDemoSummary();
  }, [isDemo, demoCustomerId, navigate]);

  const loadDemoSummary = async () => {
    try {
      const response = await api.get("/demo/summary");
      setSummary(response.data);
    } catch (error: any) {
      console.error("Failed to load demo summary:", error);
      toast.error("Failed to load demo data");
    } finally {
      setLoading(false);
    }
  };

  const exportToSheets = () => {
    // Mock export functionality for demo
    toast.success("Data exported to Google Sheets! (Demo mode)");
  };

  const goBackToLanding = () => {
    navigate("/");
  };

  const calculateIncomeVsExpenses = () => {
    if (!summary?.recent_transactions) return { income: 0, expenses: 0 };
    
    let income = 0;
    let expenses = 0;
    
    summary.recent_transactions.forEach(transaction => {
      if (transaction.type === "deposit" || transaction.transaction_date) {
        income += transaction.amount;
      } else {
        expenses += transaction.amount;
      }
    });
    
    return { income, expenses };
  };

  const getSpendingByCategory = () => {
    if (!summary?.recent_transactions) return [];
    
    const categories: { [key: string]: number } = {};
    
    summary.recent_transactions.forEach(transaction => {
      if (transaction.type === "purchase" || transaction.purchase_date) {
        const description = transaction.description.toLowerCase();
        let category = "Other";
        
        if (description.includes("grocery") || description.includes("h-e-b")) {
          category = "Groceries";
        } else if (description.includes("gas") || description.includes("shell")) {
          category = "Transportation";
        } else if (description.includes("coffee") || description.includes("starbucks")) {
          category = "Food & Dining";
        } else if (description.includes("pharmacy") || description.includes("cvs")) {
          category = "Healthcare";
        } else if (description.includes("uber") || description.includes("ride")) {
          category = "Transportation";
        } else if (description.includes("metro") || description.includes("transit")) {
          category = "Transportation";
        }
        
        categories[category] = (categories[category] || 0) + transaction.amount;
      }
    });
    
    return Object.entries(categories).map(([name, amount]) => ({ name, amount }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your demo dashboard...</p>
        </div>
      </div>
    );
  }

  const { income, expenses } = calculateIncomeVsExpenses();
  const spendingByCategory = getSpendingByCategory();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <button
                onClick={goBackToLanding}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Demo Dashboard</h1>
                <p className="text-gray-600 mt-1">Houston Financial Navigator Demo Environment</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={exportToSheets}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Export to Sheets</span>
              </button>
              <a
                href="/chat"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Try Chat Assistant
              </a>
            </div>
          </div>
        </div>

        {/* Total Balance Card */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">Total Balance</h2>
              <p className="text-4xl font-bold">${summary?.total_balance?.toFixed(2) || "0.00"}</p>
              <p className="text-blue-100 mt-2">Across all your accounts</p>
            </div>
            <DollarSign className="h-16 w-16 text-blue-200" />
          </div>
        </div>

        {/* Income vs Expenses & Spending by Category */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Income vs Expenses */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
              Income vs Expenses (This Month)
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                  <span className="font-medium text-gray-900">Income</span>
                </div>
                <span className="text-lg font-semibold text-green-600">+${income.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <TrendingDown className="h-6 w-6 text-red-600" />
                  <span className="font-medium text-gray-900">Expenses</span>
                </div>
                <span className="text-lg font-semibold text-red-600">-${expenses.toFixed(2)}</span>
              </div>
              <div className="border-t pt-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-900">Net Income</span>
                  <span className={`text-lg font-bold ${income - expenses >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${(income - expenses).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Spending by Category */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Spending by Category</h3>
            <div className="space-y-3">
              {spendingByCategory.map((category, index) => {
                const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500', 'bg-pink-500'];
                const percentage = (category.amount / expenses) * 100;
                
                return (
                  <div key={category.name} className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`}></div>
                    <div className="flex-1 flex justify-between items-center">
                      <span className="text-gray-700 font-medium">{category.name}</span>
                      <div className="text-right">
                        <span className="text-gray-900 font-semibold">${category.amount.toFixed(2)}</span>
                        <span className="text-sm text-gray-500 ml-2">({percentage.toFixed(1)}%)</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Calendar className="h-5 w-5 mr-2 text-blue-600" />
            Recent Transactions (Last 25)
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {summary?.recent_transactions?.map((transaction, index) => (
              <div key={index} className="flex justify-between items-center py-3 px-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    transaction.type === 'deposit' || transaction.transaction_date ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <p className="font-medium text-gray-900">{transaction.description}</p>
                    <p className="text-sm text-gray-600">
                      {transaction.transaction_date || transaction.purchase_date}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${
                    transaction.type === 'deposit' || transaction.transaction_date ? "text-green-600" : "text-red-600"
                  }`}>
                    {transaction.type === 'deposit' || transaction.transaction_date ? "+" : "-"}${Math.abs(transaction.amount).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{transaction.type || 'purchase'}</p>
                </div>
              </div>
            ))}
            {(!summary?.recent_transactions || summary.recent_transactions.length === 0) && (
              <p className="text-gray-500 text-center py-8">No transactions found</p>
            )}
          </div>
        </div>

        {/* Demo Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <p className="text-yellow-800 font-medium">Demo Environment</p>
          </div>
          <p className="text-yellow-700 mt-1">
            This is a demonstration environment using sample data. Real financial data would be secured and encrypted.
            Try asking our AI assistant about "rent assistance near 77002" to see local aid programs!
          </p>
        </div>
      </div>
    </div>
  );
}