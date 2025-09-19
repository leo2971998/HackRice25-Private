import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Flame,
  Loader2,
  Percent,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import toast from "react-hot-toast";

import {
  fetchTransactions,
  overrideTransactionCategory,
  fetchPersonalInflation,
  submitReceipt,
  type PersonalInflationSnapshot,
  type TransactionRecord,
} from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";
import { useAuth } from "@/context/Auth";

const CATEGORY_OPTIONS = [
  "Groceries",
  "Gasoline",
  "Restaurants",
  "Utilities",
  "Housing",
  "Shopping",
  "Entertainment",
  "Travel",
  "Healthcare",
  "Income",
  "Other",
];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [transactions, setTransactions] = useState<TransactionRecord[]>([]);
  const [overrides, setOverrides] = useState<Record<string, string>>({});
  const [inflation, setInflation] = useState<PersonalInflationSnapshot | null>(null);
  const [receiptSummary, setReceiptSummary] = useState<string | null>(null);
  const [receiptItems, setReceiptItems] = useState<string>("");
  const [receiptTotal, setReceiptTotal] = useState<string>("");
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  const loadDashboard = async (refresh = false) => {
    try {
      setUpdating(true);
      const [tx, inflationSnapshot] = await Promise.all([
        fetchTransactions(),
        fetchPersonalInflation(refresh),
      ]);
      setTransactions(tx.transactions || []);
      setOverrides(tx.overrides || {});
      setInflation(inflationSnapshot);
    } catch (error) {
      toast.error("Unable to load latest spending data");
    } finally {
      setLoading(false);
      setUpdating(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const categoryTotals = useMemo(() => inflation?.category_totals || {}, [inflation]);
  const personalRate = inflation?.personal_rate ?? null;
  const nationalRate = inflation?.national_rate ?? null;

  const handleOverride = async (transactionId: string, category: string) => {
    try {
      await overrideTransactionCategory(transactionId, category);
      toast.success("Category updated");
      await loadDashboard(true);
    } catch (error) {
      toast.error("Failed to update category");
    }
  };

  const submitReceiptForAnalysis = async (event: React.FormEvent) => {
    event.preventDefault();
    const items = receiptItems
      .split("\n")
      .map(line => line.trim())
      .filter(Boolean);
    const total = parseFloat(receiptTotal);
    if (!items.length || Number.isNaN(total)) {
      toast.error("Add line items and a numeric total");
      return;
    }
    try {
      const { summary } = await submitReceipt(items, total);
      setReceiptSummary(summary);
      toast.success("Receipt analysed");
    } catch (error) {
      toast.error("Could not analyse receipt");
    }
  };

  const renderRateBadge = (value: number | null, label: string) => {
    if (value === null || Number.isNaN(value)) {
      return (
        <div className="flex items-center gap-2 text-dark-900 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Calculating {label}
        </div>
      );
    }

    const rising = value > (nationalRate ?? value);
    return (
      <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${rising ? "bg-red-500/20 text-red-300" : "bg-emerald-500/20 text-emerald-300"}`}>
        {rising ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
        <span>{value.toFixed(2)}%</span>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-white">Welcome back{user?.first_name ? `, ${user.first_name}` : ""}</h1>
          <p className="text-dark-900">Here is the latest snapshot of your personal inflation.</p>
        </div>
        <button
          onClick={() => loadDashboard(true)}
          disabled={updating}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-dark-400 text-white hover:border-primary-500 hover:text-primary-200 transition disabled:opacity-60"
        >
          {updating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Refresh data
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="bg-dark-200/60 border border-dark-400/60">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2 text-lg">
              <Percent className="w-5 h-5 text-primary-400" />
              Personal inflation
            </CardTitle>
            {renderRateBadge(personalRate, "personal inflation")}
          </CardHeader>
          <CardContent className="space-y-3 text-dark-900">
            <p>
              National CPI: <span className="text-white font-semibold">{nationalRate !== null ? `${nationalRate.toFixed(2)}%` : "Loading"}</span>
            </p>
            <p className="text-sm text-dark-800">
              Weighted using the last 30 days of your spending, mapped directly to Bureau of Labor Statistics categories.
            </p>
          </CardContent>
        </Card>

        <Card className="bg-dark-200/60 border border-dark-400/60">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2 text-lg">
              <Flame className="w-5 h-5 text-orange-400" />
              Top pressure points
            </CardTitle>
            <Sparkles className="w-5 h-5 text-orange-300" />
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-dark-900 text-sm">
              {(inflation?.top_drivers || []).length ? (
                inflation!.top_drivers.map(driver => (
                  <li key={driver} className="flex justify-between">
                    <span className="text-white">{driver}</span>
                    <span>${categoryTotals[driver]?.toFixed(2) ?? "0.00"}</span>
                  </li>
                ))
              ) : (
                <li className="text-dark-800">Not enough data yet. Refresh after more transactions sync.</li>
              )}
            </ul>
          </CardContent>
        </Card>

        <Card className="bg-dark-200/60 border border-dark-400/60">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2 text-lg">
              <BarChart3 className="w-5 h-5 text-emerald-400" />
              Category mix
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(categoryTotals).length ? (
              <div className="space-y-2 text-sm text-dark-900">
                {Object.entries(categoryTotals)
                  .sort((a, b) => b[1] - a[1])
                  .map(([category, value]) => (
                    <div key={category} className="flex items-center gap-3">
                      <div className="w-24 text-white font-medium">{category}</div>
                      <div className="flex-1 h-2 bg-dark-400/40 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500 to-primary-300"
                          style={{ width: `${Math.min(100, (value / (inflation?.total_spend || 1)) * 100)}%` }}
                        />
                      </div>
                      <span>${value.toFixed(2)}</span>
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-dark-800 text-sm">We are waiting on transactions from your institution.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <CardTitle className="text-white text-xl">Recent transactions</CardTitle>
            <p className="text-dark-900 text-sm">Override categories to fine tune your inflation model.</p>
          </div>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="text-dark-800 border-b border-dark-400/40">
                <th className="py-3 pr-4 font-medium">Merchant</th>
                <th className="py-3 pr-4 font-medium">Date</th>
                <th className="py-3 pr-4 font-medium">Amount</th>
                <th className="py-3 pr-4 font-medium">Category</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-dark-800">
                    <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                  </td>
                </tr>
              ) : transactions.length ? (
                transactions.map(tx => (
                  <tr key={tx.transaction_id} className="border-b border-dark-400/30 last:border-0">
                    <td className="py-3 pr-4 text-white">{tx.merchant_name || tx.name}</td>
                    <td className="py-3 pr-4 text-dark-900">{new Date(tx.date).toLocaleDateString()}</td>
                    <td className="py-3 pr-4 text-white">${tx.amount.toFixed(2)}</td>
                    <td className="py-3 pr-4">
                      <select
                        value={overrides[tx.transaction_id] || tx.category}
                        onChange={event => handleOverride(tx.transaction_id, event.target.value)}
                        className="bg-dark-300/60 border border-dark-400 rounded-lg px-3 py-2 text-sm text-white"
                      >
                        {CATEGORY_OPTIONS.map(option => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-dark-800">
                    No recent transactions found. Make a purchase and refresh to see the magic.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader>
          <CardTitle className="text-white text-xl">Receipt intelligence</CardTitle>
          <p className="text-dark-900 text-sm">Paste grocery line items to see how Gemini Vision narrates the spend.</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={submitReceiptForAnalysis} className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <label className="text-sm text-dark-900 font-medium">Receipt items (one per line)</label>
              <textarea
                value={receiptItems}
                onChange={event => setReceiptItems(event.target.value)}
                className="w-full min-h-[160px] rounded-xl bg-dark-300/60 border border-dark-400 px-4 py-3 text-sm text-white focus:border-primary-500 focus:outline-none"
                placeholder={"Organic apples\nRotisserie chicken\nSparkling water"}
              />
            </div>
            <div className="space-y-4">
              <div className="space-y-3">
                <label className="text-sm text-dark-900 font-medium">Total</label>
                <input
                  value={receiptTotal}
                  onChange={event => setReceiptTotal(event.target.value)}
                  type="number"
                  step="0.01"
                  min="0"
                  className="w-full rounded-xl bg-dark-300/60 border border-dark-400 px-4 py-3 text-sm text-white focus:border-primary-500 focus:outline-none"
                  placeholder="123.45"
                />
              </div>
              <button
                type="submit"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm transition"
              >
                Analyse receipt
              </button>
              {receiptSummary && (
                <div className="rounded-xl bg-dark-300/50 border border-dark-400 px-4 py-3 text-sm text-dark-900">
                  {receiptSummary}
                </div>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
