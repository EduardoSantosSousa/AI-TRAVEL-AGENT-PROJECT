# AI Travel Agent

AI Travel Agent is an AI-powered travel itinerary planner. The project started as a simple Streamlit prototype and is being migrated into a more professional full-stack architecture with a Python backend and a custom frontend.

The current backend generates structured itineraries, enriches each stop with real place data, adds route information, attempts hourly weather enrichment, and returns a JSON response ready for a modern UI.

## Current Architecture

```text
AI-TRAVEL-AGENT/
├─ backend/
│  ├─ main.py
│  ├─ schemas.py
│  └─ services/
│     ├─ itinerary_service.py
│     ├─ place_service.py
│     ├─ route_service.py
│     └─ weather_service.py
├─ config/
│  └─ config.py
├─ core/
│  └─ planner.py
├─ src/
│  └─ chains/
│     └─ itinerary_chain.py
├─ doc/
│  ├─ code.html
│  └─ DESIGN.md
├─ frontend/
├─ app.py
├─ requirements.txt
└─ setup.py
```

## Main Flow

```text
User request
  ↓
FastAPI endpoint
  ↓
TravelPlanner
  ↓
Groq/LangChain itinerary generation
  ↓
Google Places enrichment
  ↓
Google Routes enrichment
  ↓
Google Weather enrichment
  ↓
JSON response for the frontend
```

## What The Backend Does

The backend currently supports:

- generating a travel itinerary with an LLM;
- returning the itinerary as valid JSON;
- adding a city cover image;
- adding real place data for each itinerary stop;
- adding place photos through Google Places;
- adding route distance, duration, and encoded polyline through Google Routes;
- attempting hourly weather lookup through Google Weather;
- generating practical insights for each stop;
- regenerating an itinerary when weather conditions are unfavorable.

## Key Files

### `backend/main.py`

Defines the FastAPI application and exposes the API endpoints:

```text
POST /api/itinerary
POST /api/itinerary/regenerate-for-weather
```

### `backend/schemas.py`

Defines request and response schemas using Pydantic.

Important schemas:

```text
ItineraryRequest
ItineraryResponse
WeatherRegenerationRequest
```

### `backend/services/itinerary_service.py`

Coordinates the full itinerary pipeline:

```text
LLM itinerary
→ Places enrichment
→ Routes enrichment
→ Weather enrichment
```

### `backend/services/place_service.py`

Uses Google Places API to enrich each itinerary item with:

```text
place_id
name
address
latitude
longitude
photo_url
photo_attribution
```

It also adds the main city cover image.

### `backend/services/route_service.py`

Uses Google Routes API to calculate route data for each day:

```text
total_duration
total_distance_meters
polyline
```

### `backend/services/weather_service.py`

Uses Google Weather API as the main weather provider.

For each itinerary item, it attempts to add:

```text
condition
temperature
rain_probability
precipitation_type
risk_level
recommendation
```

If Google Weather does not support the location or the API is not enabled, the backend does not fail. Instead, it returns:

```json
{
  "status": "unavailable",
  "reason_code": "unsupported_location"
}
```

or:

```json
{
  "status": "unavailable",
  "reason_code": "api_not_enabled_or_not_allowed"
}
```

### `core/planner.py`

Holds the `TravelPlanner` class, which stores trip preferences and calls the itinerary generation chain.

### `src/chains/itinerary_chain.py`

Contains the LangChain/Groq prompts.

The prompt asks the model to return valid JSON with:

```text
city
title
summary
start_date
cover_search_query
days
items
search_query
insights
```

Each itinerary stop includes practical insights such as:

```json
{
  "type": "payment",
  "text": "Bring some cash, as smaller vendors may not accept cards."
}
```

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

The Google key must have access to:

```text
Places API (New)
Routes API
Weather API
```

If you later use Google Maps in the browser, create a separate frontend key restricted by HTTP referrer.

## Installation

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running The Backend

Use `python -m uvicorn` to make sure Uvicorn runs inside the active virtual environment:

```powershell
python -m uvicorn backend.main:app --reload
```

If you are not sure whether the correct environment is active, use:

```powershell
venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Test Request

Use `POST /api/itinerary` with:

```json
{
  "city": "New York",
  "interests": ["Food", "Museums", "Architecture"],
  "days": 2,
  "start_date": "2026-05-06",
  "budget": "medium",
  "pace": "moderate",
  "trip_type": "couple",
  "start_time": "09:00",
  "end_time": "20:00",
  "restrictions": ["Avoid long walks"]
}
```

The response should include:

```text
cover_image
days[].items[].place
days[].items[].weather
days[].items[].insights
days[].route
itinerary_weather
```

## Weather Regeneration Endpoint

The backend also exposes:

```text
POST /api/itinerary/regenerate-for-weather
```

This endpoint receives:

```json
{
  "original_request": {},
  "original_itinerary": {}
}
```

It asks the LLM to regenerate the itinerary while avoiding activities affected by bad weather. The regenerated itinerary is enriched again with Places, Routes, and Weather.

## Frontend Plan

The frontend will be built using regular HTML, CSS, JavaScript, and Tailwind CSS.

The visual reference is:

```text
doc/code.html
```

That file already contains the intended UI structure:

- top navigation;
- left-side planning form;
- itinerary cover image;
- day tabs;
- timeline cards;
- weather card;
- route map area;
- export/action bar.

The frontend should consume the backend JSON and populate:

```text
itinerary.cover_image.url
day.items[].place.photo_url
day.items[].weather
day.items[].insights
day.route.polyline
itinerary.itinerary_weather.recommend_regeneration
```

## Notes And Known Limitations

- Google Weather API may not support every exact coordinate.
- If weather is unavailable, the backend marks the stop with `status = "unavailable"` instead of failing.
- Forecast availability is limited to the range supported by Google Weather.
- The old `app.py` Streamlit file is no longer the intended production entrypoint.
- API keys should never be committed to source control.

## Recommended Next Steps

1. Build the frontend from `doc/code.html`.
2. Connect the planning form to `POST /api/itinerary`.
3. Render the cover image, itinerary cards, place photos, insights, and route summary.
4. Add a weather warning UI when `itinerary_weather.recommend_regeneration` is `true`.
5. Connect the bad-weather button to `POST /api/itinerary/regenerate-for-weather`.
