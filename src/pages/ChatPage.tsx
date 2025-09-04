import { useRef, useState } from "react";
import { ask } from "@/api/client";
import type { ChatMsg, Source } from "@/lib/types";
import MessageBubble from "@/components/MessageBubble";
import QuickChips from "@/components/QuickChips";
import SourceCard from "@/components/SourceCard";
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
      setMessages((m) => [...m, { role: "bot", content: data.answer, sources: data.sources as Source[] }]);
    } catch (e: any) {
      toast.error(e?.message || "Request failed");
      setMessages((m) => [...m, { role: "bot", content: `Sorry, something went wrong: ${e?.message || "error"}` }]);
    } finally {
      setLoading(false);
      setTimeout(() => listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" }), 0);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Houston Financial Navigator</h1>
        <span className="text-xs opacity-70">Info may change — verify on source sites.</span>
      </div>

      <QuickChips onPick={onAsk} />

      <div ref={listRef} className="min-h-[50vh] max-h-[60vh] overflow-auto space-y-3 rounded-xl border border-neutral-200 dark:border-neutral-800 p-4">
        {messages.map((m, i) => (
          <div key={i} className="space-y-2">
            <MessageBubble role={m.role}>{m.content}</MessageBubble>
            {m.sources && m.sources.length > 0 && (
              <div className="grid gap-3 md:grid-cols-2">
                {m.sources.map((s, idx) => (
                  <SourceCard key={idx} s={s} />
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="animate-pulse text-sm opacity-70">Searching local programs…</div>}
      </div>

      <form onSubmit={(e) => { e.preventDefault(); onAsk(input); }} className="flex items-center gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about rent, utilities, SNAP, homebuyer aid…"
          className="flex-1 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-transparent px-4 py-3"
        />
        <button disabled={loading} className="rounded-xl bg-blue-600 px-4 py-3 text-white disabled:opacity-60">
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>
    </div>
  );
}