import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000"; // direct backend in dev

export const api = axios.create({ 
  baseURL, 
  withCredentials: true,  // allow cookies for authentication
  timeout: 15000 
});

export async function ask(question: string) {
  const { data } = await api.post("/ask", { question });
  return data as { answer: string; sources: any[] };
}