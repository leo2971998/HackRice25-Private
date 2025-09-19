// src/pages/TrustAgentPage.tsx
import { useEffect, useState } from "react";
import { useAuth } from "@/context/Auth";
import { useNavigate } from "react-router-dom";
import {
  Shield,
  Zap,
  Target,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  Bot,
  Lock,
  CheckCircle,
  Clock,
  Plus,
  Settings
} from "lucide-react";
import toast from "react-hot-toast";
import { approveMandate, cancelMandate, executeMandate } from "@/api/client";
import { SkeletonGroup } from "@/components/Skeleton";

interface AP2Mandate {
  id: string;
  type: string;
  status: string;
  data: any;
  created_at: string;
  expires_at: string;
  is_valid: boolean;
}

interface SmartFinanceStats {
  ap2_stats: {
    total_mandates: number;
    active_automations: number;
    pending_approvals: number;
  };
  active_mandates: number;
  insights: Array<{
    type: string;
    message: string;
    action: string;
    priority: string;
  }>;
}

export default function TrustAgentPage() {
  const [mandates, setMandates] = useState<AP2Mandate[]>([]);
  const [stats, setStats] = useState<SmartFinanceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateMandate, setShowCreateMandate] = useState(false);
  const { user } = useAuth();
  const nav = useNavigate();

  useEffect(() => {
    if (!user) {
      nav("/login");
      return;
    }
    loadDashboardData();
  }, [user, nav]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      const [mandatesResponse, statsResponse] = await Promise.all([
        fetch("/api/ap2/mandates", { credentials: "include" }),
        fetch("/api/smart-finance/dashboard", { credentials: "include" })
      ]);

      if (!mandatesResponse.ok) {
        const errorData = await mandatesResponse.json().catch(() => ({}));
        throw new Error(errorData.error || "Unable to load mandates");
      }

      if (!statsResponse.ok) {
        const errorData = await statsResponse.json().catch(() => ({}));
        throw new Error(errorData.error || "Unable to load insights");
      }

      const mandatesData = await mandatesResponse.json();
      const statsData = await statsResponse.json();

      setMandates(mandatesData.mandates || []);
      setStats(statsData);
    } catch (error: any) {
      toast.error(error?.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const createSavingsGoal = async () => {
    try {
      const response = await fetch("/api/ap2/mandates/intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          intent_type: "savings_goal",
          amount: 500,
          frequency: "monthly",
          goal_name: "Emergency Fund"
        })
      });

      if (response.ok) {
        toast.success("Savings automation created!");
        loadDashboardData();
      } else {
        throw new Error("Failed to create savings goal");
      }
    } catch (error: any) {
      toast.error(error?.message || "Failed to create savings goal");
    }
  };

  const createBudgetAlert = async () => {
    try {
      const response = await fetch("/api/smart-finance/budget/alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          category: "dining",
          monthly_limit: 400,
          alert_threshold: 0.8
        })
      });

      if (response.ok) {
        toast.success("Budget alert created!");
        loadDashboardData();
      } else {
        throw new Error("Failed to create budget alert");
      }
    } catch (error: any) {
      toast.error(error?.message || "Failed to create budget alert");
    }
  };

  const handleApprove = async (mandateId: string) => {
    try {
      const response = await approveMandate(mandateId);
      if (response.success) {
        toast.success(response.message || "Mandate approved");
        await loadDashboardData();
      } else {
        throw new Error(response.message || "Approval failed");
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.error || error?.message || "Unable to approve mandate");
    }
  };

  const handleExecute = async (mandateId: string) => {
    try {
      const response = await executeMandate(mandateId);
      if (response.success) {
        toast.success(response.message || "Mandate executed");
        await loadDashboardData();
      } else {
        throw new Error(response.message || response.execution_result?.error || "Execution failed");
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.error || error?.message || "Unable to execute mandate");
    }
  };

  const handleCancel = async (mandateId: string) => {
    try {
      const response = await cancelMandate(mandateId);
      if (response.success) {
        toast.success(response.message || "Mandate cancelled");
        await loadDashboardData();
      } else {
        throw new Error(response.message || "Cancellation failed");
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.error || error?.message || "Unable to cancel mandate");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "executed":
        return <CheckCircle className="h-5 w-5 text-emerald-400" />;
      case "approved":
        return <Zap className="h-5 w-5 text-primary-400" />;
      case "pending":
        return <Clock className="h-5 w-5 text-accent-gold" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-dark-700" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "text-accent-red bg-accent-red/10 border-accent-red/30";
      case "medium":
        return "text-accent-gold bg-accent-gold/10 border-accent-gold/30";
      case "positive":
        return "text-emerald-300 bg-emerald-500/10 border-emerald-500/20";
      default:
        return "text-primary-300 bg-primary-500/10 border-primary-500/20";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-100 flex items-center justify-center px-4">
        <div className="w-full max-w-4xl bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-8">
          <SkeletonGroup count={6} itemClassName="h-16 w-full bg-dark-300/70" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-100 text-white">
      <div className="w-full space-y-8">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">TrustAgent</h1>
              <p className="text-dark-900">Your AP2-Powered Financial Co-Pilot</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-dark-200 rounded-xl p-6 shadow-lg border border-dark-400">
              <div className="flex items-center gap-3">
                <Shield className="h-8 w-8 text-primary-500" />
                <div>
                  <p className="text-sm font-medium text-dark-900">Active Mandates</p>
                  <p className="text-2xl font-bold text-white">
                    {stats?.active_mandates || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-dark-200 rounded-xl p-6 shadow-lg border border-dark-400">
              <div className="flex items-center gap-3">
                <Zap className="h-8 w-8 text-emerald-500" />
                <div>
                  <p className="text-sm font-medium text-dark-900">Automations</p>
                  <p className="text-2xl font-bold text-white">
                    {stats?.ap2_stats?.active_automations || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-dark-200 rounded-xl p-6 shadow-lg border border-dark-400">
              <div className="flex items-center gap-3">
                <Target className="h-8 w-8 text-purple-400" />
                <div>
                  <p className="text-sm font-medium text-dark-900">Total Mandates</p>
                  <p className="text-2xl font-bold text-white">
                    {stats?.ap2_stats?.total_mandates || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-dark-200 rounded-xl p-6 shadow-lg border border-dark-400">
              <div className="flex items-center gap-3">
                <Lock className="h-8 w-8 text-accent-gold" />
                <div>
                  <p className="text-sm font-medium text-dark-900">Pending</p>
                  <p className="text-2xl font-bold text-white">
                    {stats?.ap2_stats?.pending_approvals || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* AI Insights */}
          <div className="lg:col-span-2">
            <div className="bg-dark-200 rounded-xl shadow-lg border border-dark-400 p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary-500" />
                AI Financial Insights
              </h2>

              {stats?.insights && stats.insights.length > 0 ? (
                <div className="space-y-3">
                  {stats.insights.map((insight, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${getPriorityColor(insight.priority)}`}
                    >
                      <p className="font-medium mb-1 text-white">{insight.message}</p>
                      <p className="text-sm text-dark-900">{insight.action}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-dark-900">No insights available. Start by creating some mandates!</p>
              )}
            </div>

            {/* AP2 Mandates */}
            <div className="bg-dark-200 rounded-xl shadow-lg border border-dark-400 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary-500" />
                  AP2 Mandates
                </h2>
                <button
                  onClick={() => setShowCreateMandate(!showCreateMandate)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  <Plus className="h-4 w-4" />
                  Create Mandate
                </button>
              </div>

              {showCreateMandate && (
                <div className="mb-6 p-4 bg-dark-300/60 rounded-lg border border-dark-400">
                  <h3 className="font-medium text-white mb-3">Quick Actions</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      onClick={createSavingsGoal}
                      className="flex items-center gap-2 p-3 bg-emerald-500/10 text-emerald-300 rounded-lg hover:bg-emerald-500/20 transition-colors"
                    >
                      <Target className="h-4 w-4" />
                      Auto-Save $500/month
                    </button>
                    <button
                      onClick={createBudgetAlert}
                      className="flex items-center gap-2 p-3 bg-accent-gold/10 text-accent-gold rounded-lg hover:bg-accent-gold/20 transition-colors"
                    >
                      <AlertTriangle className="h-4 w-4" />
                      Budget Alert ($400 dining)
                    </button>
                  </div>
                </div>
              )}

              {mandates.length > 0 ? (
                <div className="space-y-3">
                  {mandates.slice(0, 5).map((mandate) => (
                    <div key={mandate.id} className="p-4 border border-dark-400 rounded-lg bg-dark-300/60">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(mandate.status)}
                          <span className="font-medium text-white capitalize">
                            {mandate.type} Mandate
                          </span>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                          mandate.status === 'executed' ? 'bg-emerald-500/20 text-emerald-300' :
                          mandate.status === 'approved' ? 'bg-primary-500/20 text-primary-300' :
                          mandate.status === 'pending' ? 'bg-accent-gold/20 text-accent-gold' :
                          'bg-dark-400 text-dark-900'
                        }`}>
                          {mandate.status}
                        </span>
                      </div>

                      <div className="text-sm text-dark-900 space-y-1">
                        <p><strong>Intent:</strong> {mandate.data?.intent_type || mandate.data?.purpose || "Financial automation"}</p>
                        {mandate.data?.amount && (
                          <p><strong>Amount:</strong> ${mandate.data.amount}</p>
                        )}
                        <p><strong>Created:</strong> {new Date(mandate.created_at).toLocaleDateString()}</p>
                        {!mandate.is_valid && <p className="text-accent-red text-xs">Signature could not be verified</p>}
                      </div>

                      <div className="flex flex-wrap items-center gap-2 mt-4">
                        {mandate.status === "pending" && (
                          <>
                            <button
                              onClick={() => handleApprove(mandate.id)}
                              className="px-3 py-2 text-xs font-semibold bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleCancel(mandate.id)}
                              className="px-3 py-2 text-xs font-semibold bg-accent-red text-white rounded-lg hover:bg-red-600 transition-colors"
                            >
                              Cancel
                            </button>
                          </>
                        )}
                        {mandate.status === "approved" && (
                          <>
                            <button
                              onClick={() => handleExecute(mandate.id)}
                              className="px-3 py-2 text-xs font-semibold bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                            >
                              Execute
                            </button>
                            <button
                              onClick={() => handleCancel(mandate.id)}
                              className="px-3 py-2 text-xs font-semibold bg-accent-red text-white rounded-lg hover:bg-red-600 transition-colors"
                            >
                              Cancel
                            </button>
                          </>
                        )}
                        {mandate.status === "executed" && (
                          <span className="text-xs text-emerald-300 font-semibold">Automation complete</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Shield className="h-12 w-12 text-dark-700 mx-auto mb-3" />
                  <p className="text-dark-900 mb-4">No AP2 mandates yet</p>
                  <p className="text-sm text-dark-900">Create your first mandate to start autonomous financial management</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">

            {/* AP2 Features */}
            <div className="bg-dark-200 rounded-xl shadow-lg border border-dark-400 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary-500" />
                AP2 Features
              </h3>

              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-primary-500/10 rounded-lg">
                  <Shield className="h-5 w-5 text-primary-400" />
                  <div>
                    <p className="font-medium text-white">Secure Mandates</p>
                    <p className="text-xs text-dark-900">Cryptographically signed</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-emerald-500/10 rounded-lg">
                  <Zap className="h-5 w-5 text-emerald-400" />
                  <div>
                    <p className="font-medium text-white">Auto-Execution</p>
                    <p className="text-xs text-dark-900">Autonomous operations</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-purple-500/10 rounded-lg">
                  <Target className="h-5 w-5 text-purple-300" />
                  <div>
                    <p className="font-medium text-white">Smart Goals</p>
                    <p className="text-xs text-dark-900">AI-powered recommendations</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-dark-200 rounded-xl shadow-lg border border-dark-400 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Settings className="h-5 w-5 text-dark-900" />
                Quick Actions
              </h3>

              <div className="space-y-2">
                <button
                  onClick={() => nav("/dashboard")}
                  className="w-full text-left p-3 rounded-lg hover:bg-dark-300/70 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <DollarSign className="h-4 w-4 text-primary-500" />
                    <span className="text-sm font-medium text-white">View Dashboard</span>
                  </div>
                </button>

                <button
                  onClick={() => nav("/chat")}
                  className="w-full text-left p-3 rounded-lg hover:bg-dark-300/70 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Bot className="h-4 w-4 text-emerald-400" />
                    <span className="text-sm font-medium text-white">AI Assistant</span>
                  </div>
                </button>

                <button
                  onClick={() => nav("/learn")}
                  className="w-full text-left p-3 rounded-lg hover:bg-dark-300/70 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Target className="h-4 w-4 text-purple-400" />
                    <span className="text-sm font-medium text-white">Financial Learning</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}