import { Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import ChatPage from "@/pages/ChatPage";
import LearnPage from "@/pages/LearnPage";
import AdminPortalPage from "@/pages/AdminPortalPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import Onboarding from "@/pages/Onboarding";
import Dashboard from "@/pages/Dashboard";
import DashboardDemo from "@/pages/DashboardDemo";
import LandingPage from "@/pages/LandingPage";

import ProtectedRoute from "@/components/ProtectedRoute";
import { AuthProvider } from "@/context/Auth";
import { Toaster } from "react-hot-toast";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* All routes now use Layout for consistent navbar */}
        <Route path="/" element={
          <Layout>
            <LandingPage />
          </Layout>
        } />
        
        <Route path="/login" element={
          <Layout>
            <LoginPage />
          </Layout>
        } />
        
        <Route path="/register" element={
          <Layout>
            <RegisterPage />
          </Layout>
        } />
        
        {/* Protected routes */}
        <Route path="/onboarding" element={
          <Layout>
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          </Layout>
        } />
        
        <Route path="/dashboard" element={
          <Layout>
            <ProtectedRoute requiresPlaid>
              <Dashboard />
            </ProtectedRoute>
          </Layout>
        } />

        {/* Demo route without protection */}
        <Route path="/demo" element={
          <Layout>
            <DashboardDemo />
          </Layout>
        } />

        
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
            <ProtectedRoute requiresAdmin>
              <AdminPortalPage />
            </ProtectedRoute>
          </Layout>
        } />
      </Routes>
      <Toaster position="top-right" />
    </AuthProvider>
  );
}