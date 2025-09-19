import { useState } from "react";
import { BookOpen, TrendingUp, DollarSign, PieChart, Target, CheckCircle, Play, Award, Calculator, Lightbulb } from "lucide-react";

interface LessonProgress {
  [key: string]: boolean;
}

export default function LearnPage() {
  const [activeLesson, setActiveLesson] = useState<string | null>(null);
  const [lessonProgress, setLessonProgress] = useState<LessonProgress>({});
  const [budgetData, setBudgetData] = useState({
    income: 5000,
    housing: 1500,
    transportation: 600,
    food: 400,
    utilities: 200,
    savings: 500,
    entertainment: 300,
    other: 500
  });

  const lessons = [
    {
      id: "basics",
      title: "Budgeting Basics",
      description: "Learn the fundamentals of creating and managing a budget",
      icon: BookOpen,
      color: "from-blue-600 to-indigo-600",
      estimated: "5 min"
    },
    {
      id: "50-30-20",
      title: "50/30/20 Rule",
      description: "Master the popular budgeting method for balanced finances",
      icon: PieChart,
      color: "from-green-600 to-emerald-600",
      estimated: "7 min"
    },
    {
      id: "emergency-fund",
      title: "Emergency Fund",
      description: "Build financial security with proper emergency savings",
      icon: Target,
      color: "from-purple-600 to-pink-600",
      estimated: "6 min"
    },
    {
      id: "debt-management",
      title: "Debt Management",
      description: "Strategies to pay off debt efficiently and build wealth",
      icon: TrendingUp,
      color: "from-red-600 to-rose-600",
      estimated: "8 min"
    }
  ];

  const tips = [
    {
      icon: DollarSign,
      title: "Track Every Dollar",
      description: "Monitor all income and expenses to understand your spending patterns"
    },
    {
      icon: Calculator,
      title: "Use the 24-Hour Rule",
      description: "Wait 24 hours before making non-essential purchases over $50"
    },
    {
      icon: Target,
      title: "Set SMART Goals",
      description: "Create Specific, Measurable, Achievable, Relevant, Time-bound financial goals"
    },
    {
      icon: Lightbulb,
      title: "Automate Savings",
      description: "Set up automatic transfers to savings accounts to pay yourself first"
    }
  ];

  const completedLessons = Object.values(lessonProgress).filter(Boolean).length;
  const totalLessons = lessons.length;
  const progressPercentage = (completedLessons / totalLessons) * 100;

  const markLessonComplete = (lessonId: string) => {
    setLessonProgress(prev => ({ ...prev, [lessonId]: true }));
  };

  const calculateBudgetBreakdown = () => {
    const { income, housing, transportation, food, utilities, savings, entertainment, other } = budgetData;
    const totalExpenses = housing + transportation + food + utilities + savings + entertainment + other;
    const remaining = income - totalExpenses;
    
    return {
      totalExpenses,
      remaining,
      categories: [
        { name: "Housing", amount: housing, percentage: (housing / income) * 100, color: "bg-blue-500" },
        { name: "Transportation", amount: transportation, percentage: (transportation / income) * 100, color: "bg-green-500" },
        { name: "Food", amount: food, percentage: (food / income) * 100, color: "bg-yellow-500" },
        { name: "Utilities", amount: utilities, percentage: (utilities / income) * 100, color: "bg-purple-500" },
        { name: "Savings", amount: savings, percentage: (savings / income) * 100, color: "bg-emerald-500" },
        { name: "Entertainment", amount: entertainment, percentage: (entertainment / income) * 100, color: "bg-pink-500" },
        { name: "Other", amount: other, percentage: (other / income) * 100, color: "bg-indigo-500" }
      ]
    };
  };

  const budgetBreakdown = calculateBudgetBreakdown();

  return (
    <div className="min-h-screen bg-dark-100 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-dark-200 rounded-2xl shadow-xl p-6 border border-dark-400">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-full p-3">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Financial Learning Center</h1>
                <p className="text-dark-900">Master budgeting and financial planning skills</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2 text-emerald-300 bg-emerald-500/10 px-3 py-1 rounded-full mb-2">
                <Award className="h-4 w-4" />
                <span className="text-xs font-medium">{completedLessons}/{totalLessons} Complete</span>
              </div>
              <div className="w-32 bg-dark-400 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-600 to-emerald-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Tips */}
        <div className="bg-dark-200 rounded-2xl shadow-xl p-6 border border-dark-400">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
            <Lightbulb className="h-5 w-5 text-accent-gold" />
            <span>Quick Financial Tips</span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {tips.map((tip, index) => (
              <div key={index} className="p-4 bg-dark-300/60 rounded-xl border border-dark-400 hover:bg-dark-300/80 hover:shadow-md transition-all">
                <div className="flex items-center space-x-3 mb-2">
                  <tip.icon className="h-5 w-5 text-primary-400" />
                  <h3 className="font-semibold text-white text-sm">{tip.title}</h3>
                </div>
                <p className="text-xs text-dark-900">{tip.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Learning Modules */}
          <div className="bg-dark-200 rounded-2xl shadow-xl overflow-hidden border border-dark-400">
            <div className="bg-gradient-to-r from-primary-600 to-primary-500 px-6 py-4">
              <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                <Play className="h-5 w-5" />
                <span>Learning Modules</span>
              </h2>
            </div>
            
            <div className="p-6 space-y-4">
              {lessons.map((lesson) => (
                <div key={lesson.id} className="border-2 border-dark-400 rounded-xl p-4 hover:border-primary-500 transition-all bg-dark-300/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`bg-gradient-to-r ${lesson.color} rounded-lg p-2`}>
                        <lesson.icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-white flex items-center space-x-2">
                          <span>{lesson.title}</span>
                          {lessonProgress[lesson.id] && (
                            <CheckCircle className="h-4 w-4 text-emerald-400" />
                          )}
                        </h3>
                        <p className="text-sm text-dark-900">{lesson.description}</p>
                        <span className="text-xs text-primary-400 font-medium">{lesson.estimated} read</span>
                      </div>
                    </div>
                    <button 
                      onClick={() => {
                        setActiveLesson(activeLesson === lesson.id ? null : lesson.id);
                        if (!lessonProgress[lesson.id]) {
                          markLessonComplete(lesson.id);
                        }
                      }}
                      className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                        lessonProgress[lesson.id] 
                          ? 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30' 
                          : 'bg-primary-500/20 text-primary-300 hover:bg-primary-500/30'
                      }`}
                    >
                      {activeLesson === lesson.id ? 'Hide' : lessonProgress[lesson.id] ? 'Review' : 'Start'}
                    </button>
                  </div>
                  
                  {activeLesson === lesson.id && (
                    <div className="mt-4 p-4 bg-dark-400/50 rounded-lg">
                      {lesson.id === "basics" && (
                        <div className="space-y-3">
                          <h4 className="font-semibold text-white">Budgeting Fundamentals</h4>
                          <ul className="space-y-2 text-sm text-dark-900">
                            <li>• <strong>Track Income:</strong> Know exactly how much money comes in monthly</li>
                            <li>• <strong>List Expenses:</strong> Categorize all fixed and variable expenses</li>
                            <li>• <strong>Set Priorities:</strong> Distinguish between needs and wants</li>
                            <li>• <strong>Create Limits:</strong> Set spending limits for each category</li>
                            <li>• <strong>Review Regularly:</strong> Check and adjust your budget monthly</li>
                          </ul>
                        </div>
                      )}
                      {lesson.id === "50-30-20" && (
                        <div className="space-y-3">
                          <h4 className="font-semibold text-white">The 50/30/20 Rule</h4>
                          <div className="space-y-2 text-sm text-dark-900">
                            <div className="flex items-center space-x-2">
                              <div className="w-4 h-4 bg-blue-500 rounded"></div>
                              <span><strong>50% Needs:</strong> Housing, utilities, groceries, transportation</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <div className="w-4 h-4 bg-green-500 rounded"></div>
                              <span><strong>30% Wants:</strong> Entertainment, dining out, hobbies, shopping</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <div className="w-4 h-4 bg-purple-500 rounded"></div>
                              <span><strong>20% Savings:</strong> Emergency fund, retirement, debt repayment</span>
                            </div>
                          </div>
                        </div>
                      )}
                      {lesson.id === "emergency-fund" && (
                        <div className="space-y-3">
                          <h4 className="font-semibold text-white">Building Emergency Savings</h4>
                          <ul className="space-y-2 text-sm text-dark-900">
                            <li>• <strong>Start Small:</strong> Begin with $500 for minor emergencies</li>
                            <li>• <strong>Build to 3-6 Months:</strong> Save 3-6 months of living expenses</li>
                            <li>• <strong>Keep Accessible:</strong> Use high-yield savings account</li>
                            <li>• <strong>Only for Emergencies:</strong> Job loss, medical bills, major repairs</li>
                            <li>• <strong>Replenish Quickly:</strong> Rebuild immediately after using</li>
                          </ul>
                        </div>
                      )}
                      {lesson.id === "debt-management" && (
                        <div className="space-y-3">
                          <h4 className="font-semibold text-white">Debt Payoff Strategies</h4>
                          <ul className="space-y-2 text-sm text-dark-900">
                            <li>• <strong>List All Debts:</strong> Balance, minimum payment, interest rate</li>
                            <li>• <strong>Choose Strategy:</strong> Debt avalanche (highest interest) or snowball (smallest balance)</li>
                            <li>• <strong>Pay Minimums:</strong> Always pay minimum on all debts</li>
                            <li>• <strong>Extra to Target:</strong> Put any extra money toward target debt</li>
                            <li>• <strong>Avoid New Debt:</strong> Stop using credit cards while paying off</li>
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Budget Calculator */}
          <div className="bg-dark-200 rounded-2xl shadow-xl overflow-hidden border border-dark-400">
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4">
              <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                <Calculator className="h-5 w-5" />
                <span>Budget Calculator</span>
              </h2>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-1">Monthly Income</label>
                  <input
                    type="number"
                    value={budgetData.income}
                    onChange={(e) => setBudgetData({...budgetData, income: Number(e.target.value)})}
                    className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-white mb-1">Housing</label>
                    <input
                      type="number"
                      value={budgetData.housing}
                      onChange={(e) => setBudgetData({...budgetData, housing: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white mb-1">Transportation</label>
                    <input
                      type="number"
                      value={budgetData.transportation}
                      onChange={(e) => setBudgetData({...budgetData, transportation: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white mb-1">Food</label>
                    <input
                      type="number"
                      value={budgetData.food}
                      onChange={(e) => setBudgetData({...budgetData, food: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white mb-1">Utilities</label>
                    <input
                      type="number"
                      value={budgetData.utilities}
                      onChange={(e) => setBudgetData({...budgetData, utilities: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white mb-1">Savings</label>
                    <input
                      type="number"
                      value={budgetData.savings}
                      onChange={(e) => setBudgetData({...budgetData, savings: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white mb-1">Entertainment</label>
                    <input
                      type="number"
                      value={budgetData.entertainment}
                      onChange={(e) => setBudgetData({...budgetData, entertainment: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 bg-dark-300 text-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                </div>
              </div>
              
              {/* Budget Visualization */}
              <div className="space-y-4">
                <h3 className="font-semibold text-white">Budget Breakdown</h3>
                <div className="space-y-2">
                  {budgetBreakdown.categories.map((category, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1">
                        <div className={`w-3 h-3 rounded-full ${category.color}`}></div>
                        <span className="text-sm font-medium text-white">{category.name}</span>
                        <div className="flex-1 bg-dark-400 rounded-full h-2 mx-3">
                          <div 
                            className={`${category.color} h-2 rounded-full transition-all duration-300`}
                            style={{ width: `${Math.min(category.percentage, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-semibold text-white">${category.amount}</span>
                        <span className="text-xs text-dark-900 ml-2">({category.percentage.toFixed(1)}%)</span>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className={`p-3 rounded-lg ${budgetBreakdown.remaining >= 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${budgetBreakdown.remaining >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                      {budgetBreakdown.remaining >= 0 ? 'Remaining' : 'Over Budget'}
                    </span>
                    <span className={`font-bold ${budgetBreakdown.remaining >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                      ${Math.abs(budgetBreakdown.remaining)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}