export interface Resource {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  distance_miles: number | null;
  is_open: boolean | null;
  rating: number | null;
  place_id: string | null;
  category: string;
}

export interface ChatResponse {
  reply: string;
  resources: Resource[];
  user_lat: number | null;
  user_lng: number | null;
}

export interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  resources?: Resource[];
}
