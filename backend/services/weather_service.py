from datetime import datetime
from typing import Any
import asyncio

import httpx

from config.config import GOOGLE_MAPS_API_KEY


GOOGLE_WEATHER_HOURLY_URL = "https://weather.googleapis.com/v1/forecast/hours:lookup"
RAIN_PROBABILITY_THRESHOLD = 60
OUTDOOR_CATEGORIES = {
    "architecture",
    "historical",
    "historical places",
    "nature",
    "outdoor",
    "park",
    "shrine",
    "temple",
    "walking",
}


async def get_hourly_forecast(client: httpx.AsyncClient, latitude: float, longitude: float, hours: int = 240,) -> list[dict[str, Any]]:

    if not GOOGLE_MAPS_API_KEY:
        return []

    forecast_hours = []
    page_token = None

    while len(forecast_hours) < hours:
        params = {
            "key": GOOGLE_MAPS_API_KEY,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "unitsSystem": "METRIC",
            "hours": hours,
            "pageSize": 24,
            "languageCode": "en",
        }

        if page_token:
            params["pageToken"] = page_token

        response = await client.get(
            GOOGLE_WEATHER_HOURLY_URL,
            params=params,
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()
        forecast_hours.extend(data.get("forecastHours", []))

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return forecast_hours[:hours]


def parse_item_hour(time_value: str) -> int | None:
    if not time_value:
        return None

    normalized = time_value.strip().upper()

    for fmt in ("%H:%M", "%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(normalized, fmt).hour
        except ValueError:
            continue

    return None


def forecast_datetime_key(forecast_hour: dict[str, Any]) -> tuple[str | None, int | None]:
    display_date_time = forecast_hour.get("displayDateTime") or {}
    year = display_date_time.get("year")
    month = display_date_time.get("month")
    day = display_date_time.get("day")
    hour = display_date_time.get("hours")

    if not year or not month or not day or hour is None:
        return None, None

    date_value = f"{year:04d}-{month:02d}-{day:02d}"
    return date_value, hour


def find_hour_weather(
    forecast_hours: list[dict[str, Any]],
    date_value: str,
    time_value: str,
) -> dict[str, Any] | None:
    item_hour = parse_item_hour(time_value)
    if not date_value or item_hour is None:
        return None

    for forecast_hour in forecast_hours:
        forecast_date, forecast_hour_value = forecast_datetime_key(forecast_hour)
        if forecast_date == date_value and forecast_hour_value == item_hour:
            return forecast_hour

    return None


def get_temperature_c(forecast_hour: dict[str, Any]) -> float | int | None:
    temperature = forecast_hour.get("temperature") or {}
    return temperature.get("degrees")


def get_condition(forecast_hour: dict[str, Any]) -> str | None:
    condition = forecast_hour.get("weatherCondition") or {}
    description = condition.get("description") or {}
    return description.get("text")


def get_precipitation_probability(forecast_hour: dict[str, Any]) -> int | None:
    precipitation = forecast_hour.get("precipitation") or {}
    probability = precipitation.get("probability") or {}
    return probability.get("percent")


def get_precipitation_type(forecast_hour: dict[str, Any]) -> str | None:
    precipitation = forecast_hour.get("precipitation") or {}
    probability = precipitation.get("probability") or {}
    return probability.get("type")


def get_risk_level(rain_probability: float | int | None) -> str:
    if rain_probability is None:
        return "unknown"
    if rain_probability >= 70:
        return "high"
    if rain_probability >= 40:
        return "medium"
    return "low"


def is_outdoor_item(item: dict[str, Any]) -> bool:
    category = str(item.get("category", "")).strip().lower()
    title = str(item.get("title", "")).strip().lower()
    description = str(item.get("description", "")).strip().lower()

    text = f"{category} {title} {description}"
    return any(keyword in text for keyword in OUTDOOR_CATEGORIES)


def get_weather_recommendation(risk_level: str) -> str:
    if risk_level == "high":
        return "High rain risk. Consider an indoor or covered alternative."
    if risk_level == "medium":
        return "Moderate rain risk. Keep a flexible backup plan."
    if risk_level == "low":
        return "Weather looks suitable for this stop."
    return "Weather risk could not be evaluated."


def build_item_weather(forecast_hour: dict[str, Any] | None) -> dict[str, Any]:
    if not forecast_hour:
        return build_unavailable_item_weather(
            reason_code="forecast_not_found",
            recommendation="Hourly weather forecast is unavailable for this stop.",
        )

    rain_probability = get_precipitation_probability(forecast_hour)
    risk_level = get_risk_level(rain_probability)

    return {
        "status": "available",
        "condition": get_condition(forecast_hour),
        "temp_c": get_temperature_c(forecast_hour),
        "rain_probability": rain_probability,
        "precipitation_type": get_precipitation_type(forecast_hour),
        "risk_level": risk_level,
        "recommendation": get_weather_recommendation(risk_level),
    }


def build_unavailable_item_weather(reason_code: str, recommendation: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "reason_code": reason_code,
        "condition": None,
        "temp_c": None,
        "rain_probability": None,
        "precipitation_type": None,
        "risk_level": "unknown",
        "recommendation": recommendation,
    }


def build_day_weather(item_weathers: list[dict[str, Any]]) -> dict[str, Any]:
    available_weather = [
        weather for weather in item_weathers
        if weather.get("status") == "available"
    ]

    if not available_weather:
        return {
            "status": "unavailable",
            "reason_code": "no_available_hourly_forecast",
            "condition": None,
            "max_temp_c": None,
            "min_temp_c": None,
            "rain_probability": None,
            "risk_level": "unknown",
            "recommendation": "Daily weather forecast is unavailable.",
        }

    temperatures = [
        weather.get("temp_c") for weather in available_weather
        if weather.get("temp_c") is not None
    ]
    rain_probabilities = [
        weather.get("rain_probability") for weather in available_weather
        if weather.get("rain_probability") is not None
    ]
    max_rain_probability = max(rain_probabilities) if rain_probabilities else None
    risk_level = get_risk_level(max_rain_probability)

    return {
        "status": "available",
        "condition": available_weather[0].get("condition"),
        "max_temp_c": max(temperatures) if temperatures else None,
        "min_temp_c": min(temperatures) if temperatures else None,
        "rain_probability": max_rain_probability,
        "risk_level": risk_level,
        "recommendation": get_weather_recommendation(risk_level),
    }


async def enrich_itinerary_weather(itinerary: dict[str, Any]) -> dict[str, Any]:
    if not GOOGLE_MAPS_API_KEY:
        itinerary["itinerary_weather"] = {
            "status": "unavailable",
            "summary": "Weather enrichment is unavailable because GOOGLE_MAPS_API_KEY is not configured.",
            "max_rain_probability": None,
            "recommend_regeneration": False,
            "reason": None,
        }
        return itinerary

    forecast_cache: dict[tuple[float, float], list[dict[str, Any]]] = {}
    forecast_errors: dict[tuple[float, float], Exception] = {}

    high_risk_items = []
    max_rain_probability = 0
    available_weather_count = 0

    locations: dict[tuple[float, float], tuple[float, float]] = {}

    for day in itinerary.get("days", []):
        for item in day.get("items", []):
            place = item.get("place") or {}
            latitude = place.get("latitude")
            longitude = place.get("longitude")

            if latitude is None or longitude is None:
                continue

            cache_key = (round(latitude, 4), round(longitude, 4))
            locations[cache_key] = (latitude, longitude)

    async with httpx.AsyncClient(timeout=20) as client:
        tasks = [
            get_hourly_forecast(client, latitude, longitude)
            for latitude, longitude in locations.values()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    for cache_key, result in zip(locations.keys(), results):
        if isinstance(result, Exception):
            forecast_cache[cache_key] = []
            forecast_errors[cache_key] = result
        else:
            forecast_cache[cache_key] = result

    for day in itinerary.get("days", []):
        date_value = day.get("date")
        item_weathers = []

        for item in day.get("items", []):
            place = item.get("place") or {}
            latitude = place.get("latitude")
            longitude = place.get("longitude")

            if not date_value or latitude is None or longitude is None:
                item["weather"] = build_item_weather(None)
                item_weathers.append(item["weather"])
                continue

            cache_key = (round(latitude, 4), round(longitude, 4))

            if cache_key in forecast_errors:
                error = forecast_errors[cache_key]

                if isinstance(error, httpx.HTTPStatusError):
                    status_code = error.response.status_code
                    print("Google Weather status:", status_code)
                    print("Google Weather response:", error.response.text)

                    if status_code == 404:
                        item["weather"] = build_unavailable_item_weather(
                            reason_code="unsupported_location",
                            recommendation=(
                                "Google Weather does not support this exact location. "
                                "Show a weather-unavailable state or use a fallback weather provider."
                            ),
                        )
                    elif status_code == 403:
                        item["weather"] = build_unavailable_item_weather(
                            reason_code="api_not_enabled_or_not_allowed",
                            recommendation=(
                                "Google Weather API is not enabled or this API key is not allowed to use it."
                            ),
                        )
                    else:
                        item["weather"] = build_item_weather(None)
                else:
                    print(f"Error enriching weather for item '{item.get('title')}': {error}")
                    item["weather"] = build_unavailable_item_weather(
                        reason_code="weather_lookup_error",
                        recommendation="Weather forecast could not be fetched for this stop.",
                    )

                item_weathers.append(item["weather"])
                continue

            forecast_hour = find_hour_weather(
                forecast_cache.get(cache_key, []),
                date_value,
                item.get("time", ""),
            )

            item["weather"] = build_item_weather(forecast_hour)
            item_weathers.append(item["weather"])

            rain_probability = item.get("weather", {}).get("rain_probability")
            if rain_probability is not None:
                available_weather_count += 1
                max_rain_probability = max(max_rain_probability, rain_probability)

            if (
                is_outdoor_item(item)
                and rain_probability is not None
                and rain_probability >= RAIN_PROBABILITY_THRESHOLD
            ):
                high_risk_items.append({
                    "day": day.get("day"),
                    "date": date_value,
                    "time": item.get("time"),
                    "title": item.get("title"),
                    "rain_probability": rain_probability,
                })

        day["weather"] = build_day_weather(item_weathers)

    if available_weather_count == 0:
        itinerary["itinerary_weather"] = {
            "status": "unavailable",
            "provider": "google_weather",
            "summary": "Google Weather forecast is unavailable for all itinerary stops.",
            "max_rain_probability": None,
            "recommend_regeneration": False,
            "reason": "No hourly weather forecast could be matched or fetched.",
            "high_risk_items": [],
        }
        return itinerary

    recommend_regeneration = len(high_risk_items) > 0
    itinerary["itinerary_weather"] = {
        "status": "available",
        "provider": "google_weather",
        "summary": build_itinerary_weather_summary(high_risk_items, max_rain_probability),
        "max_rain_probability": max_rain_probability,
        "recommend_regeneration": recommend_regeneration,
        "reason": "Outdoor stops overlap with high rain probability." if recommend_regeneration else None,
        "high_risk_items": high_risk_items,
    }

    return itinerary


def build_itinerary_weather_summary(
    high_risk_items: list[dict[str, Any]],
    max_rain_probability: float | int,
) -> str:
    if high_risk_items:
        return (
            f"Weather risk is high for {len(high_risk_items)} outdoor stop(s). "
            f"Maximum rain probability is {max_rain_probability}%."
        )

    return f"Weather looks manageable for the itinerary. Maximum rain probability is {max_rain_probability}%."
