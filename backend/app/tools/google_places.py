import googlemaps
from app.config import settings
from app.models.schemas import Resource

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = googlemaps.Client(key=settings.google_maps_api_key)
    return _client


CATEGORY_QUERIES = {
    "food": ["food bank", "community kitchen", "soup kitchen", "free meals"],
    "shelter": ["homeless shelter", "emergency shelter", "temporary housing"],
    "medical": ["hospital", "urgent care", "clinic", "emergency room"],
    "emergency": ["police station", "fire station"],
}


def search_nearby_resources(
    latitude: float,
    longitude: float,
    category: str,
    radius_meters: int = 5000,
) -> list[Resource]:
    """Search for nearby emergency resources using Google Places API."""
    resources = []
    queries = CATEGORY_QUERIES.get(category, [category])

    for query in queries:
        results = _get_client().places_nearby(
            location=(latitude, longitude),
            radius=radius_meters,
            keyword=query,
            open_now=False,
        )

        for place in results.get("results", [])[:3]:
            loc = place["geometry"]["location"]
            resources.append(
                Resource(
                    name=place["name"],
                    address=place.get("vicinity", "Address unavailable"),
                    latitude=loc["lat"],
                    longitude=loc["lng"],
                    is_open=place.get("opening_hours", {}).get("open_now"),
                    rating=place.get("rating"),
                    place_id=place.get("place_id"),
                    category=category,
                )
            )

    seen = set()
    unique = []
    for r in resources:
        if r.place_id not in seen:
            seen.add(r.place_id)
            unique.append(r)

    return unique[:5]
