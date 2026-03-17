import { useState, useCallback } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { MapPanel } from "./components/MapPanel";
import { ImageCrisisAnalyzer } from "./components/ImageCrisisAnalyzer";
import { useGeolocation } from "./hooks/useGeolocation";
import { sendMessage, analyzeImageAndGetGuidance } from "./services/api";
import type { Message, Resource } from "./types";

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [mapCenter, setMapCenter] = useState<{
    lat: number | null;
    lng: number | null;
  }>({ lat: null, lng: null });
  const [activeTab, setActiveTab] = useState<"chat" | "crisis">("chat");

  const geo = useGeolocation();

  const handleSend = useCallback(
    async (text: string) => {
      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content: text,
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const res = await sendMessage(text, geo.latitude, geo.longitude);
        const agentMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "agent",
          content: res.reply,
          resources: res.resources,
        };
        setMessages((prev) => [...prev, agentMsg]);

        if (res.resources.length > 0) {
          setResources(res.resources);
        }
        if (res.user_lat && res.user_lng) {
          setMapCenter({ lat: res.user_lat, lng: res.user_lng });
        }
      } catch {
        const errMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "agent",
          content:
            "I'm having trouble connecting right now. If this is an emergency, please call 911.",
        };
        setMessages((prev) => [...prev, errMsg]);
      } finally {
        setLoading(false);
      }
    },
    [geo.latitude, geo.longitude]
  );

  const handleAnalyzeWithLocation = useCallback(async (imageFile: File) => {
    if (!imageFile) return;
    setLoading(true);

    try {
      const res = await analyzeImageAndGetGuidance(imageFile, geo.latitude, geo.longitude);
      
      const agentMsg: Message = {
        id: Date.now().toString(),
        role: "agent",
        content: res.reply,
        resources: res.resources,
      };
      
      setMessages((prev) => [...prev, agentMsg]);
      if (res.resources.length > 0) {
        setResources(res.resources);
      }
      if (res.user_lat && res.user_lng) {
        setMapCenter({ lat: res.user_lat, lng: res.user_lng });
      }
      setActiveTab("chat");
    } catch (err) {
      const errMsg: Message = {
        id: Date.now().toString(),
        role: "agent",
        content: err instanceof Error ? err.message : "Failed to analyze image",
      };
      setMessages((prev) => [...prev, errMsg]);
      setActiveTab("chat");
    } finally {
      setLoading(false);
    }
  }, [geo.latitude, geo.longitude]);

  const userLat = mapCenter.lat ?? geo.latitude;
  const userLng = mapCenter.lng ?? geo.longitude;

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-[420px] flex-shrink-0 border-r bg-white flex flex-col">
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex-1 py-3 font-medium ${
              activeTab === "chat"
                ? "border-b-2 border-blue-500 text-blue-600"
                : "text-gray-500"
            }`}
          >
            💬 Chat
          </button>
          <button
            onClick={() => setActiveTab("crisis")}
            className={`flex-1 py-3 font-medium ${
              activeTab === "crisis"
                ? "border-b-2 border-red-500 text-red-600"
                : "text-gray-500"
            }`}
          >
            🚨 Crisis Scan
          </button>
        </div>
        {activeTab === "chat" ? (
          <ChatPanel
            messages={messages}
            onSend={handleSend}
            loading={loading}
            onLocate={geo.requestLocation}
            locationReady={!!geo.latitude}
          />
        ) : (
          <div className="flex-1 overflow-y-auto">
            <ImageCrisisAnalyzer 
              onAnalyze={handleAnalyzeWithLocation} 
              loading={loading}
            />
          </div>
        )}
      </div>
      <div className="flex-1">
        <MapPanel
          resources={resources}
          userLat={userLat}
          userLng={userLng}
        />
      </div>
    </div>
  );
}
