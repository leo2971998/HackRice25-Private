import { useEffect, useMemo, useRef, useState } from "react";
import {
  ask,
  createChatSessionRequest,
  fetchChatSession,
  listChatSessions,
  type AskResponse,
  type ChatSessionSummary,
} from "@/api/client";
import type { ChatMsg } from "@/lib/types";
import MessageBubble from "@/components/MessageBubble";
import QuickChips from "@/components/QuickChips";
import SourceCard from "@/components/SourceCard";
import { MessageCircle, Sparkles, Send, Plus, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";
import { useAuth } from "@/context/Auth";

const WELCOME_MESSAGE: ChatMsg = {
  id: "welcome",
  role: "bot",
  content:
    "Hi! I can help you find rent, utility, food, and homebuyer programs in Houston/Harris County. Ask me anything.",
};

function formatTimestamp(timestamp?: string) {
  if (!timestamp) return "";
  try {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat("en", {
      month: "short",
      day: "numeric",
    }).format(date);
  } catch (error) {
    return "";
  }
}

function buildSessionPreview(session: ChatSessionSummary) {
  return session.last_message || `${session.message_count} message${session.message_count === 1 ? "" : "s"}`;
}

export default function ChatPage() {
  const { user } = useAuth();
  const isAuthenticated = Boolean(user);

  const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMsg[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionLoading, setSessionLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const historyForRequest = useMemo(
    () => messages.filter((msg) => msg.id !== WELCOME_MESSAGE.id),
    [messages]
  );

  useEffect(() => {
    if (!isAuthenticated) {
      setSessions([]);
      setActiveSessionId(null);
      setMessages([WELCOME_MESSAGE]);
      return;
    }

    refreshSessions(true).catch(() => {
      toast.error("Unable to load saved conversations");
    });
  }, [isAuthenticated]);

  useEffect(() => {
    const container = listRef.current;
    if (!container) return;
    container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function refreshSessions(autoSelect = false) {
    if (!isAuthenticated) return;
    try {
      const { sessions: fetched } = await listChatSessions();
      setSessions(fetched);

      if (autoSelect) {
        if (fetched.length === 0) {
          setActiveSessionId(null);
          setMessages([WELCOME_MESSAGE]);
          return;
        }
        const mostRecent = fetched[0];
        await loadSession(mostRecent.id);
      } else if (activeSessionId && !fetched.some((session) => session.id === activeSessionId) && fetched.length > 0) {
        await loadSession(fetched[0].id);
      }
    } catch (error: any) {
      throw error;
    }
  }

  async function loadSession(sessionId: string) {
    setSessionLoading(true);
    try {
      const session = await fetchChatSession(sessionId);
      setActiveSessionId(sessionId);
      const history = session.messages.length > 0 ? [WELCOME_MESSAGE, ...session.messages] : [WELCOME_MESSAGE];
      setMessages(history);
    } catch (error: any) {
      console.error(error);
      toast.error("Failed to load conversation");
    } finally {
      setSessionLoading(false);
    }
  }

  async function handleCreateSession() {
    if (!isAuthenticated) {
      toast.error("Sign in to save and organize your chats");
      return;
    }

    try {
      const { session_id, title } = await createChatSessionRequest();
      const now = new Date().toISOString();
      setSessions((prev) => [
        {
          id: session_id,
          title,
          last_message: "",
          message_count: 0,
          created_at: now,
          updated_at: now,
        },
        ...prev.filter((session) => session.id !== session_id),
      ]);
      setActiveSessionId(session_id);
      setMessages([WELCOME_MESSAGE]);
      setInput("");
    } catch (error: any) {
      console.error(error);
      toast.error("Unable to start a new conversation");
    }
  }

  async function onAsk(question: string) {
    const trimmed = question.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    let sessionId = activeSessionId;

    if (isAuthenticated && !sessionId) {
      try {
        const { session_id, title } = await createChatSessionRequest();
        sessionId = session_id;
        setActiveSessionId(sessionId);
        const now = new Date().toISOString();
        setSessions((prev) => [
          {
            id: session_id,
            title,
            last_message: "",
            message_count: 0,
            created_at: now,
            updated_at: now,
          },
          ...prev.filter((session) => session.id !== session_id),
        ]);
      } catch (error: any) {
        setLoading(false);
        toast.error("Unable to start a new conversation");
        return;
      }
    }

    try {
      const response: AskResponse = await ask(trimmed, {
        sessionId,
        conversationHistory: isAuthenticated ? undefined : historyForRequest,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: response.summary,
          sources: response.sources ?? [],
          timestamp: new Date().toISOString(),
        },
      ]);

      if (response.session_id) {
        setActiveSessionId(response.session_id);
      }

      if (isAuthenticated) {
        refreshSessions(false).catch(() => {
          console.warn("Failed to refresh sessions");
        });
      }
    } catch (error: any) {
      console.error(error);
      const message = error?.response?.data?.error || error?.message || "Request failed";
      toast.error(message);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: `Sorry, something went wrong: ${message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
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
              <div className="flex items-center justify-end space-x-2 text-accent-emerald bg-accent-emerald/20 px-3 py-1 rounded-full border border-accent-emerald/30">
                <Sparkles className="h-4 w-4" />
                <span className="text-xs font-medium">AI-Powered</span>
              </div>
              <span className="text-xs text-dark-900 mt-1 block">Info may change — verify on source sites</span>
            </div>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-[280px,1fr]">
          <aside className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Conversations</h3>
              <button
                type="button"
                onClick={handleCreateSession}
                className="inline-flex items-center gap-1 rounded-lg bg-primary-500/80 hover:bg-primary-500 text-white px-3 py-1 text-sm transition"
              >
                <Plus className="h-4 w-4" />
                New
              </button>
            </div>

            {!isAuthenticated && (
              <div className="bg-dark-100/50 border border-dark-400 rounded-lg p-4 text-sm text-dark-900 space-y-2">
                <p className="font-medium text-white">Sign in to save your chats</p>
                <p>
                  Your questions are answered anonymously. Log in to keep a history of conversations and pick up where you
                  left off.
                </p>
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center rounded-lg bg-primary-500/80 hover:bg-primary-500 text-white px-3 py-2 text-sm transition"
                >
                  Go to Login
                </Link>
              </div>
            )}

            {isAuthenticated && sessionLoading && (
              <div className="flex items-center justify-center py-8 text-dark-900">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            )}

            {isAuthenticated && !sessionLoading && sessions.length === 0 && (
              <div className="bg-dark-100/50 border border-dashed border-dark-400 rounded-lg p-4 text-sm text-dark-900">
                <p className="font-medium text-white">No conversations yet</p>
                <p>Start a chat to see it appear here.</p>
              </div>
            )}

            {isAuthenticated && sessions.length > 0 && (
              <div className="space-y-2">
                {sessions.map((session) => (
                  <button
                    key={session.id}
                    type="button"
                    onClick={() => loadSession(session.id)}
                    className={`w-full text-left rounded-lg border px-3 py-2 transition focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-0 ${
                      activeSessionId === session.id
                        ? "bg-primary-500/20 border-primary-500 text-white"
                        : "bg-dark-300/40 border-dark-400 text-dark-50 hover:bg-dark-300/60"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs text-dark-900 mb-1">
                      <span>{formatTimestamp(session.updated_at)}</span>
                      <span>{session.message_count} msgs</span>
                    </div>
                    <div className="text-sm font-semibold text-white truncate">{session.title}</div>
                    <div className="text-xs text-dark-900 overflow-hidden text-ellipsis">
                      {buildSessionPreview(session)}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </aside>

          <div className="space-y-4">
            <div className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Popular Questions</h3>
              <QuickChips onPick={onAsk} />
            </div>

            <div className="bg-dark-200 border border-dark-400 rounded-lg shadow-lg overflow-hidden">
              <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-4">
                <h3 className="text-lg font-semibold text-white">Chat with our AI Assistant</h3>
                <p className="text-primary-100 text-sm">Ask about rent, utilities, SNAP, homebuyer aid, and more</p>
              </div>

              <div ref={listRef} className="h-[60vh] overflow-auto p-6 space-y-4 bg-dark-100/50">
                {messages.map((message, index) => (
                  <div key={`${message.id ?? index}-${index}`} className="space-y-3">
                    <MessageBubble role={message.role}>{message.content}</MessageBubble>
                    {message.sources && message.sources.length > 0 && (
                      <div className="grid gap-3 md:grid-cols-2 ml-12">
                        {message.sources.map((source, idx) => (
                          <SourceCard key={idx} s={source} />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex items-center space-x-3 ml-12 text-dark-900">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span className="text-sm">Searching local programs…</span>
                  </div>
                )}
              </div>

              <div className="border-t bg-white p-6">
                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    onAsk(input);
                  }}
                  className="flex items-center gap-3"
                >
                  <div className="flex-1 relative">
                    <input
                      value={input}
                      onChange={(event) => setInput(event.target.value)}
                      placeholder="Ask about rent, utilities, SNAP, homebuyer aid…"
                      className="w-full rounded-xl border-2 border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:bg-white focus:outline-none transition-all"
                      disabled={loading}
                    />
                  </div>
                  <button
                    type="submit"
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
      </div>
    </div>
  );
}
