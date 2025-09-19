// src/pages/Dashboard.tsx
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { mySummary, logout } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import { useNavigate } from "react-router-dom";
import {
  Download,
  TrendingUp,
  TrendingDown,
  Calendar,
  DollarSign,
  PieChart,
  BarChart3,
  ArrowDownRight,
  ArrowUpRight,
  Sparkles,
  Loader2,
} from "lucide-react";
import toast from "react-hot-toast";
import { Skeleton, SkeletonGroup } from "@/components/Skeleton";
import { categorizeTransaction, createDeposit, createPurchase, type TransactionPayload } from "@/api/client";

interface SummaryData {
  total_balance: number;
  accounts: any[];
  recent_transactions: any[];
  customer_id: string;
  user_categories?: Record<string, string>;
  ap2_summary?: {
    active_count: number;
    pending_count: number;
    estimated_savings: number;
  };
}

const CATEGORY_OPTIONS = [
  "Groceries",
  "Transportation",
  "Housing",
  "Utilities",
  "Healthcare",
  "Entertainment",
  "Food & Dining",
  "Savings",
  "Income",
  "Other",
];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value || 0);

export default function Dashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTransaction, setSelectedTransaction] = useState<any | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [transactionCategories, setTransactionCategories] = useState<Record<string, string>>({});
  const [categoryDraft, setCategoryDraft] = useState("");
  const [categorySaving, setCategorySaving] = useState(false);
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<"deposit" | "purchase" | null>(null);
  const [depositForm, setDepositForm] = useState(() => ({
    amount: "",
    description: "",
    date: new Date().toISOString().slice(0, 10),
  }));
  const [purchaseForm, setPurchaseForm] = useState(() => ({
    amount: "",
    description: "",
    date: new Date().toISOString().slice(0, 10),
  }));
  const [displayBalance, setDisplayBalance] = useState(0);
  const animationFrameRef = useRef<number>();
  const previousBalanceRef = useRef(0);
  const hasInitialBalanceRef = useRef(false);
  const { user, setUser } = useAuth();
  const nav = useNavigate();

  const inferCategory = useCallback(
    (transaction: any) => {
      if (!transaction) return "Other";
      const key = transaction.category_key || "";
      const saved = key ? transactionCategories[key] : undefined;
      if (saved) {
        return saved;
      }

      if (transaction.transaction_date) {
        return "Income";
      }

      const description = (transaction.description || "").toLowerCase();
      if (description.includes("grocery") || description.includes("h-e-b")) {
        return "Groceries";
      }
      if (description.includes("gas") || description.includes("shell")) {
        return "Transportation";
      }
      if (description.includes("coffee") || description.includes("starbucks")) {
        return "Food & Dining";
      }
      if (description.includes("pharmacy") || description.includes("cvs")) {
        return "Healthcare";
      }
      if (description.includes("uber") || description.includes("ride")) {
        return "Transportation";
      }
      if (description.includes("metro") || description.includes("transit")) {
        return "Transportation";
      }
      if (description.includes("utility") || description.includes("electric")) {
        return "Utilities";
      }
      if (description.includes("rent") || description.includes("mortgage") || description.includes("lease")) {
        return "Housing";
      }

      return "Other";
    },
    [transactionCategories]
  );

  const loadSummary = useCallback(async ({ showSkeleton = false } = {}) => {
    if (showSkeleton) {
      setLoading(true);
    }
    try {
      const data = await mySummary();
      setSummary(data);
      setTransactionCategories(data.user_categories || {});
    } catch (error: any) {
      if (error?.response?.data?.error === "no_nessie_customer") {
        nav("/onboarding");
      } else {
        toast.error("Failed to load dashboard data");
      }
    } finally {
      setLoading(false);
    }
  }, [nav]);

  useEffect(() => {
    if (!user) {
      nav("/login");
      return;
    }

    if (!user.nessie_customer_id) {
      nav("/onboarding");
      return;
    }

    loadSummary({ showSkeleton: true });
  }, [user, nav, loadSummary]);

  useEffect(() => {
    if (!selectedTransaction) {
      setCategoryDraft("");
      return;
    }
    setCategoryDraft(inferCategory(selectedTransaction));
  }, [selectedTransaction, inferCategory]);

  useEffect(() => {
    if (!summary) return;

    const target = summary.total_balance || 0;
    if (!hasInitialBalanceRef.current) {
      setDisplayBalance(target);
      previousBalanceRef.current = target;
      hasInitialBalanceRef.current = true;
      return;
    }

    const start = previousBalanceRef.current;
    const diff = target - start;
    const duration = 700;
    const startTime = performance.now();

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    const animate = (time: number) => {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayBalance(start + diff * eased);

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        previousBalanceRef.current = target;
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);
  }, [summary]);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

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
      const rawDate = transaction.transaction_date || transaction.purchase_date;
      if (!rawDate) return;
      const transactionDate = new Date(rawDate);
      if (Number.isNaN(transactionDate.getTime())) return;
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

  const { spendingByCategory, transactionsByCategory } = useMemo(() => {
    if (!summary?.recent_transactions) {
      return { spendingByCategory: [], transactionsByCategory: {} as Record<string, any[]> };
    }

    const categories: Record<string, number> = {};
    const transactionMap: Record<string, any[]> = {};

    summary.recent_transactions.forEach(transaction => {
      const category = inferCategory(transaction);
      if (!category) return;

      if (!transactionMap[category]) {
        transactionMap[category] = [];
      }
      transactionMap[category].push(transaction);

      if (transaction.purchase_date) {
        categories[category] = (categories[category] || 0) + transaction.amount;
      }
    });

    const formattedCategories = Object.entries(categories).map(([name, amount]) => ({ name, amount }));

    return { spendingByCategory: formattedCategories, transactionsByCategory: transactionMap };
  }, [summary, inferCategory]);

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
      <div className="min-h-[calc(100vh-8rem)] bg-dark-100 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-6xl space-y-6">
          <div className="bg-dark-200 border border-dark-400 rounded-2xl p-6 shadow-xl space-y-4">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-64" />
            <SkeletonGroup count={3} itemClassName="h-12 w-full bg-dark-300/70" />
          </div>
          <div className="grid lg:grid-cols-2 gap-6">
            <Skeleton className="h-56 w-full bg-dark-200 border border-dark-400 rounded-2xl" />
            <Skeleton className="h-56 w-full bg-dark-200 border border-dark-400 rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  const largestPurchase = useMemo(() => {
    if (!summary?.recent_transactions) return null;
    return summary.recent_transactions
      .filter(transaction => transaction.purchase_date)
      .reduce((max: any, transaction: any) => {
        if (!max || transaction.amount > max.amount) {
          return transaction;
        }
        return max;
      }, null as any);
  }, [summary?.recent_transactions]);

  const largestDeposit = useMemo(() => {
    if (!summary?.recent_transactions) return null;
    return summary.recent_transactions
      .filter(transaction => transaction.transaction_date)
      .reduce((max: any, transaction: any) => {
        if (!max || transaction.amount > max.amount) {
          return transaction;
        }
        return max;
      }, null as any);
  }, [summary?.recent_transactions]);

  const spendingTrend = useMemo(() => {
    if (!summary?.recent_transactions) return null;

    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    const previous = new Date(currentYear, currentMonth - 1, 1);
    const previousMonth = previous.getMonth();
    const previousYear = previous.getFullYear();

    let currentSpending = 0;
    let previousSpending = 0;

    summary.recent_transactions.forEach(transaction => {
      if (!transaction.purchase_date) return;
      const dateValue = new Date(transaction.purchase_date);
      if (Number.isNaN(dateValue.getTime())) return;

      if (dateValue.getFullYear() === currentYear && dateValue.getMonth() === currentMonth) {
        currentSpending += transaction.amount;
      } else if (dateValue.getFullYear() === previousYear && dateValue.getMonth() === previousMonth) {
        previousSpending += transaction.amount;
      }
    });

    let percentage = 0;
    let direction: "up" | "down" | "flat" = "flat";
    if (previousSpending > 0) {
      const change = ((currentSpending - previousSpending) / previousSpending) * 100;
      if (change > 0.5) {
        direction = "up";
        percentage = change;
      } else if (change < -0.5) {
        direction = "down";
        percentage = Math.abs(change);
      }
    }

    return {
      current: currentSpending,
      previous: previousSpending,
      direction,
      percentage,
    };
  }, [summary?.recent_transactions]);

  const ap2Summary = summary?.ap2_summary || {
    active_count: 0,
    pending_count: 0,
    estimated_savings: 0,
  };

  const { income, expenses } = calculateIncomeVsExpenses();
  const balanceData = get30DayBalance();
  const filteredTransactions = useMemo(() => {
    if (!summary?.recent_transactions) return [] as any[];
    if (!selectedCategory) return summary.recent_transactions;
    return transactionsByCategory[selectedCategory] || [];
  }, [summary?.recent_transactions, selectedCategory, transactionsByCategory]);

  const handleSubmitDeposit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const amount = parseFloat(depositForm.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      toast.error("Enter a positive deposit amount");
      return;
    }

    const payload: TransactionPayload = {
      amount,
      description: depositForm.description || "Deposit",
      date: depositForm.date,
    };

    setActionLoading("deposit");
    try {
      const { transaction, total_balance } = await createDeposit(payload);
      if (!transaction) {
        throw new Error("Deposit failed to return transaction");
      }
      toast.success("Deposit recorded");
      setShowDepositModal(false);
      setDepositForm(() => ({ amount: "", description: "", date: new Date().toISOString().slice(0, 10) }));
      setSummary(prev => {
        if (!prev) return prev;
        const updatedTransactions = [transaction, ...prev.recent_transactions].slice(0, 25);
        const updatedBalance = typeof total_balance === "number" ? total_balance : prev.total_balance + amount;
        return { ...prev, recent_transactions: updatedTransactions, total_balance: updatedBalance };
      });
      if (transaction.category_key) {
        setTransactionCategories(prev => ({
          ...prev,
          [transaction.category_key]: inferCategory(transaction),
        }));
      }
      loadSummary();
    } catch (error: any) {
      console.error(error);
      toast.error(error?.response?.data?.error || "Failed to add deposit");
    } finally {
      setActionLoading(null);
    }
  };

  const handleSubmitPurchase = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const amount = parseFloat(purchaseForm.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      toast.error("Enter a positive purchase amount");
      return;
    }

    const payload: TransactionPayload = {
      amount,
      description: purchaseForm.description || "Purchase",
      date: purchaseForm.date,
    };

    setActionLoading("purchase");
    try {
      const { transaction, total_balance } = await createPurchase(payload);
      if (!transaction) {
        throw new Error("Purchase failed to return transaction");
      }
      toast.success("Purchase added");
      setShowPurchaseModal(false);
      setPurchaseForm(() => ({ amount: "", description: "", date: new Date().toISOString().slice(0, 10) }));
      setSummary(prev => {
        if (!prev) return prev;
        const updatedTransactions = [transaction, ...prev.recent_transactions].slice(0, 25);
        const updatedBalance = typeof total_balance === "number" ? total_balance : prev.total_balance - amount;
        return { ...prev, recent_transactions: updatedTransactions, total_balance: updatedBalance };
      });
      if (transaction.category_key) {
        setTransactionCategories(prev => ({
          ...prev,
          [transaction.category_key]: inferCategory(transaction),
        }));
      }
      loadSummary();
    } catch (error: any) {
      console.error(error);
      toast.error(error?.response?.data?.error || "Failed to add purchase");
    } finally {
      setActionLoading(null);
    }
  };

  const handleSaveCategory = async () => {
    if (!selectedTransaction) return;
    const trimmed = categoryDraft.trim();
    if (!trimmed) {
      toast.error("Enter a category name");
      return;
    }
    if (!selectedTransaction.category_key) {
      toast.error("Unable to categorize this transaction");
      return;
    }

    setCategorySaving(true);
    try {
      await categorizeTransaction({ category_key: selectedTransaction.category_key, category: trimmed });
      setTransactionCategories(prev => ({ ...prev, [selectedTransaction.category_key]: trimmed }));
      toast.success("Category saved");
    } catch (error: any) {
      console.error(error);
      toast.error(error?.response?.data?.error || "Failed to save category");
    } finally {
      setCategorySaving(false);
    }
  };

  const handleAskAIAboutTransaction = () => {
    if (!selectedTransaction) return;
    const merchant = selectedTransaction.description || "this transaction";
    const when = selectedTransaction.transaction_date || selectedTransaction.purchase_date;
    const prompt = `Tell me about my spending habits related to this transaction at ${merchant}${when ? ` on ${when}` : ""}.`;
    setSelectedTransaction(null);
    nav("/chat", { state: { prefillPrompt: prompt } });
  };

  return (
    <div className="bg-dark-100 min-h-[calc(100vh-8rem)] p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">
                Welcome back, {user?.first_name || user?.email}!
              </h1>
              <p className="text-dark-900 mt-1">Here's your financial overview</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={exportToSheets}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Export to Sheets</span>
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-dark-300 hover:bg-dark-400 text-dark-900 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Total Balance Card */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl shadow-xl p-8 text-white border border-dark-400">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">Total Balance</h2>
              <p className="text-4xl font-bold transition-all duration-500">{formatCurrency(displayBalance)}</p>
              <p className="text-primary-100 mt-2">Across all your accounts</p>
            </div>
            <DollarSign className="h-16 w-16 text-primary-100" />
          </div>
        </div>

        {/* Key Insights */}
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-700">Largest Purchase</p>
                <h4 className="text-2xl font-semibold text-accent-red mt-2">
                  {largestPurchase ? formatCurrency(-largestPurchase.amount) : "—"}
                </h4>
              </div>
              <div className="h-12 w-12 rounded-full bg-accent-red/10 flex items-center justify-center">
                <ArrowDownRight className="h-6 w-6 text-accent-red" />
              </div>
            </div>
            <p className="text-sm text-dark-900 mt-3">
              {largestPurchase
                ? `${largestPurchase.description} on ${largestPurchase.purchase_date}`
                : "We haven't seen any purchases this month."}
            </p>
          </div>

          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-700">Largest Deposit</p>
                <h4 className="text-2xl font-semibold text-emerald-300 mt-2">
                  {largestDeposit ? formatCurrency(largestDeposit.amount) : "—"}
                </h4>
              </div>
              <div className="h-12 w-12 rounded-full bg-emerald-500/10 flex items-center justify-center">
                <ArrowUpRight className="h-6 w-6 text-emerald-300" />
              </div>
            </div>
            <p className="text-sm text-dark-900 mt-3">
              {largestDeposit
                ? `${largestDeposit.description} on ${largestDeposit.transaction_date}`
                : "Add a deposit to start tracking your income."}
            </p>
          </div>

          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-700">Spending Trend</p>
                <h4 className="text-2xl font-semibold text-white mt-2">
                  {spendingTrend
                    ? spendingTrend.direction === "flat"
                      ? "Holding steady"
                      : `${spendingTrend.direction === "up" ? "Up" : "Down"} ${spendingTrend.percentage.toFixed(1)}%`
                    : "Not enough data"}
                </h4>
              </div>
              <div className="h-12 w-12 rounded-full bg-primary-500/10 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-primary-300" />
              </div>
            </div>
            <p className="text-sm text-dark-900 mt-3">
              {spendingTrend
                ? spendingTrend.direction === "flat"
                  ? "You're spending about the same as last month."
                  : spendingTrend.direction === "up"
                    ? "Spending is higher than last month—keep an eye on your budget."
                    : "Great work! You're spending less than last month."
                : "We need two months of transactions to spot a trend."}
            </p>
          </div>
        </div>

        {/* Income vs Expenses & Spending by Category */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Income vs Expenses (This Month) */}
          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2 text-primary-500" />
              Income vs Expenses (This Month)
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-emerald-500/10 rounded-lg">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-6 w-6 text-emerald-400" />
                  <span className="font-medium text-white">Income</span>
                </div>
                <span className="text-lg font-semibold text-emerald-300">+${income.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-accent-red/10 rounded-lg">
                <div className="flex items-center space-x-3">
                  <TrendingDown className="h-6 w-6 text-accent-red" />
                  <span className="font-medium text-white">Expenses</span>
                </div>
                <span className="text-lg font-semibold text-accent-red">-${expenses.toFixed(2)}</span>
              </div>
              <div className="border-t border-dark-400 pt-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">Net Income</span>
                  <span className={`text-lg font-bold ${income - expenses >= 0 ? 'text-emerald-300' : 'text-accent-red'}`}>
                    ${(income - expenses).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Spending by Category */}
          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <PieChart className="h-5 w-5 mr-2 text-purple-400" />
              Spending by Category
            </h3>
            <div className="space-y-3">
              {spendingByCategory.map((category, index) => {
                const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500'];
                const percentage = expenses > 0 ? (category.amount / expenses) * 100 : 0;

                return (
                  <button
                    key={category.name}
                    onClick={() => setSelectedCategory(prev => (prev === category.name ? null : category.name))}
                    className={`flex items-center space-x-3 w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      selectedCategory === category.name ? 'bg-dark-300' : 'hover:bg-dark-300/70'
                    }`}
                  >
                    <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`}></div>
                    <div className="flex-1 flex justify-between items-center">
                      <span className="text-dark-900 font-medium">{category.name}</span>
                      <div className="text-right">
                        <span className="text-white font-semibold">${category.amount.toFixed(2)}</span>
                        <span className="text-sm text-dark-800 ml-2">({percentage.toFixed(1)}%)</span>
                      </div>
                    </div>
                  </button>
                );
              })}
              {spendingByCategory.length === 0 && (
                <p className="text-dark-900 text-center py-4">No spending data available</p>
              )}
            </div>
          </div>
        </div>

        {/* Balance Line (30d) & Recent Transactions */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Balance Line (30d) */}
          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-emerald-400" />
              Balance Line (30 Days)
            </h3>
            <div className="h-40 flex items-end space-x-1">
              {balanceData.slice(-15).map((data, index) => {
                const maxBalance = Math.max(...balanceData.map(d => d.balance));
                const height = (data.balance / maxBalance) * 100;

                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="bg-gradient-to-t from-primary-500 to-primary-300 rounded-sm w-full"
                      style={{ height: `${height}%`, minHeight: '4px' }}
                    ></div>
                    <span className="text-xs text-dark-800 mt-1 transform rotate-45 origin-bottom-left">
                      {data.date.split('/')[1]}/{data.date.split('/')[0]}
                    </span>
                  </div>
                );
              })}
            </div>
            <p className="text-sm text-dark-900 mt-2 text-center">
              Current: ${balanceData[balanceData.length - 1]?.balance.toFixed(2)}
            </p>
          </div>

          {/* Recent Transactions (interactive) */}
          <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-primary-500" />
                Recent Transactions
              </h3>
              {selectedCategory && (
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="text-xs text-primary-300 hover:text-primary-200"
                >
                  Clear filter
                </button>
              )}
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {filteredTransactions.slice(0, 25).map((transaction, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedTransaction(transaction)}
                  className="w-full text-left flex justify-between items-center py-2 px-3 border border-dark-400 rounded-lg hover:bg-dark-300 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      transaction.transaction_date ? 'bg-emerald-400' : 'bg-accent-red'
                    }`}></div>
                    <div>
                      <p className="font-medium text-white text-sm">{transaction.description}</p>
                      <p className="text-xs text-dark-900">
                        {transaction.transaction_date || transaction.purchase_date}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold text-sm ${
                      transaction.transaction_date ? "text-emerald-300" : "text-accent-red"
                    }`}>
                      {transaction.transaction_date ? "+" : "-"}${Math.abs(transaction.amount).toFixed(2)}
                    </p>
                  </div>
                </button>
              ))}
              {filteredTransactions.length === 0 && (
                <p className="text-dark-900 text-center py-8">No transactions found</p>
              )}
            </div>
          </div>
        </div>

        {/* AP2 Automations Summary */}
        <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="h-12 w-12 rounded-full bg-purple-500/10 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-purple-300" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Autonomous AP2 Automations</h3>
              <p className="text-dark-900 mt-1">
                You have <span className="text-white font-semibold">{ap2Summary.active_count}</span> active automations and
                <span className="text-white font-semibold"> {ap2Summary.pending_count}</span> awaiting approval.
                They're managing roughly {formatCurrency(ap2Summary.estimated_savings)} each month.
              </p>
            </div>
          </div>
          <button
            onClick={() => nav("/trust-agent")}
            className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-200 rounded-lg transition-colors"
          >
            Review automations
          </button>
        </div>

        {/* Quick Actions */}
        <div className="bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 bg-primary-500/10 hover:bg-primary-500/20 rounded-lg text-center transition-colors">
              <div className="text-primary-300 font-semibold">View All Transactions</div>
            </button>
            <button
              onClick={() => setShowDepositModal(true)}
              className="p-4 bg-emerald-500/10 hover:bg-emerald-500/20 rounded-lg text-center transition-colors"
            >
              <div className="text-emerald-300 font-semibold">Add Deposit</div>
            </button>
            <button
              onClick={() => setShowPurchaseModal(true)}
              className="p-4 bg-accent-gold/10 hover:bg-accent-gold/20 rounded-lg text-center transition-colors"
            >
              <div className="text-accent-gold font-semibold">Make Purchase</div>
            </button>
            <button
              onClick={() => nav("/chat")}
              className="p-4 bg-purple-500/10 hover:bg-purple-500/20 rounded-lg text-center transition-colors"
            >
              <div className="text-purple-300 font-semibold">Ask AI Assistant</div>
            </button>
          </div>
        </div>
      </div>

      {showDepositModal && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center px-4 py-8 z-50"
          onClick={() => setShowDepositModal(false)}
        >
          <form
            onSubmit={handleSubmitDeposit}
            onClick={event => event.stopPropagation()}
            className="w-full max-w-md bg-dark-200 border border-dark-400 rounded-2xl shadow-2xl p-6 space-y-4"
          >
            <div className="flex justify-between items-center">
              <h4 className="text-xl font-semibold text-white">Add a Deposit</h4>
              <button
                type="button"
                onClick={() => setShowDepositModal(false)}
                className="text-dark-900 hover:text-white"
              >
                Close
              </button>
            </div>
            <div className="space-y-4">
              <label className="block text-sm text-dark-800">
                Amount
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={depositForm.amount}
                  onChange={event => setDepositForm(prev => ({ ...prev, amount: event.target.value }))}
                  className="mt-1 w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  required
                />
              </label>
              <label className="block text-sm text-dark-800">
                Description
                <input
                  type="text"
                  value={depositForm.description}
                  onChange={event => setDepositForm(prev => ({ ...prev, description: event.target.value }))}
                  placeholder="Paycheck, refund, etc."
                  className="mt-1 w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </label>
              <label className="block text-sm text-dark-800">
                Date
                <input
                  type="date"
                  value={depositForm.date}
                  onChange={event => setDepositForm(prev => ({ ...prev, date: event.target.value }))}
                  className="mt-1 w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  required
                />
              </label>
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowDepositModal(false)}
                className="px-4 py-2 bg-dark-300 text-dark-900 rounded-lg hover:bg-dark-400"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading === "deposit"}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg flex items-center gap-2 disabled:opacity-70"
              >
                {actionLoading === "deposit" && <Loader2 className="h-4 w-4 animate-spin" />}Save Deposit
              </button>
            </div>
          </form>
        </div>
      )}

      {showPurchaseModal && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center px-4 py-8 z-50"
          onClick={() => setShowPurchaseModal(false)}
        >
          <form
            onSubmit={handleSubmitPurchase}
            onClick={event => event.stopPropagation()}
            className="w-full max-w-md bg-dark-200 border border-dark-400 rounded-2xl shadow-2xl p-6 space-y-4"
          >
            <div className="flex justify-between items-center">
              <h4 className="text-xl font-semibold text-white">Log a Purchase</h4>
              <button
                type="button"
                onClick={() => setShowPurchaseModal(false)}
                className="text-dark-900 hover:text-white"
              >
                Close
              </button>
            </div>
            <div className="space-y-4">
              <label className="block text-sm text-dark-800">
                Amount
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={purchaseForm.amount}
                  onChange={event => setPurchaseForm(prev => ({ ...prev, amount: event.target.value }))}
                  className="mt-1 w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  required
                />
              </label>
              <label className="block text-sm text-dark-800">
                Description
                <input
                  type="text"
                  value={purchaseForm.description}
                  onChange={event => setPurchaseForm(prev => ({ ...prev, description: event.target.value }))}
                  placeholder="Merchant, memo, or notes"
                  className="mt-1 w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                />
              </label>
              <label className="block text-sm text-dark-800">
                Date
                <input
                  type="date"
                  value={purchaseForm.date}
                  onChange={event => setPurchaseForm(prev => ({ ...prev, date: event.target.value }))}
                  className="mt-1 w-full px-4 py-3 border border-dark-400 bg-dark-300 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  required
                />
              </label>
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowPurchaseModal(false)}
                className="px-4 py-2 bg-dark-300 text-dark-900 rounded-lg hover:bg-dark-400"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading === "purchase"}
                className="px-4 py-2 bg-accent-gold/90 hover:bg-accent-gold text-dark-100 rounded-lg flex items-center gap-2 disabled:opacity-70"
              >
                {actionLoading === "purchase" && <Loader2 className="h-4 w-4 animate-spin" />}Save Purchase
              </button>
            </div>
          </form>
        </div>
      )}

      {selectedTransaction && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center px-4 py-8 z-50">
          <div className="w-full max-w-lg bg-dark-200 border border-dark-400 rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-xl font-semibold text-white">Transaction Details</h4>
              <button
                onClick={() => setSelectedTransaction(null)}
                className="text-dark-900 hover:text-white"
              >
                Close
              </button>
            </div>
            <div className="space-y-3 text-sm text-dark-900">
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-700">Description</p>
                <p className="text-white text-base">{selectedTransaction.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs uppercase tracking-wide text-dark-700">Amount</p>
                  <p className={`text-lg font-semibold ${selectedTransaction.transaction_date ? 'text-emerald-300' : 'text-accent-red'}`}>
                    {selectedTransaction.transaction_date ? "+" : "-"}${Math.abs(selectedTransaction.amount).toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-dark-700">Type</p>
                  <p className="text-white">{selectedTransaction.transaction_date ? "Deposit" : "Purchase"}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-dark-700">Date</p>
                  <p className="text-white">{selectedTransaction.transaction_date || selectedTransaction.purchase_date}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-dark-700">Status</p>
                  <p className="text-white">{selectedTransaction.status || "posted"}</p>
                </div>
              </div>
              {selectedTransaction.merchant && (
                <div>
                  <p className="text-xs uppercase tracking-wide text-dark-700">Merchant</p>
                  <p className="text-white">{selectedTransaction.merchant?.name || selectedTransaction.merchant}</p>
                </div>
              )}
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-700">Account</p>
                <p className="text-white">{selectedTransaction.account_id || "Primary"}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-700">Category</p>
                <div className="mt-2 space-y-2">
                  <select
                    value={CATEGORY_OPTIONS.includes(categoryDraft) ? categoryDraft : "custom"}
                    onChange={event => {
                      const value = event.target.value;
                      if (value === "custom") return;
                      setCategoryDraft(value);
                    }}
                    className="w-full px-3 py-2 bg-dark-300 text-white border border-dark-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {CATEGORY_OPTIONS.map(option => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                    <option value="custom">Custom...</option>
                  </select>
                  <input
                    type="text"
                    value={categoryDraft}
                    onChange={event => setCategoryDraft(event.target.value)}
                    placeholder="Enter a category"
                    className="w-full px-3 py-2 bg-dark-300 text-white border border-dark-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3 pt-1">
                    <button
                      type="button"
                      onClick={handleSaveCategory}
                      disabled={categorySaving}
                      className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg flex items-center gap-2 disabled:opacity-70"
                    >
                      {categorySaving && <Loader2 className="h-4 w-4 animate-spin" />}Save Category
                    </button>
                    <button
                      type="button"
                      onClick={handleAskAIAboutTransaction}
                      className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-200 rounded-lg"
                    >
                      Ask AI About This
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}