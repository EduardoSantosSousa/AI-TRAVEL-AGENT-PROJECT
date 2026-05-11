import httpx
from config.config import GOOGLE_MAPS_API_KEY
import asyncio

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


def build_waypoint(latitude: float, longitude: float) -> dict:
    return {
        "location": {
            "latLng": {
                "latitude": latitude,
                "longitude": longitude,
            }
        }
    }


async def compute_day_route(
    client: httpx.AsyncClient,
    points: list[dict],
) -> dict | None:
    if len(points) < 2:
        return None

    origin = build_waypoint(points[0]["latitude"], points[0]["longitude"])
    destination = build_waypoint(points[-1]["latitude"], points[-1]["longitude"])

    intermediates = [
        build_waypoint(point["latitude"], point["longitude"])
        for point in points[1:-1]
    ]

    payload = {
        "origin": origin,
        "destination": destination,
        "intermediates": intermediates,
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_UNAWARE",
        "computeAlternativeRoutes": False,
        "languageCode": "en-US",
        "units": "METRIC",
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline",
    }

    response = await client.post(
        ROUTES_URL,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    routes = response.json().get("routes", [])
    if not routes:
        return None

    route = routes[0]

    return {
        "total_duration": route.get("duration"),
        "total_distance_meters": route.get("distanceMeters"),
        "polyline": route.get("polyline", {}).get("encodedPolyline"),
    }

async def enrich_day_route(client: httpx.AsyncClient, day: dict) -> None:
    points = []

    for item in day.get("items", []):
        place = item.get("place") or {}

        if place.get("latitude") and place.get("longitude"):
            points.append({
                "latitude": place["latitude"],
                "longitude": place["longitude"],
            })

    try:
        day["route"] = await compute_day_route(client, points)
    except Exception:
        day["route"] = None

async def enrich_itinerary_routes(itinerary: dict) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        await asyncio.gather(
            *(enrich_day_route(client, day) for day in itinerary.get("days", []))
        )

    return itinerary        
