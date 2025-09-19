export type Source = {
  name: string;
  why?: string;
  url?: string;
  apply_url?: string;
  phone?: string;
  eligibility?: string;
  county?: string;
  last_verified?: string;
};

export type ChatMsg = {
  id?: string;
  role: "user" | "bot";
  content: string;
  sources?: Source[];
  timestamp?: string;
};