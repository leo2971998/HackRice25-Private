// src/pages/Dashboard.tsx
import { useEffect, useState } from "react";
import { mySummary, logout } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import { useNavigate } from "react-router-dom";
import { Download, TrendingUp, TrendingDown, Calendar, DollarSign, PieChart, BarChart3 } from "lucide-react";
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

  const exportToSheets = () => {
    // TODO: Implement real Google Sheets export
    toast.success("Export to Sheets feature coming soon!");
  };

  const calculateIncomeVsExpenses = () => {
    if (!summary?.recent_transactions) return { income: 0, expenses: 0 };
    
    let income = 0;
    let expenses = 0;
    
    // Get current month's transactions
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    
    summary.recent_transactions.forEach(transaction => {
      const transactionDate = new Date(transaction.transaction_date || transaction.purchase_date);
      if (transactionDate.getMonth() === currentMonth && transactionDate.getFullYear() === currentYear) {
        if (transaction.transaction_date) { // Deposit
          income += transaction.amount;
        } else { // Purchase
          expenses += transaction.amount;
        }
      }
    });
    
    return { income, expenses };
  };

  const getSpendingByCategory = () => {
    if (!summary?.recent_transactions) return [];
    
    const categories: { [key: string]: number } = {};
    
    summary.recent_transactions.forEach(transaction => {
      if (transaction.purchase_date) { // Only purchases
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
        } else if (description.includes("utility") || description.includes("electric")) {
          category = "Utilities";
        }
        
        categories[category] = (categories[category] || 0) + transaction.amount;
      }
    });
    
    return Object.entries(categories).map(([name, amount]) => ({ name, amount }));
  };

  const get30DayBalance = () => {
    // Mock balance line data for 30 days
    const balanceData = [];
    let currentBalance = summary?.total_balance || 0;
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      // Simulate balance changes
      const variation = (Math.random() - 0.5) * 100;
      currentBalance += variation;
      
      balanceData.push({
        date: date.toLocaleDateString(),
        balance: Math.max(0, currentBalance)
      });
    }
    
    return balanceData;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  const { income, expenses } = calculateIncomeVsExpenses();
  const spendingByCategory = getSpendingByCategory();
  const balanceData = get30DayBalance();

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-4 min-h-[calc(100vh-8rem)]">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.first_name || user?.email}!
              </h1>
              <p className="text-gray-600 mt-1">Here's your financial overview</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={exportToSheets}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Export to Sheets</span>
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              >
                Logout
              </button>
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
          {/* Income vs Expenses (This Month) */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
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
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <PieChart className="h-5 w-5 mr-2 text-purple-600" />
              Spending by Category
            </h3>
            <div className="space-y-3">
              {spendingByCategory.map((category, index) => {
                const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500'];
                const percentage = expenses > 0 ? (category.amount / expenses) * 100 : 0;
                
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
              {spendingByCategory.length === 0 && (
                <p className="text-gray-500 text-center py-4">No spending data available</p>
              )}
            </div>
          </div>
        </div>

        {/* Balance Line (30d) & Recent Transactions */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Balance Line (30d) */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
              Balance Line (30 Days)
            </h3>
            <div className="h-40 flex items-end space-x-1">
              {balanceData.slice(-15).map((data, index) => {
                const maxBalance = Math.max(...balanceData.map(d => d.balance));
                const height = (data.balance / maxBalance) * 100;
                
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div 
                      className="bg-gradient-to-t from-blue-500 to-blue-300 rounded-sm w-full"
                      style={{ height: `${height}%`, minHeight: '4px' }}
                    ></div>
                    <span className="text-xs text-gray-500 mt-1 transform rotate-45 origin-bottom-left">
                      {data.date.split('/')[1]}/{data.date.split('/')[0]}
                    </span>
                  </div>
                );
              })}
            </div>
            <p className="text-sm text-gray-600 mt-2 text-center">
              Current: ${balanceData[balanceData.length - 1]?.balance.toFixed(2)}
            </p>
          </div>

          {/* Recent Transactions (10-25) */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-blue-600" />
              Recent Transactions
            </h3>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {summary?.recent_transactions?.slice(0, 25).map((transaction, index) => (
                <div key={index} className="flex justify-between items-center py-2 px-3 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      transaction.transaction_date ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{transaction.description}</p>
                      <p className="text-xs text-gray-600">
                        {transaction.transaction_date || transaction.purchase_date}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold text-sm ${
                      transaction.transaction_date ? "text-green-600" : "text-red-600"
                    }`}>
                      {transaction.transaction_date ? "+" : "-"}${Math.abs(transaction.amount).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
              {(!summary?.recent_transactions || summary.recent_transactions.length === 0) && (
                <p className="text-gray-500 text-center py-8">No transactions found</p>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors">
              <div className="text-blue-600 font-semibold">View All Transactions</div>
            </button>
            <button className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors">
              <div className="text-green-600 font-semibold">Add Deposit</div>
            </button>
            <button className="p-4 bg-orange-50 hover:bg-orange-100 rounded-lg text-center transition-colors">
              <div className="text-orange-600 font-semibold">Make Purchase</div>
            </button>
            <button 
              onClick={() => nav("/chat")}
              className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors"
            >
              <div className="text-purple-600 font-semibold">Ask AI Assistant</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}