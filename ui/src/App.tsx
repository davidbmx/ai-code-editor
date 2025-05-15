import React, { useState, useRef, useEffect } from "react";

type MessageRole = "user" | "assistant" | "system";

interface Message {
  role: MessageRole;
  content: string;
  isLoading?: boolean;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = { role: "user", content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Prepare request
      const requestBody = {
        messages: [{ role: "user", content: inputValue }],
        config: { thread_id: "123" },
      };

      // Make API call
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      if (!reader) throw new Error("Response body is null");

      let assistantMessage = "";

      // Process the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Convert the Uint8Array to a string
        const chunk = new TextDecoder().decode(value);

        // Parse the SSE format
        const lines = chunk.split("\n\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.role === "assistant") {
                assistantMessage += data.content;

                // Update the assistant message in real-time
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const existingAssistantIndex = newMessages.findIndex(
                    (msg) => msg.role === "assistant" && msg.isLoading
                  );

                  if (existingAssistantIndex !== -1) {
                    // Update existing message
                    newMessages[existingAssistantIndex] = {
                      role: "assistant",
                      content: assistantMessage,
                      isLoading: true,
                    };
                  } else {
                    // Add new message
                    newMessages.push({
                      role: "assistant",
                      content: assistantMessage,
                      isLoading: true,
                    });
                  }

                  return newMessages;
                });
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }

      // Finalize the assistant message
      setMessages((prev) => {
        const newMessages = [...prev];
        const assistantIndex = newMessages.findIndex(
          (msg) => msg.role === "assistant" && msg.isLoading
        );

        if (assistantIndex !== -1) {
          newMessages[assistantIndex] = {
            role: "assistant",
            content: assistantMessage,
            isLoading: false,
          };
        } else if (assistantMessage) {
          newMessages.push({
            role: "assistant",
            content: assistantMessage,
            isLoading: false,
          });
        }

        return newMessages;
      });
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content:
            "An error occurred while processing your request. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Chat Panel */}
      <div className="w-1/3 flex flex-col border-r border-gray-200 bg-white">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold">Chat</h2>
        </div>

        {/* Messages Container */}
        <div
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto p-4 space-y-4"
        >
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-gray-500">
              <p>Start a conversation by typing a message below.</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : message.role === "assistant"
                      ? "bg-gray-200 text-gray-800"
                      : "bg-yellow-100 text-yellow-800"
                  } ${message.isLoading ? "opacity-70" : ""}`}
                >
                  <p className="whitespace-pre-wrap break-words">
                    {message.content}
                  </p>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg p-3 bg-gray-200 text-gray-800 opacity-70">
                <p>Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form
          onSubmit={handleSendMessage}
          className="border-t border-gray-200 p-4 flex gap-2"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 rounded-md border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-blue-500 text-white rounded-md px-4 py-2 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>

      {/* Preview Panel */}
      <div className="flex-1 flex flex-col bg-white">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold">Preview</h2>
        </div>
        <div className="flex-1 p-4">
          <iframe
            src="http://localhost:3000/"
            className="w-full h-full border-none rounded-lg shadow-lg bg-white"
            title="Code Preview"
          />
        </div>
      </div>
    </div>
  );
}

export default App;
