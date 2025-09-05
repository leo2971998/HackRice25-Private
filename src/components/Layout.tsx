import { ReactNode } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface LayoutProps {
  children: ReactNode;
  className?: string;
}

export default function Layout({ children, className }: LayoutProps) {
  return (
    <div className="min-h-dvh flex flex-col bg-gradient-to-br from-dark-300 via-dark-200 to-dark-100">
      <Navbar />
      <main className={`flex-1 mx-auto w-full max-w-4xl px-4 py-6 ${className || ''}`}>{children}</main>
      <Footer />
    </div>
  );
}