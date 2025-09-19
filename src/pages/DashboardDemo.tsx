import { useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Flame,
  Loader2,
  Percent,
  RefreshCw,
  Sparkles,
  CreditCard,
  Link,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";

// Mock data for demo
const mockInflation = {
  personal_rate: 3.8,
  national_rate: 3.2,
  category_totals: {
    "Groceries": 420.50,
    "Gasoline": 180.30,
    "Restaurants": 250.75,
    "Utilities": 150.00,
    "Shopping": 120.45,
  },
  total_spend: 1121.00,
  top_drivers: ["Groceries", "Restaurants", "Gasoline"]
};

const mockTransactions = [
  {
    transaction_id: "demo-1",
    name: "H-E-B #443",
    merchant_name: "H-E-B",
    amount: 86.23,
    date: "2024-03-15",
    category: "Groceries"
  },
  {
    transaction_id: "demo-2", 
    name: "Shell Oil 23891",
    merchant_name: "Shell",
    amount: 42.18,
    date: "2024-03-14",
    category: "Gasoline"
  },
  {
    transaction_id: "demo-3",
    name: "Netflix",
    merchant_name: "Netflix", 
    amount: 15.99,
    date: "2024-03-12",
    category: "Entertainment"
  }
];

export default function DashboardDemo() {
  const [plaidLinked, setPlaidLinked] = useState(false);
  const [creditCardRecommendation, setCreditCardRecommendation] = useState<string | null>(null);
  const [loadingRecommendation, setLoadingRecommendation] = useState(false);

  const renderRateBadge = (value: number | null, label: string) => {
    if (value === null || Number.isNaN(value)) {
      return (
        <div className="flex items-center gap-2 text-dark-200 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Calculating {label}
        </div>
      );
    }

    const isHigh = value > 3.5;
    const IconComponent = isHigh ? ArrowUpRight : ArrowDownRight;
    const colorClass = isHigh ? "text-red-400" : "text-green-400";

    return (
      <div className={`flex items-center gap-1 ${colorClass} text-lg font-medium`}>
        <IconComponent className="w-5 h-5" />
        {value.toFixed(1)}%
      </div>
    );
  };

  const handlePlaidLink = () => {
    setPlaidLinked(true);
  };

  const loadCreditCardRecommendation = () => {
    setLoadingRecommendation(true);
    setTimeout(() => {
      setCreditCardRecommendation(`🎯 **Chase Sapphire Preferred Credit Card**

Based on your spending patterns, this card is perfect for you:

**Why it's ideal:**
- **3x points** on dining (your #2 spending category: $250.75/month)  
- **2x points** on travel and gas
- **1x points** on everything else including groceries

**Value for your spending:**
- Monthly dining: $250.75 × 3 = 752 points
- Monthly gas: $180.30 × 2 = 361 points  
- Other spending: $690 × 1 = 690 points
- **Total: ~1,803 points/month** (worth ~$18-36/month in travel)

**Key Benefits:**
- 60,000 point sign-up bonus (worth $750+ in travel)
- 1:1 transfer to airline/hotel partners
- No foreign transaction fees
- $95 annual fee (easily offset by rewards)

With your $1,121 monthly spending, you could earn $200-400+ in travel rewards annually!`);
      setLoadingRecommendation(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-500 via-dark-400 to-dark-300 text-white">
      <div className="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard Demo</h1>
          <p className="text-dark-200">Demonstrating new Plaid Link and AI Credit Card Recommender features</p>
        </div>

        {/* Inflation Overview */}
        <div className="grid gap-6 md:grid-cols-3 mb-8">
          <Card className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-dark-200">Personal inflation</CardTitle>
              <Flame className="w-4 h-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              {renderRateBadge(mockInflation.personal_rate, "personal rate")}
              <p className="text-xs text-dark-200 mt-1">vs national {mockInflation.national_rate}%</p>
            </CardContent>
          </Card>

          <Card className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-dark-200">Monthly spending</CardTitle>
              <BarChart3 className="w-4 h-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${mockInflation.total_spend.toFixed(2)}</div>
              <p className="text-xs text-dark-200 mt-1">across all categories</p>
            </CardContent>
          </Card>

          <Card className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-dark-200">Top drivers</CardTitle>
              <Percent className="w-4 h-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium">
                {mockInflation.top_drivers.join(", ")}
              </div>
              <p className="text-xs text-dark-200 mt-1">biggest impact categories</p>
            </CardContent>
          </Card>
        </div>

        {/* New Features Demo */}
        <div className="grid gap-6 md:grid-cols-2 mb-8">
          
          {/* Plaid Link Card */}
          <Card className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader>
              <CardTitle className="text-white text-xl flex items-center gap-2">
                <Link className="w-5 h-5" />
                Bank Account Connection
              </CardTitle>
              <p className="text-white/80 text-sm">Connect your bank account for personalized inflation insights</p>
            </CardHeader>
            <CardContent className="space-y-4">
              {plaidLinked ? (
                <div className="flex items-center gap-2 text-green-400">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm">Bank account connected</span>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-dark-200 text-sm">
                    Link your bank account to get real-time transaction data and personalized AI financial insights.
                  </p>
                  <button
                    onClick={handlePlaidLink}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm transition disabled:opacity-60"
                  >
                    <Link className="w-4 h-4" />
                    Connect Bank Account (Demo)
                  </button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Credit Card Recommender Card */}
          <Card className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader>
              <CardTitle className="text-white text-xl flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                AI Credit Card Recommender
              </CardTitle>
              <p className="text-white/80 text-sm">Get personalized credit card recommendations based on your spending</p>
            </CardHeader>
            <CardContent className="space-y-4">
              {!plaidLinked ? (
                <p className="text-dark-200 text-sm">
                  Connect your bank account to get AI-powered credit card recommendations based on your spending patterns.
                </p>
              ) : (
                <div className="space-y-3">
                  <button
                    onClick={loadCreditCardRecommendation}
                    disabled={loadingRecommendation}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm transition disabled:opacity-60"
                  >
                    {loadingRecommendation ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4" />
                    )}
                    {loadingRecommendation ? "Analyzing..." : "Get AI Recommendation"}
                  </button>
                  
                  {creditCardRecommendation && (
                    <div className="mt-4 p-4 bg-dark-300/50 rounded-lg border border-dark-400">
                      <h4 className="text-white font-medium mb-2">🎯 Personalized Recommendation</h4>
                      <div className="text-sm text-white/90 whitespace-pre-wrap">
                        {creditCardRecommendation}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Transactions Demo */}
        <Card className="bg-dark-200/40 border border-dark-400/60 mb-8">
          <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle className="text-white text-xl">Recent transactions (Demo Data)</CardTitle>
              <p className="text-white/80 text-sm">Sample transaction data to show categorization</p>
            </div>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="text-white border-b border-dark-400/40">
                  <th className="py-3 pr-4 font-medium">Merchant</th>
                  <th className="py-3 pr-4 font-medium">Date</th>
                  <th className="py-3 pr-4 font-medium">Amount</th>
                  <th className="py-3 pr-4 font-medium">Category</th>
                </tr>
              </thead>
              <tbody>
                {mockTransactions.map((tx) => (
                  <tr key={tx.transaction_id} className="text-white/90 border-b border-dark-400/20">
                    <td className="py-3 pr-4 font-medium">{tx.merchant_name || tx.name}</td>
                    <td className="py-3 pr-4 text-dark-200">{tx.date}</td>
                    <td className="py-3 pr-4">${tx.amount.toFixed(2)}</td>
                    <td className="py-3 pr-4">
                      <span className="inline-flex items-center rounded-full bg-primary-500/20 px-2.5 py-0.5 text-xs font-medium text-primary-300">
                        {tx.category}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        {/* Category Breakdown */}
        <Card className="bg-dark-200/40 border border-dark-400/60">
          <CardHeader>
            <CardTitle className="text-white text-xl">Spending by category</CardTitle>
            <p className="text-white/80 text-sm">Your inflation model at a glance</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(mockInflation.category_totals)
                .sort((a, b) => b[1] - a[1])
                .map(([category, value]) => (
                  <div key={category} className="flex items-center gap-3">
                    <div className="w-24 text-white font-medium">{category}</div>
                    <div className="flex-1 h-2 bg-dark-400/40 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-500 to-primary-300"
                        style={{ width: `${Math.min(100, (value / mockInflation.total_spend) * 100)}%` }}
                      />
                    </div>
                    <span>${value.toFixed(2)}</span>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}