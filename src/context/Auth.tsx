// src/context/Auth.tsx
import { createContext, useContext, useEffect, useState } from "react";
import { me } from "@/api/auth";

type User = {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  nessie_customer_id?: string;
} | null;

const Ctx = createContext<{
  user: User;
  setUser: (u: User) => void;
  loading: boolean;
}>({ user: null, setUser: () => {}, loading: true });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Ctx.Provider value={{ user, setUser, loading }}>
      {children}
    </Ctx.Provider>
  );
}

export const useAuth = () => useContext(Ctx);