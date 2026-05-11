import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from config.config import GROQ_API_KEY, MODEL_NAME

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=0,
    max_tokens=8192,
)

json_llm = llm.bind(response_format={"type": "json_object"})


def parse_llm_json(content: str, context: str) -> dict:
    raw_content = (content or "").strip()

    if raw_content.startswith("```"):
        raw_content = raw_content.strip("`").strip()
        if raw_content.lower().startswith("json"):
            raw_content = raw_content[4:].strip()

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        start = raw_content.find("{")
        end = raw_content.rfind("}")

        if start != -1 and end != -1 and start < end:
            try:
                return json.loads(raw_content[start:end + 1])
            except json.JSONDecodeError:
                pass

        preview = raw_content[:500] if raw_content else "<empty response>"
        print(f"Invalid JSON from LLM during {context}: {preview}")
        raise ValueError(f"LLM returned invalid JSON during {context}. Preview: {preview}")


async def invoke_json_with_retries(messages: list, context: str) -> dict:
    attempts = [
        messages,
        messages + [
            HumanMessage(
                content=(
                    "The previous response was invalid JSON. Return one complete JSON "
                    "object only. Use double quotes for all keys and strings. Do not "
                    "include trailing commas, Markdown, comments, or explanations."
                )
            )
        ],
        messages + [
            HumanMessage(
                content=(
                    "Return a shorter but complete itinerary as valid JSON only. "
                    "Limit each day to 4 to 6 items. Keep descriptions and insights "
                    "brief so the JSON is not truncated."
                )
            )
        ],
    ]

    last_error = None

    for index, attempt_messages in enumerate(attempts, start=1):
        try:
            response = await json_llm.ainvoke(attempt_messages)
            return parse_llm_json(response.content, f"{context} attempt {index}")
        except ValueError as error:
            last_error = error

    raise last_error


itinerary_prompt = ChatPromptTemplate([
    ("system", """
You are a professional travel planner.

Create a personalized travel itinerary. 
     
For each itinerary item, include a "search_query" field.
The search_query must combine the place name, city, and country when possible.
Do not invent coordinates, place IDs, ratings, addresses, or image URLs.
External APIs will enrich those fields later.

Trip details:
- Destination city: {city}
- Trip start date: {start_date}     
- Duration: {days} day(s)
- Interests: {interests}
- Budget: {budget}
- Travel pace: {pace}
- Trip type: {trip_type}
- Start time: {start_time}
- End time: {end_time}
- Restrictions: {restrictions}

Return ONLY valid JSON.
Do not include Markdown.
Do not include explanations before or after the JSON.

The JSON must follow exactly this structure:

{{
  "city": "{city}",
  "title": "Trip to {city}",
  "summary": "Short trip summary",
  "start_date": "{start_date}",
  "cover_search_query": "{city} travel city landscape",
  "days": [
    {{
      "day": 1,
      "date": "{start_date}",
      "date_label": "Day 1",
      "weather_note": "Optional practical weather note",
      "items": [
        {{
          "time": "09:00",
          "title": "Place or activity name",
          "category": "Nature",
          "description": "Short description",
          "duration": "1 hour",
          "tip": "Practical tip",
          "insights": [
            {{
              "type": "info",
              "text": "Short practical local advice for this stop"
            }}
          ],
          "travel_to_next": "20 mins by car",
          "search_query": "Place name city country"
        }}
      ]
    }}
  ]
}}
     
At the root JSON level, include:     
- cover_search_query
     
For each itinerary item, include:
- search_query     
          
Rules:
- Create exactly {days} day(s).
- Every itinerary item must be located inside the destination city: {city}.
- Do not include nearby cities, neighboring municipalities, day trips, airports, or long-distance transfers outside {city}.
- If a requested interest is not available inside {city}, choose the closest matching activity that is still inside {city}.
- Day 1 must use the trip start date: {start_date}.
- Each following day must increment the date by one calendar day.
- Every day must include a "date" field in YYYY-MM-DD format.
- Respect start and end time.
- Each day must cover the full schedule window from {start_time} to {end_time}.
- The first item of each day must start at or very close to {start_time}.
- The final item of each day must end at or very close to {end_time}.
- Do not finish a day early unless the user restrictions explicitly require it.
- For multi-day trips, every day must have a complete schedule, not only Day 1.
- Include enough stops, meals, breaks, and travel time to realistically fill the available hours.
- Add lunch and dinner stops when they fit within the {start_time} to {end_time} window.
- Use item times that progress chronologically and leave realistic gaps for travel and breaks.
- Limit each day to 4 to 6 itinerary items.
- Keep descriptions, tips, weather notes, and insights short.
- For each itinerary item, include an "insights" array.
- Each insight must include "type" and "text".
- Allowed insight types: info, reservation, payment, accessibility, crowd, weather, transport, cultural.
- Food places should include payment, reservation, or local etiquette insights when useful.
- Markets and small vendors should mention cash when relevant, using cautious language like "may not accept cards".
- Temples and shrines should include cultural etiquette when relevant.
- Outdoor locations should include weather or crowd timing insights when useful.
- Do not invent specific policies such as exact card acceptance unless it is commonly known or phrased cautiously.
- Keep each insight short and practical.
- cover_search_query must describe the destination city as a travel cover image.
- search_query must combine the place name, destination city, state/region, and country when possible.
- search_query must not name any city other than {city}.
- Do not invent image URLs.
- Do not invent coordinates.
- Do not invent place IDs.
- External APIs will enrich those fields later.
     
"""),
    ("human", "Create my travel itinerary as JSON.")
])


async def generate_itinerary(
    city: str,
    interests: list[str],
    days: int = 1,
    start_date: str = "",
    budget: str = "medium",
    pace: str = "moderate",
    trip_type: str = "solo",
    start_time: str = "09:00",
    end_time: str = "20:00",
    restrictions: list[str] | None = None,
) -> dict:
    restrictions = restrictions or []

    messages = itinerary_prompt.format_messages(
        city=city,
        interests=", ".join(interests),
        days=days,
        start_date=start_date,
        budget=budget,
        pace=pace,
        trip_type=trip_type,
        start_time=start_time,
        end_time=end_time,
        restrictions=", ".join(restrictions) if restrictions else "None",
    )

    return await invoke_json_with_retries(messages, "itinerary generation")


weather_regeneration_prompt = ChatPromptTemplate([
    ("system", """
You are a professional travel planner.

Regenerate the itinerary because the weather forecast may make the original plan uncomfortable or impractical.

Return ONLY valid JSON.
Do not include Markdown.
Do not include explanations before or after the JSON.

Keep the same JSON structure used by the original itinerary.

Original trip request:
{request_context}

Original itinerary:
{original_itinerary}

Weather context:
{weather_context}

Rules:
- Keep the same city, dates, budget, pace, trip type, start time, end time and restrictions.
- Every replacement activity must remain inside the original destination city.
- Do not include nearby cities, neighboring municipalities, day trips, airports, or long-distance transfers outside the original destination city.
- Preserve activities that have low weather risk when possible.
- Replace outdoor activities during high rain probability hours.
- Prefer indoor or covered alternatives when rain risk is high.
- Good rainy-day alternatives include museums, covered markets, tea houses, galleries, indoor dining, shopping arcades, cultural workshops and temples with substantial indoor/covered areas.
- For each itinerary item, include a "search_query" field.
- For each itinerary item, include an "insights" array with short practical advice.
- Allowed insight types: info, reservation, payment, accessibility, crowd, weather, transport, cultural.
- Food places should include payment, reservation, or local etiquette insights when useful.
- Markets and small vendors should mention cash when relevant, using cautious language like "may not accept cards".
- Temples and shrines should include cultural etiquette when relevant.
- Outdoor locations should include weather or crowd timing insights when useful.
- At the root JSON level, include "cover_search_query".
- Do not invent coordinates, place IDs, ratings, addresses or image URLs.
"""),
    ("human", "Regenerate the itinerary as valid JSON.")
])


async def regenerate_itinerary_for_weather(
    request_context: dict,
    original_itinerary: dict,
    weather_context: dict,
) -> dict:
    messages = weather_regeneration_prompt.format_messages(
        request_context=json.dumps(request_context, ensure_ascii=False),
        original_itinerary=json.dumps(original_itinerary, ensure_ascii=False),
        weather_context=json.dumps(weather_context, ensure_ascii=False),
    )

    return await invoke_json_with_retries(messages, "weather regeneration")
