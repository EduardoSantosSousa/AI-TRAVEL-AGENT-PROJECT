const API_BASE_URL = "http://127.0.0.1:8000";

export async function generateItinerary(payload) {
  const response = await fetch(`${API_BASE_URL}/api/itinerary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to generate itinerary");
  }

  return response.json();
}

export async function regenerateForWeather(originalRequest, originalItinerary) {
  const response = await fetch(`${API_BASE_URL}/api/itinerary/regenerate-for-weather`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      original_request: originalRequest,
      original_itinerary: originalItinerary,
    }),
  });

  if (!response.ok) {
  const errorText = await response.text();
  throw new Error(`Failed to generate itinerary: ${errorText}`);
  }

  return response.json();
}
