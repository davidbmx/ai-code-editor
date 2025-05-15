import React, { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage, ChatMessageProps } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { Separator } from "@/components/ui/separator";

interface ChatContainerProps {
  messages: ChatMessageProps[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatContainer({
  messages,
  onSendMessage,
  isLoading,
}: ChatContainerProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollArea = scrollAreaRef.current;
      scrollArea.scrollTop = scrollArea.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <h2 className="text-xl font-semibold">Chat</h2>
      </div>

      <div ref={scrollAreaRef} className="flex-1 overflow-y-auto p-4">
        <div className="flex flex-col gap-4">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              <p>Start a conversation by typing a message below.</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={index}
                role={message.role}
                content={message.content}
                isLoading={message.isLoading}
              />
            ))
          )}
          {isLoading && (
            <ChatMessage
              role="assistant"
              content="Thinking..."
              isLoading={true}
            />
          )}
        </div>
      </div>

      <div className="border-t border-border mt-auto">
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
