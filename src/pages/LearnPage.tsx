import { useState } from "react";
import {
  Brain,
  ChartPie,
  Compass,
  Target,
  Zap,
  FileText,
  TrendingUp,
  Award,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";

const MODULES = [
  {
    id: "personal-inflation",
    title: "Personal inflation 101",
    description: "Understand how Inflate-Wise converts your spending into a custom CPI.",
    points: [
      "Every transaction is categorised with Gemini and mapped to official BLS CPI series.",
      "Weights are calculated using your last 30 days of spend per category.",
      "Your personal index is the weighted sum of CPI category changes.",
    ],
  },
  {
    id: "cpi-mapping",
    title: "BLS categories explained",
    description: "See which CPI buckets power the dashboard visuals.",
    points: [
      "Groceries → Food at home (CUSR0000SAF11)",
      "Gasoline → Gasoline (all types) (CUSR0000SETB01)",
      "Travel → Airline fares (CUSR0000SETG01)",
    ],
  },
  {
    id: "action-loops",
    title: "Turning insight into action",
    description: "Use the assistant and automations to fight inflation proactively.",
    points: [
      "Ask for reduction strategies on your most expensive categories.",
      "Upload receipts to enrich the data set with high fidelity itemisation.",
      "Track progress weekly by comparing personal vs national CPI.",
    ],
  },
];

const INSIGHTS = [
  {
    icon: ChartPie,
    title: "Why personal beats national",
    description:
      "Headline CPI measures everyone. Inflate-Wise weights the basket to match your lifestyle so advice is actually relevant.",
  },
  {
    icon: Target,
    title: "Precision targeting",
    description:
      "Gemini categorisation unlocks laser-focused coaching. No more generic budgeting tips—it's calibrated to your data.",
  },
  {
    icon: FileText,
    title: "BLS-aligned storytelling",
    description:
      "Judges and mentors will recognise official CPI labels, demonstrating a credible path to production partnerships.",
  },
];

export default function LearnPage() {
  const [activeModule, setActiveModule] = useState<string | null>(MODULES[0]?.id ?? null);

  return (
    <div className="space-y-10">
      <Card className="bg-dark-200/50 border border-dark-400/60">
        <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-3">
            <Brain className="w-10 h-10 text-primary-300" />
            <div>
              <CardTitle className="text-white text-2xl">Inflation Academy</CardTitle>
              <p className="text-dark-200 text-sm">
                Master the concepts behind Inflate-Wise so you can explain the magic to judges, mentors, and future users.
              </p>
            </div>
          </div>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/20 text-primary-200 text-sm">
            <Award className="w-4 h-4" />
            Hackathon ready
          </div>
        </CardHeader>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        {INSIGHTS.map(insight => (
          <Card key={insight.title} className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader className="flex items-center gap-3">
              <insight.icon className="w-6 h-6 text-primary-300" />
              <CardTitle className="text-white text-lg">{insight.title}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-dark-200">{insight.description}</CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader className="flex items-center gap-3">
          <Compass className="w-6 h-6 text-primary-300" />
          <CardTitle className="text-white text-xl">Deep dive modules</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-[240px,1fr] gap-6">
          <div className="space-y-2">
            {MODULES.map(module => (
              <button
                key={module.id}
                onClick={() => setActiveModule(module.id)}
                className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition ${
                  activeModule === module.id
                    ? "border-primary-500 bg-primary-500/20 text-white"
                    : "border-dark-400 bg-dark-300/40 text-dark-50 hover:border-primary-500"
                }`}
              >
                {module.title}
              </button>
            ))}
          </div>
          <div className="rounded-xl bg-dark-300/40 border border-dark-400 p-6 space-y-4">
            {MODULES.filter(module => module.id === activeModule).map(module => (
              <div key={module.id} className="space-y-3">
                <h3 className="text-white text-lg font-semibold">{module.title}</h3>
                <p className="text-dark-200 text-sm">{module.description}</p>
                <ul className="space-y-2 text-sm text-dark-50">
                  {module.points.map(point => (
                    <li key={point} className="flex items-start gap-2">
                      <Zap className="w-4 h-4 text-primary-400 mt-1" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-primary-300" />
          <CardTitle className="text-white text-xl">Pitch-ready talking points</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-6 text-sm text-dark-200">
          <div className="space-y-3">
            <h4 className="text-white font-semibold">Problem</h4>
            <p>Generic inflation numbers hide the reality of rapid price changes in certain categories.</p>
            <p>People need a co-pilot that factors in their unique spending mix.</p>
          </div>
          <div className="space-y-3">
            <h4 className="text-white font-semibold">Solution</h4>
            <p>Plaid brings in real transactions, Gemini labels them intelligently, and Inflate-Wise calculates a personal CPI in seconds.</p>
            <p>With function-calling, the assistant grounds every recommendation in your live metrics.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
