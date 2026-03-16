import googlemaps
from app.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = googlemaps.Client(key=settings.google_maps_api_key)
    return _client


def geocode_location(address: str) -> dict | None:
    """Resolve a text address/landmark to lat/lng coordinates."""
    results = _get_client().geocode(address)
    if not results:
        return None
    loc = results[0]["geometry"]["location"]
    return {
        "latitude": loc["lat"],
        "longitude": loc["lng"],
        "formatted_address": results[0]["formatted_address"],
    }
