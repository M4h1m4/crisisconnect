import { ChatResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "";

export async function sendMessage(
  message: string,
  latitude?: number | null,
  longitude?: number | null
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, latitude, longitude }),
  });
  if (!res.ok) throw new Error("Failed to get response");
  return res.json();
}
