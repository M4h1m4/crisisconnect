import { useState, useCallback } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { MapPanel } from "./components/MapPanel";
import { useGeolocation } from "./hooks/useGeolocation";
import { sendMessage } from "./services/api";
import { Message, Resource } from "./types";

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [mapCenter, setMapCenter] = useState<{
    lat: number | null;
    lng: number | null;
  }>({ lat: null, lng: null });

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

  const userLat = mapCenter.lat ?? geo.latitude;
  const userLng = mapCenter.lng ?? geo.longitude;

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-[420px] flex-shrink-0 border-r bg-white">
        <ChatPanel
          messages={messages}
          onSend={handleSend}
          loading={loading}
          onLocate={geo.requestLocation}
          locationReady={!!geo.latitude}
        />
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
