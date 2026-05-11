from core.planner import TravelPlanner
from backend.schemas import ItineraryRequest, WeatherRegenerationRequest
from backend.services.place_service import enrich_itinerary_places
from backend.services.route_service import enrich_itinerary_routes
from backend.services.weather_service import enrich_itinerary_weather
from src.chains.itinerary_chain import regenerate_itinerary_for_weather


async def  create_itinerary(payload: ItineraryRequest) -> dict:
    planner = TravelPlanner()
    planner.set_city(payload.city)
    planner.set_interests(", ".join(payload.interests))
    planner.set_preferences(
        days=payload.days,
        start_date=payload.start_date,
        budget=payload.budget,
        pace=payload.pace,
        trip_type=payload.trip_type,
        start_time=payload.start_time,
        end_time=payload.end_time,
        restrictions=payload.restrictions,
    )

    itinerary = await planner.create_itinerary()
    itinerary = await enrich_itinerary_places(itinerary)
    itinerary = await enrich_itinerary_routes(itinerary)
    itinerary = await enrich_itinerary_weather(itinerary)

    return itinerary


async def enrich_generated_itinerary(itinerary: dict) -> dict:
    itinerary = await enrich_itinerary_places(itinerary)
    itinerary = await enrich_itinerary_routes(itinerary)
    itinerary = await enrich_itinerary_weather(itinerary)

    return itinerary


async def regenerate_itinerary_due_to_weather(payload: WeatherRegenerationRequest) -> dict:
    original_request = payload.original_request.model_dump()
    original_itinerary = payload.original_itinerary
    weather_context = {
        "itinerary_weather": original_itinerary.get("itinerary_weather"),
        "days": [
            {
                "day": day.get("day"),
                "date": day.get("date"),
                "weather": day.get("weather"),
                "items": [
                    {
                        "time": item.get("time"),
                        "title": item.get("title"),
                        "category": item.get("category"),
                        "weather": item.get("weather"),
                    }
                    for item in day.get("items", [])
                ],
            }
            for day in original_itinerary.get("days", [])
        ],
    }

    regenerated_itinerary = await regenerate_itinerary_for_weather(
        request_context=original_request,
        original_itinerary=original_itinerary,
        weather_context=weather_context,
    )

    return await enrich_generated_itinerary(regenerated_itinerary)
