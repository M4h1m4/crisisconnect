from typing import TypedDict


class AgentState(TypedDict):
    user_message: str
    user_lat: float | None
    user_lng: float | None
    category: str
    urgency: str
    search_queries: list[str]
    immediate_advice: str
    location_resolved: bool
    resources: list
    response: str
