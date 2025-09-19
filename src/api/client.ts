import axios from "axios";
import type { ChatMsg, Source } from "@/lib/types";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000"; // direct backend in dev

export const api = axios.create({
  baseURL,
  withCredentials: true, // allow cookies for authentication
  timeout: 15000,
});

export type AskResponse = {
  title?: string;
  summary: string;
  actionable_steps?: string[];
  sources?: Source[];
  provider?: string;
  agent_used?: boolean;
  priority_level?: string;
  follow_up_questions?: string[];
  intent_classification?: Record<string, unknown>;
  session_id?: string | null;
};

export type ChatSessionSummary = {
  id: string;
  title: string;
  last_message: string;
  message_count: number;
  created_at?: string;
  updated_at?: string;
};

export type ChatSessionDetail = ChatSessionSummary & {
  messages: ChatMsg[];
};

function mapHistory(history: ChatMsg[] = []): Array<{ role: string; content: string }> {
  return history
    .filter((msg) => msg.role && msg.content)
    .map((msg) => ({ role: msg.role, content: msg.content }));
}

export async function ask(
  question: string,
  options: {
    sessionId?: string | null;
    conversationHistory?: ChatMsg[];
    context?: Record<string, unknown>;
    title?: string;
  } = {}
) {
  const payload: Record<string, unknown> = { question };

  if (options.sessionId) {
    payload.session_id = options.sessionId;
  }
  if (options.conversationHistory) {
    payload.conversation_history = mapHistory(options.conversationHistory);
  }
  if (options.context) {
    payload.context = options.context;
  }
  if (options.title) {
    payload.title = options.title;
  }

  const { data } = await api.post("/ask", payload);
  return data as AskResponse;
}

export async function createChatSessionRequest(title?: string) {
  const payload = title ? { title } : {};
  const { data } = await api.post("/chat/sessions", payload);
  return data as { session_id: string; title: string };
}

export async function listChatSessions() {
  const { data } = await api.get("/chat/sessions");
  return data as { sessions: ChatSessionSummary[] };
}

export async function fetchChatSession(sessionId: string) {
  const { data } = await api.get(`/chat/sessions/${sessionId}`);
  const messages: ChatMsg[] = (data.messages || []).map((msg: any, index: number) => ({
    id: `${sessionId}-${index}`,
    role: msg.role === "assistant" ? "bot" : msg.role,
    content: msg.content || "",
    sources: msg.sources || [],
    timestamp: msg.timestamp,
  }));

  return {
    id: data.id as string,
    title: (data.title || "Conversation") as string,
    last_message: (data.last_message || "") as string,
    message_count: (data.message_count || messages.length) as number,
    created_at: data.created_at as string | undefined,
    updated_at: data.updated_at as string | undefined,
    messages,
  } satisfies ChatSessionDetail;
}
