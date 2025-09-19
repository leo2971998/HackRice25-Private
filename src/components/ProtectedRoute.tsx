// src/components/ProtectedRoute.tsx
import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/Auth";
import { Skeleton, SkeletonGroup } from "./Skeleton";

interface ProtectedRouteProps {
  children: ReactNode;
  requiresPlaid?: boolean;
  requiresAdmin?: boolean;
}

export default function ProtectedRoute({ children, requiresPlaid = false, requiresAdmin = false }: ProtectedRouteProps) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-100 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-dark-200 border border-dark-400 rounded-2xl shadow-xl p-8 space-y-6">
          <div className="space-y-3">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-48" />
          </div>
          <SkeletonGroup count={3} itemClassName="h-12 w-full bg-dark-300/70" />
          <Skeleton className="h-10 w-full bg-dark-300/70" />
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiresPlaid && !user.plaid_item_id) {
    return <Navigate to="/onboarding" replace />;
  }

  if (requiresAdmin && user.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}