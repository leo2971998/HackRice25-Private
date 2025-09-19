import { useEffect, useState } from "react";
import {
  Cpu,
  FunctionSquare,
  BarChart3,
  UploadCloud,
  Bot,
  PlayCircle,
  CheckCircle,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";
import { fetchPersonalInflation } from "@/api/client";

interface Insight {
  label: string;
  value: string;
  description: string;
}

export default function TrustAgentPage() {
  const [insights, setInsights] = useState<Insight[]>([]);

  useEffect(() => {
    fetchPersonalInflation()
      .then(snapshot => {
        if (!snapshot) return;
        setInsights([
          {
            label: "Personal CPI",
            value: snapshot.personal_rate !== null ? `${snapshot.personal_rate.toFixed(2)}%` : "Calculating",
            description: "Your weighted inflation rate over the past 30 days.",
          },
          {
            label: "National CPI",
            value: `${snapshot.national_rate.toFixed(2)}%`,
            description: "The latest Bureau of Labor Statistics headline number.",
          },
          {
            label: "Top category",
            value: snapshot.top_drivers?.[0] ?? "Pending",
            description: "Biggest contributor to your recent inflation pressure.",
          },
        ]);
      })
      .catch(() => {
        setInsights([]);
      });
  }, []);

  return (
    <div className="space-y-8">
      <Card className="bg-dark-200/50 border border-dark-400/60">
        <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-3">
            <Cpu className="w-10 h-10 text-primary-300" />
            <div>
              <CardTitle className="text-white text-2xl">Inflate-Wise Lab</CardTitle>
              <p className="text-dark-900 text-sm">
                Peek behind the scenes at how Gemini function calling, Plaid, and CPI data come together.
              </p>
            </div>
          </div>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/20 text-primary-200 text-sm">
            <Bot className="w-4 h-4" />
            Gemini inside
          </div>
        </CardHeader>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        {insights.map(insight => (
          <Card key={insight.label} className="bg-dark-200/40 border border-dark-400/60">
            <CardHeader>
              <CardTitle className="text-white text-lg">{insight.label}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-3xl font-semibold text-primary-200">{insight.value}</div>
              <p className="text-sm text-dark-900">{insight.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader className="flex items-center gap-3">
          <FunctionSquare className="w-6 h-6 text-primary-300" />
          <CardTitle className="text-white text-xl">Function calling blueprint</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-6 text-sm text-dark-900">
          <div className="space-y-3">
            <h3 className="text-white font-semibold">Tools exposed to Gemini</h3>
            <ul className="space-y-2">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-primary-400 mt-1" />
                <span><strong>get_user_inflation_report</strong> → fetches Plaid transactions, applies Gemini categorisation, and returns a CPI-aligned summary.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-primary-400 mt-1" />
                <span><strong>recommend_actions</strong> → proposes savings opportunities based on the largest category weights.</span>
              </li>
            </ul>
          </div>
          <div className="space-y-3">
            <h3 className="text-white font-semibold">Conversation flow</h3>
            <ol className="space-y-2 list-decimal list-inside">
              <li>User asks a question (e.g. "Why is my rate rising?").</li>
              <li>Gemini determines it needs data and triggers <em>get_user_inflation_report</em>.</li>
              <li>The backend calls Plaid, maps categories, and sends the structured report back to Gemini.</li>
              <li>Gemini crafts an answer referencing the precise numbers from your account.</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader className="flex items-center gap-3">
          <UploadCloud className="w-6 h-6 text-primary-300" />
          <CardTitle className="text-white text-xl">Receipt ingestion pipeline</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-6 text-sm text-dark-900">
          <div className="space-y-3">
            <h3 className="text-white font-semibold">Pipeline</h3>
            <p>Receipts are sent to Gemini Vision which extracts merchants, totals, and key line items. The data is categorised and immediately reflected on the dashboard.</p>
            <p>Every ingestion updates the inflation snapshot so your personal CPI is always current.</p>
          </div>
          <div className="space-y-3">
            <h3 className="text-white font-semibold">Demo script</h3>
            <ol className="space-y-2 list-decimal list-inside">
              <li>Upload a grocery receipt in the dashboard.</li>
              <li>Watch the AI describe the purchase and place it in the "Groceries" CPI bucket.</li>
              <li>Ask Inflate-Wise how the receipt impacts your personal inflation this month.</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-dark-200/40 border border-dark-400/60">
        <CardHeader className="flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-primary-300" />
          <CardTitle className="text-white text-xl">Demo choreography</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-3 gap-4 text-sm text-dark-900">
          <div className="space-y-2">
            <h4 className="text-white font-semibold flex items-center gap-2">
              <PlayCircle className="w-4 h-4 text-primary-300" /> Step 1
            </h4>
            <p>Link a Plaid sandbox account and highlight the mock balances returned by the API.</p>
          </div>
          <div className="space-y-2">
            <h4 className="text-white font-semibold flex items-center gap-2">
              <PlayCircle className="w-4 h-4 text-primary-300" /> Step 2
            </h4>
            <p>Show the dashboard calculating personal inflation and call out the categories driving the rate.</p>
          </div>
          <div className="space-y-2">
            <h4 className="text-white font-semibold flex items-center gap-2">
              <PlayCircle className="w-4 h-4 text-primary-300" /> Step 3
            </h4>
            <p>Jump into the chat page and ask for coaching that references the freshly updated numbers.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
