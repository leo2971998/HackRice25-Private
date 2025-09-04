import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "/api"; // proxy in dev

export const api = axios.create({ baseURL, timeout: 15000 });

export async function ask(question: string) {
  const { data } = await api.post("/ask", { question });
  return data as { answer: string; sources: any[] };
}