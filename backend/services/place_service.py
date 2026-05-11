import httpx
from config.config import GOOGLE_MAPS_API_KEY
import asyncio

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"


async def search_place(client: httpx.AsyncClient, query: str) -> dict | None:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.photos"
        ),
    }

    payload = {
        "textQuery": query,
        "maxResultCount": 1,
        "languageCode": "en",
    }

    response = await client.post(
        PLACES_TEXT_SEARCH_URL,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    places = response.json().get("places", [])
    return places[0] if places else None


def is_place_in_destination_city(place: dict, destination_city: str) -> bool:
    if not destination_city:
        return True

    city = destination_city.split(",")[0].strip().lower()
    address = str(place.get("formattedAddress", "")).lower()
    name = str(place.get("displayName", {}).get("text", "")).lower()

    return city in address or city in name


async def get_photo_url(
    client: httpx.AsyncClient,
    photo_name: str,
    max_width: int = 1200,
) -> str | None:
    if not photo_name:
        return None

    url = f"https://places.googleapis.com/v1/{photo_name}/media"

    response = await client.get(
        url,
        params={
            "key": GOOGLE_MAPS_API_KEY,
            "maxWidthPx": max_width,
            "skipHttpRedirect": "true",
        },
    )
    response.raise_for_status()

    return response.json().get("photoUri")


async def normalize_place(
    client: httpx.AsyncClient,
    place: dict,
) -> dict:
    location = place.get("location", {})
    photos = place.get("photos", [])
    first_photo = photos[0] if photos else {}

    photo_url = await get_photo_url(client, first_photo.get("name"))

    return {
        "place_id": place.get("id"),
        "name": place.get("displayName", {}).get("text"),
        "address": place.get("formattedAddress"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "photo_url": photo_url,
        "photo_attribution": first_photo.get("authorAttributions", []),
    }


async def enrich_item_place(
    client: httpx.AsyncClient,
    item: dict,
    destination_city: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    query = item.get("search_query") or item.get("title")

    try:
        async with semaphore:
            place = await search_place(client, query)

            if place and not is_place_in_destination_city(place, destination_city):
                print(
                    f"Skipping place outside destination city '{destination_city}' "
                    f"for query '{query}': {place.get('formattedAddress')}"
                )
                item["place"] = None
                return item

            item["place"] = await normalize_place(client, place) if place else None

    except httpx.HTTPStatusError as e:
        print("Google Places status:", e.response.status_code)
        print("Google Places response:", e.response.text)
        item["place"] = None

    except Exception as e:
        print(f"Error enriching place for query '{query}': {e}")
        item["place"] = None

    return item



async def enrich_city_cover_image(
    client: httpx.AsyncClient,
    itinerary: dict,
    semaphore: asyncio.Semaphore,
) -> dict:
    query = itinerary.get("cover_search_query") or f"{itinerary.get('city')} travel city landscape"

    try:
        async with semaphore:
            place = await search_place(client, query)
            cover = await normalize_place(client, place) if place else None

        itinerary["cover_image"] = {
            "url": cover.get("photo_url") if cover else None,
            "attribution": cover.get("photo_attribution") if cover else [],
        }

    except Exception as e:
        print(f"Error enriching cover image for query '{query}': {e}")
        itinerary["cover_image"] = {
            "url": None,
            "attribution": [],
        }

    return itinerary


async def enrich_itinerary_places(itinerary: dict) -> dict:
    semaphore = asyncio.Semaphore(5)
    destination_city = itinerary.get("city", "")

    async with httpx.AsyncClient(timeout=20) as client:
        await enrich_city_cover_image(client, itinerary, semaphore)

        tasks = [
            enrich_item_place(client, item, destination_city, semaphore)
            for day in itinerary.get("days", [])
            for item in day.get("items", [])
        ]

        await asyncio.gather(*tasks)

    return itinerary
