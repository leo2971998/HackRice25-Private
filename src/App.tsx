import { Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import ChatPage from "@/pages/ChatPage";
import LearnPage from "@/pages/LearnPage";
import { Toaster } from "react-hot-toast";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/learn" element={<LearnPage />} />
      </Routes>
      <Toaster position="top-right" />
    </Layout>
  );
}