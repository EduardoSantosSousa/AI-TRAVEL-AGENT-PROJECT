from typing import Any
from pydantic import BaseModel, Field

class ItineraryRequest(BaseModel):
    city:str
    interests: list[str]
    days: int = 1
    start_date: str
    budget: str = 'medium'
    pace: str = "moderate"
    trip_type: str = "moderate"
    start_time: str = "09:00"
    end_time: str = "20:00"
    restrictions: list[str] = Field(default_factory=list)


class ItineraryResponse(BaseModel):
    city: str
    itinerary: dict[str, Any]


class WeatherRegenerationRequest(BaseModel):
    original_request: ItineraryRequest
    original_itinerary: dict[str, Any]

