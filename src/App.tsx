import { Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import ChatPage from "@/pages/ChatPage";
import LearnPage from "@/pages/LearnPage";
import AdminSandboxPage from "@/pages/AdminSandboxPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import Onboarding from "@/pages/Onboarding";
import Dashboard from "@/pages/Dashboard";
import LandingPage from "@/pages/LandingPage";
import DemoDashboard from "@/pages/DemoDashboard";
import ProtectedRoute from "@/components/ProtectedRoute";
import { AuthProvider } from "@/context/Auth";
import { Toaster } from "react-hot-toast";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Landing page as root */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Demo dashboard (public for demo purposes) */}
        <Route path="/dashboard-demo" element={<DemoDashboard />} />
        
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
        <Route path="/chat" element={
          <Layout>
            <ChatPage />
          </Layout>
        } />
        
        <Route path="/learn" element={
          <Layout>
            <LearnPage />
          </Layout>
        } />
        
        <Route path="/admin" element={
          <Layout>
            <AdminSandboxPage />
          </Layout>
        } />
      </Routes>
      <Toaster position="top-right" />
    </AuthProvider>
  );
}