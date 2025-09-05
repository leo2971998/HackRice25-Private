import { ReactNode } from "react";
import { Bot, User } from "lucide-react";

export default function MessageBubble({ role, children }: { role: "user" | "bot"; children: ReactNode }) {
  const isUser = role === "user";
  return (
    <div className={`flex items-start space-x-3 ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? "bg-blue-600" 
          : "bg-gradient-to-r from-green-500 to-emerald-600"
      }`}>
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Bot className="h-4 w-4 text-white" />
        )}
      </div>
      
      {/* Message */}
      <div className={`max-w-[70%] rounded-2xl px-4 py-3 text-sm shadow-sm whitespace-pre-wrap ${
        isUser 
          ? "bg-blue-600 text-white rounded-tr-md" 
          : "bg-white border border-gray-200 text-gray-900 rounded-tl-md"
      }`}>
        {children}
      </div>
    </div>
  );
}