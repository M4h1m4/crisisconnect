from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    latitude: float | None = None
    longitude: float | None = None


class ARCoreLocation(BaseModel):
    latitude: float
    longitude: float
    altitude: float | None = None
    horizontal_accuracy: float | None = None
    vertical_accuracy: float | None = None
    yaw: float | None = None
    pitch: float | None = None
    roll: float | None = None


class ImageCrisisRequest(BaseModel):
    description: Optional[str] = None
    arcore_location: Optional[ARCoreLocation] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None


class AuthorityNotification(BaseModel):
    authorities_notified: bool
    notification_id: str | None = None
    message: str
    location_sent: dict | None = None


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
