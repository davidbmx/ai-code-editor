import React from "react";
import { cn } from "@/lib/utils";

export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessageProps {
  role: MessageRole;
  content: string;
  isLoading?: boolean;
}

export function ChatMessage({
  role,
  content,
  isLoading = false,
}: ChatMessageProps) {
  return (
    <div
      className={cn(
        "flex w-full",
        role === "user" ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg p-3 shadow-sm",
          role === "user"
            ? "bg-primary text-primary-foreground"
            : role === "assistant"
            ? "bg-muted"
            : "bg-secondary text-secondary-foreground",
          isLoading && "opacity-70"
        )}
      >
        <div className="whitespace-pre-wrap break-words text-sm">{content}</div>
      </div>
    </div>
  );
}
