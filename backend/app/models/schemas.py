from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    latitude: float | None = None
    longitude: float | None = None


class Resource(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    distance_miles: float | None = None
    is_open: bool | None = None
    rating: float | None = None
    place_id: str | None = None
    category: str


class ChatResponse(BaseModel):
    reply: str
    resources: list[Resource] = []
    user_lat: float | None = None
    user_lng: float | None = None
