import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const api = axios.create({
  baseURL,
  withCredentials: true,
  timeout: 20000,
});

export type AssistantResponse = {
  answer: string;
  context: {
    personal_inflation?: PersonalInflationSnapshot;
  };
};

export type PersonalInflationSnapshot = {
  personal_rate: number | null;
  national_rate: number;
  category_totals: Record<string, number>;
  category_weights: Record<string, number>;
  top_drivers: string[];
  total_spend: number;
};

export type TransactionRecord = {
  transaction_id: string;
  name: string;
  merchant_name?: string;
  amount: number;
  date: string;
  category: string;
};

export type TransactionsResponse = {
  transactions: TransactionRecord[];
  category_totals: Record<string, number>;
  personal_inflation: PersonalInflationSnapshot;
  balances?: any;
  overrides: Record<string, string>;
  next_cursor?: string | null;
};

export const askAssistant = async (question: string) => {
  const { data } = await api.post<AssistantResponse>("/assistant/ask", { question });
  return data;
};

export const fetchTransactions = async () => {
  const { data } = await api.get<TransactionsResponse>("/transactions");
  return data;
};

export const overrideTransactionCategory = async (transactionId: string, category: string) => {
  const { data } = await api.post("/transactions/categorize", {
    transaction_id: transactionId,
    category,
  });
  return data as { ok: boolean; transaction_id: string; category: string };
};

export const getPlaidStatus = async () => {
  const { data } = await api.get("/plaid/status");
  return data as { linked: boolean; balances?: any; warning?: string };
};

export const createPlaidLinkToken = async () => {
  const { data } = await api.post("/plaid/link-token");
  return data as { link_token: string; expiration?: string | null; mode?: string };
};

export const exchangePlaidPublicToken = async (payload: { public_token: string; institution?: any }) => {
  const { data } = await api.post("/plaid/exchange", payload);
  return data as { ok: boolean; item_id: string; mode: string; balances?: any };
};

export const unlinkPlaid = async () => {
  const { data } = await api.delete("/plaid/link");
  return data as { ok: boolean };
};

export const fetchPersonalInflation = async (refresh = false) => {
  const { data } = await api.get("/inflation/personal", { params: { refresh: refresh ? "true" : "false" } });
  return data.personal_inflation as PersonalInflationSnapshot;
};

export const submitReceipt = async (items: string[], total: number) => {
  const { data } = await api.post("/uploads/receipt", { items, total });
  return data as { summary: string };
};
