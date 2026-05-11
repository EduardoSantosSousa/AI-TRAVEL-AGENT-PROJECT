from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.schemas import ItineraryRequest, ItineraryResponse, WeatherRegenerationRequest
from backend.services.itinerary_service import create_itinerary, regenerate_itinerary_due_to_weather

load_dotenv()

app = FastAPI(title="AI Travel Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(payload: ItineraryRequest):
    itinerary = await create_itinerary(payload)

    return ItineraryResponse(
        city=payload.city,
        itinerary=itinerary,
    )


@app.post("/api/itinerary/regenerate-for-weather", response_model=ItineraryResponse)
async def regenerate_for_weather(payload: WeatherRegenerationRequest):
    itinerary = await regenerate_itinerary_due_to_weather(payload)

    return ItineraryResponse(
        city=payload.original_request.city,
        itinerary=itinerary,
    )