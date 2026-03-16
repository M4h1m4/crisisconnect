import type { Message } from "../types";
import { ResourceCard } from "./ResourceCard";

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        {message.resources && message.resources.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.resources.map((r, i) => (
              <ResourceCard key={i} resource={r} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
