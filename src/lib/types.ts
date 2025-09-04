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

export type ChatMsg = { role: "user" | "bot"; content: string; sources?: Source[] };