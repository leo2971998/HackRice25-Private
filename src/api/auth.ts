import { api } from "./client";

export const register = (body: {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}) => api.post("/auth/register", body).then(r => r.data);

export const login = (body: { email: string; password: string }) =>
  api.post("/auth/login", body).then(r => r.data);

export const logout = () => api.post("/auth/logout").then(r => r.data);

export const me = () => api.get("/me").then(r => r.data);

export const listUsers = () => api.get("/auth/users").then(r => r.data);

export const updateUserRole = (userId: string, role: "user" | "admin") =>
  api.patch(`/auth/users/${userId}`, { role }).then(r => r.data);

export const deleteUser = (userId: string) => api.delete(`/auth/users/${userId}`).then(r => r.data);
