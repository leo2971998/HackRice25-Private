import { Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import ChatPage from "@/pages/ChatPage";
import LearnPage from "@/pages/LearnPage";
import AdminSandboxPage from "@/pages/AdminSandboxPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import Onboarding from "@/pages/Onboarding";
import Dashboard from "@/pages/Dashboard";
import ProtectedRoute from "@/components/ProtectedRoute";
import { AuthProvider } from "@/context/Auth";
import { Toaster } from "react-hot-toast";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route path="/onboarding" element={
          <ProtectedRoute>
            <Onboarding />
          </ProtectedRoute>
        } />
        
        <Route path="/dashboard" element={
          <ProtectedRoute requiresNessie>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        {/* Layout-wrapped routes */}
        <Route path="/*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/learn" element={<LearnPage />} />
              <Route path="/admin" element={<AdminSandboxPage />} />
            </Routes>
          </Layout>
        } />
      </Routes>
      <Toaster position="top-right" />
    </AuthProvider>
  );
}