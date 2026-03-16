import { Component, ReactNode } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
} from "@vis.gl/react-google-maps";
import type { Resource } from "../types";

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

class MapErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-full items-center justify-center bg-gray-100">
          <p className="text-gray-500">Map unavailable — check your Google Maps API key.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

function MapContent({ resources, userLat, userLng }: MapPanelProps) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "";

  if (!apiKey || apiKey === "your_google_maps_api_key_here") {
    return (
      <div className="flex h-full items-center justify-center bg-gray-100">
        <p className="text-gray-500">
          Set VITE_GOOGLE_MAPS_API_KEY in frontend/.env to enable the map.
        </p>
      </div>
    );
  }

  const center =
    userLat && userLng
      ? { lat: userLat, lng: userLng }
      : { lat: 37.3352, lng: -121.8811 };

  return (
    <APIProvider apiKey={apiKey}>
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

export function MapPanel(props: MapPanelProps) {
  return (
    <MapErrorBoundary>
      <MapContent {...props} />
    </MapErrorBoundary>
  );
}
