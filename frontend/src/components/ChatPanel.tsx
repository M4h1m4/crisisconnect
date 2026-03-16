import { useState, useRef, useEffect } from "react";
import { Send, MapPin, Loader2 } from "lucide-react";
import { Message } from "../types";
import { MessageBubble } from "./MessageBubble";

interface ChatPanelProps {
  messages: Message[];
  onSend: (message: string) => void;
  loading: boolean;
  onLocate: () => void;
  locationReady: boolean;
}

export function ChatPanel({
  messages,
  onSend,
  loading,
  onLocate,
  locationReady,
}: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="border-b bg-white px-4 py-3">
        <h1 className="text-lg font-bold text-gray-900">CrisisConnect</h1>
        <p className="text-xs text-gray-500">Emergency Resource Agent</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-700">
                How can I help you?
              </h2>
              <p className="mt-2 text-sm text-gray-500">
                Tell me what you need — food, shelter, medical help, or
                emergency services.
              </p>
              {!locationReady && (
                <button
                  onClick={onLocate}
                  className="mt-4 inline-flex items-center gap-2 rounded-full bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
                >
                  <MapPin size={16} />
                  Share my location
                </button>
              )}
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-gray-100 px-4 py-3">
              <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t bg-white p-4">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onLocate}
            className={`flex-shrink-0 rounded-full p-2 ${
              locationReady
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-500 hover:bg-gray-200"
            }`}
            title={locationReady ? "Location shared" : "Share location"}
          >
            <MapPin size={20} />
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe what you need..."
            className="flex-1 rounded-full border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex-shrink-0 rounded-full bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
}
