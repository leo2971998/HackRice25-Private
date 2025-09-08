import { useRef, useState } from "react";
import { ask } from "@/api/client";
import type { ChatMsg, Source } from "@/lib/types";
import MessageBubble from "@/components/MessageBubble";
import QuickChips from "@/components/QuickChips";
import SourceCard from "@/components/SourceCard";
import { MessageCircle, Sparkles, Send } from "lucide-react";
import toast from "react-hot-toast";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    { role: "bot", content: "Hi! I can help you find rent, utility, food, and homebuyer programs in Houston/Harris County. Ask me anything." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  async function onAsk(q: string) {
    if (!q.trim()) return;
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");
    setLoading(true);
    try {
      const data = await ask(q);
      setMessages((m) => [...m, { role: "bot", content: data.summary, sources: data.sources as Source[] }]);
    } catch (e: any) {
      toast.error(e?.message || "Request failed");
      setMessages((m) => [...m, { role: "bot", content: `Sorry, something went wrong: ${e?.message || "error"}` }]);
    } finally {
      setLoading(false);
      setTimeout(() => listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" }), 0);
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-full p-3">
                <MessageCircle className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Financial Assistant</h1>
                <p className="text-dark-900">Get personalized help finding local aid programs</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2 text-accent-emerald bg-accent-emerald/20 px-3 py-1 rounded-full border border-accent-emerald/30">
                <Sparkles className="h-4 w-4" />
                <span className="text-xs font-medium">AI-Powered</span>
              </div>
              <span className="text-xs text-dark-900 mt-1 block">Info may change — verify on source sites</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Popular Questions</h3>
          <QuickChips onPick={onAsk} />
        </div>

        {/* Chat Container */}
        <div className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-4">
            <h3 className="text-lg font-semibold text-white">Chat with our AI Assistant</h3>
            <p className="text-primary-100 text-sm">Ask about rent, utilities, SNAP, homebuyer aid, and more</p>
          </div>
          
          <div ref={listRef} className="h-[60vh] overflow-auto p-6 space-y-4 bg-dark-100/50">
            {messages.map((m, i) => (
              <div key={i} className="space-y-3">
                <MessageBubble role={m.role}>{m.content}</MessageBubble>
                {m.sources && m.sources.length > 0 && (
                  <div className="grid gap-3 md:grid-cols-2 ml-12">
                    {m.sources.map((s, idx) => (
                      <SourceCard key={idx} s={s} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-center space-x-3 ml-12">
                <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm text-gray-600">Searching local programs…</span>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t bg-white p-6">
            <form onSubmit={(e) => { e.preventDefault(); onAsk(input); }} className="flex items-center gap-3">
              <div className="flex-1 relative">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about rent, utilities, SNAP, homebuyer aid…"
                  className="w-full rounded-xl border-2 border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:bg-white focus:outline-none transition-all"
                  disabled={loading}
                />
              </div>
              <button 
                disabled={loading || !input.trim()} 
                className="rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 flex items-center space-x-2 shadow-lg"
              >
                <Send className="h-4 w-4" />
                <span>{loading ? "Thinking…" : "Ask"}</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
