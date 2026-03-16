from typing import TypedDict


class AgentState(TypedDict):
    user_message: str
    user_lat: float | None
    user_lng: float | None
    intent: str
    location_resolved: bool
    resources: list
    response: str
