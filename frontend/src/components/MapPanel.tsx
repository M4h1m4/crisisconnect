import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
} from "@vis.gl/react-google-maps";
import { Resource } from "../types";

const CATEGORY_PIN_COLORS: Record<string, string> = {
  food: "#16a34a",
  shelter: "#2563eb",
  medical: "#dc2626",
  emergency: "#ea580c",
};

interface MapPanelProps {
  resources: Resource[];
  userLat: number | null;
  userLng: number | null;
}

export function MapPanel({ resources, userLat, userLng }: MapPanelProps) {
  const center =
    userLat && userLng
      ? { lat: userLat, lng: userLng }
      : { lat: 37.3352, lng: -121.8811 };

  return (
    <APIProvider apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ""}>
      <Map
        defaultCenter={center}
        defaultZoom={14}
        mapId="crisisconnect-map"
        className="h-full w-full"
      >
        {userLat && userLng && (
          <AdvancedMarker position={{ lat: userLat, lng: userLng }}>
            <Pin background="#3b82f6" borderColor="#1d4ed8" glyphColor="#fff" />
          </AdvancedMarker>
        )}
        {resources.map((r, i) => (
          <AdvancedMarker
            key={i}
            position={{ lat: r.latitude, lng: r.longitude }}
            title={r.name}
          >
            <Pin
              background={CATEGORY_PIN_COLORS[r.category] || "#6b7280"}
              borderColor="#fff"
              glyphColor="#fff"
            />
          </AdvancedMarker>
        ))}
      </Map>
    </APIProvider>
  );
}
