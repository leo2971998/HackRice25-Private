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
      
      // Load AP2 mandates
      const mandatesResponse = await fetch("/api/ap2/mandates", {
        credentials: "include"
      });
      
      if (mandatesResponse.ok) {
        const mandatesData = await mandatesResponse.json();
        setMandates(mandatesData.mandates || []);
      }

      // Load smart finance dashboard
      const statsResponse = await fetch("/api/smart-finance/dashboard", {
        credentials: "include"
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }
      
    } catch (error) {
      console.error("Failed to load TrustAgent dashboard:", error);
      toast.error("Failed to load dashboard data");
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
    } catch (error) {
      toast.error("Failed to create savings goal");
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
    } catch (error) {
      toast.error("Failed to create budget alert");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "executed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "approved":
        return <Zap className="h-5 w-5 text-blue-500" />;
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200";
      case "medium":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "positive":
        return "text-green-600 bg-green-50 border-green-200";
      default:
        return "text-blue-600 bg-blue-50 border-blue-200";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">TrustAgent</h1>
              <p className="text-gray-600">Your AP2-Powered Financial Co-Pilot</p>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <Shield className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Mandates</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.active_mandates || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <Zap className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Automations</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.ap2_stats?.active_automations || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <Target className="h-8 w-8 text-purple-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Mandates</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.ap2_stats?.total_mandates || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <Lock className="h-8 w-8 text-orange-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-gray-900">
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
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                AI Financial Insights
              </h2>
              
              {stats?.insights && stats.insights.length > 0 ? (
                <div className="space-y-3">
                  {stats.insights.map((insight, index) => (
                    <div 
                      key={index}
                      className={`p-4 rounded-lg border ${getPriorityColor(insight.priority)}`}
                    >
                      <p className="font-medium mb-1">{insight.message}</p>
                      <p className="text-sm opacity-75">{insight.action}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No insights available. Start by creating some mandates!</p>
              )}
            </div>

            {/* AP2 Mandates */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  AP2 Mandates
                </h2>
                <button
                  onClick={() => setShowCreateMandate(!showCreateMandate)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="h-4 w-4" />
                  Create Mandate
                </button>
              </div>

              {showCreateMandate && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h3 className="font-medium text-gray-900 mb-3">Quick Actions</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      onClick={createSavingsGoal}
                      className="flex items-center gap-2 p-3 bg-green-100 text-green-800 rounded-lg hover:bg-green-200 transition-colors"
                    >
                      <Target className="h-4 w-4" />
                      Auto-Save $500/month
                    </button>
                    <button
                      onClick={createBudgetAlert}
                      className="flex items-center gap-2 p-3 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 transition-colors"
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
                    <div key={mandate.id} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(mandate.status)}
                          <span className="font-medium text-gray-900 capitalize">
                            {mandate.type} Mandate
                          </span>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                          mandate.status === 'executed' ? 'bg-green-100 text-green-800' :
                          mandate.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                          mandate.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {mandate.status}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600">
                        <p><strong>Intent:</strong> {mandate.data?.intent_type || mandate.data?.purpose || "Financial automation"}</p>
                        {mandate.data?.amount && (
                          <p><strong>Amount:</strong> ${mandate.data.amount}</p>
                        )}
                        <p><strong>Created:</strong> {new Date(mandate.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Shield className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500 mb-4">No AP2 mandates yet</p>
                  <p className="text-sm text-gray-400">Create your first mandate to start autonomous financial management</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            
            {/* AP2 Features */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Bot className="h-5 w-5 text-blue-600" />
                AP2 Features
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                  <Shield className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">Secure Mandates</p>
                    <p className="text-xs text-gray-600">Cryptographically signed</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                  <Zap className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="font-medium text-gray-900">Auto-Execution</p>
                    <p className="text-xs text-gray-600">Autonomous operations</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                  <Target className="h-5 w-5 text-purple-600" />
                  <div>
                    <p className="font-medium text-gray-900">Smart Goals</p>
                    <p className="text-xs text-gray-600">AI-powered recommendations</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Settings className="h-5 w-5 text-gray-600" />
                Quick Actions
              </h3>
              
              <div className="space-y-2">
                <button 
                  onClick={() => nav("/dashboard")}
                  className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <DollarSign className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">View Dashboard</span>
                  </div>
                </button>
                
                <button 
                  onClick={() => nav("/chat")}
                  className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Bot className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">AI Assistant</span>
                  </div>
                </button>
                
                <button 
                  onClick={() => nav("/learn")}
                  className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Target className="h-4 w-4 text-purple-600" />
                    <span className="text-sm font-medium">Financial Learning</span>
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