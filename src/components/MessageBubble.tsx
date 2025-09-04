import { ReactNode } from "react";
export default function MessageBubble({ role, children }: { role: "user" | "bot"; children: ReactNode }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm whitespace-pre-wrap ${isUser ? "bg-blue-600 text-white" : "bg-neutral-100 dark:bg-neutral-900"}`}>
        {children}
      </div>
    </div>
  );
}