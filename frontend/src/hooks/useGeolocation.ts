import { useState, useCallback } from "react";

interface GeoState {
  latitude: number | null;
  longitude: number | null;
  loading: boolean;
  error: string | null;
}

export function useGeolocation() {
  const [geo, setGeo] = useState<GeoState>({
    latitude: null,
    longitude: null,
    loading: false,
    error: null,
  });

  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setGeo((prev) => ({ ...prev, error: "Geolocation not supported" }));
      return;
    }
    setGeo((prev) => ({ ...prev, loading: true, error: null }));
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGeo({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          loading: false,
          error: null,
        });
      },
      (err) => {
        setGeo((prev) => ({ ...prev, loading: false, error: err.message }));
      }
    );
  }, []);

  return { ...geo, requestLocation };
}
