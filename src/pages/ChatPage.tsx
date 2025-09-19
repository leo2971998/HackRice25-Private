import { FormEvent, useState } from "react";
import { Sparkles, Send, Loader2, MessageCircle } from "lucide-react";
import toast from "react-hot-toast";

import { askAssistant, type AssistantResponse } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";

interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
}

const PROMPTS = [
  "Why is my personal inflation higher than the national average?",
  "Which categories increased my spending the most this month?",
  "How can I reduce my gasoline spending next month?",
];

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState<ConversationTurn[]>([
    {
      role: "assistant",
      content: "Hi, I'm Inflate-Wise. Ask me about your spending, inflation drivers, or ways to lower costs.",
    },
  ]);

  const sendPrompt = async (prompt: string) => {
    if (!prompt.trim()) return;
    setConversation(prev => [...prev, { role: "user", content: prompt }]);
    setInput("");
    setLoading(true);
    try {
      const response: AssistantResponse = await askAssistant(prompt);
      setConversation(prev => [...prev, { role: "assistant", content: response.answer }]);
    } catch (error) {
      toast.error("Something went wrong. Please try again.");
      setConversation(prev => [
        ...prev,
        {
          role: "assistant",
          content: "I couldn't reach the financial engine right now. Try refreshing your dashboard first.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await sendPrompt(input);
  };

  return (
    <div className="grid lg:grid-cols-[1fr,320px] gap-8">
      <Card className="bg-dark-200/50 border border-dark-400/60">
        <CardHeader>
          <CardTitle className="text-white text-xl flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-primary-400" />
            Ask Inflate-Wise
          </CardTitle>
          <p className="text-dark-700 text-sm">
            Gemini analyses your personal inflation data before responding, so answers are grounded in your real numbers.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4 h-[480px] overflow-y-auto pr-2">
            {conversation.map((turn, index) => (
              <div
                key={`${turn.role}-${index}`}
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${turn.role === "user" ? "ml-auto bg-primary-500 text-white" : "bg-dark-300/60 border border-dark-400 text-dark-100"}`}
              >
                {turn.content}
              </div>
            ))}
            {loading && (
              <div className="max-w-[85%] bg-dark-300/60 border border-dark-400 rounded-2xl px-4 py-3 text-sm text-dark-900 flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-primary-300" />
                Analysing your latest transactions...
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex gap-3">
              <input
                value={input}
                onChange={event => setInput(event.target.value)}
                placeholder="Ask how to lower your personal inflation"
                className="flex-1 rounded-xl bg-dark-300/60 border border-dark-400 px-4 py-3 text-sm text-white focus:border-primary-500 focus:outline-none"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-primary-500 hover:bg-primary-600 text-white transition disabled:opacity-60"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <Card className="bg-dark-200/40 border border-dark-400/60">
          <CardHeader>
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-300" />
              Try one of these
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {PROMPTS.map(prompt => (
              <button
                key={prompt}
                onClick={() => sendPrompt(prompt)}
                className="w-full text-left px-4 py-3 rounded-lg bg-dark-300/60 border border-dark-400 text-sm text-dark-50 hover:border-primary-500 transition"
              >
                {prompt}
              </button>
            ))}
          </CardContent>
        </Card>

        <Card className="bg-dark-200/40 border border-dark-400/60">
          <CardHeader>
            <CardTitle className="text-white text-lg">What can I do?</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-dark-900 space-y-3">
            <p>• Ask for a breakdown of what caused last month's personal inflation.</p>
            <p>• Get actionable steps to control a specific category like groceries or travel.</p>
            <p>• Upload a receipt on the dashboard and ask the assistant to interpret it.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
