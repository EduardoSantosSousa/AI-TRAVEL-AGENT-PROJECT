import { generateItinerary, regenerateForWeather } from "./api/itineraryApi.js";

let selectedDays = 1;
let selectedInterests = ["Food", "Nature"];
let selectedRestrictions = [];
let lastRequest = null;
let lastItinerary = null;
let selectedDayIndex = 0;

const form = document.querySelector("#planner-form");
const result = document.querySelector("#itinerary-result");

const activeClasses = ["border-transparent", "bg-secondary-container", "text-on-secondary-container", "shadow-sm"];
const inactiveClasses = ["border-outline-variant", "bg-surface-container-lowest", "text-on-surface"];

function setActive(button, isActive) {
  if (isActive) {
    button.classList.add(...activeClasses);
    button.classList.remove(...inactiveClasses);
  } else {
    button.classList.remove(...activeClasses);
    button.classList.add(...inactiveClasses);
  }
}

document.querySelectorAll(".duration-option").forEach((button) => {
  button.addEventListener("click", () => {
    selectedDays = Number(button.dataset.days);

    document.querySelectorAll(".duration-option").forEach((item) => {
      setActive(item, item === button);
    });
  });
});

document.querySelectorAll(".interest-option").forEach((button) => {
  const interest = button.dataset.interest;
  setActive(button, selectedInterests.includes(interest));

  button.addEventListener("click", () => {
    if (selectedInterests.includes(interest)) {
      selectedInterests = selectedInterests.filter((item) => item !== interest);
    } else {
      selectedInterests.push(interest);
    }

    setActive(button, selectedInterests.includes(interest));
  });
});

document.querySelectorAll(".restriction-option").forEach((button) => {
  button.addEventListener("click", () => {
    const restriction = button.dataset.restriction;

    if (selectedRestrictions.includes(restriction)) {
      selectedRestrictions = selectedRestrictions.filter((item) => item !== restriction);
    } else {
      selectedRestrictions.push(restriction);
    }

    setActive(button, selectedRestrictions.includes(restriction));
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    city: document.querySelector("#destination").value,
    interests: selectedInterests,
    days: selectedDays,
    start_date: document.querySelector("#start-date").value,
    budget: document.querySelector("#budget").value,
    pace: document.querySelector("#pace").value,
    trip_type: document.querySelector("#trip-type").value,
    start_time: document.querySelector("#start-time").value,
    end_time: document.querySelector("#end-time").value,
    restrictions: selectedRestrictions,
  };

  lastRequest = payload;
  selectedDayIndex = 0;

  renderLoading();

  try {
    const data = await generateItinerary(payload);
    lastItinerary = data.itinerary;
    renderItinerary(lastItinerary);
  } catch (error) {
    renderError(error);
  }
});

document.addEventListener("click", async (event) => {
  const dayButton = event.target.closest("[data-day-index]");
  if (dayButton && lastItinerary) {
    selectedDayIndex = Number(dayButton.dataset.dayIndex);
    renderItinerary(lastItinerary);
    return;
  }

  const regenerateButton = event.target.closest("#regenerate-weather-btn");
  if (regenerateButton && lastRequest && lastItinerary) {
    renderLoading();

    try {
      const data = await regenerateForWeather(lastRequest, lastItinerary);
      lastItinerary = data.itinerary;
      selectedDayIndex = 0;
      renderItinerary(lastItinerary);
    } catch (error) {
      renderError(error);
    }
  }
});

function renderLoading() {
  result.innerHTML = `
    <div class="p-stack-lg flex flex-col items-center justify-center min-h-[600px] text-center">
      <span class="material-symbols-outlined text-6xl text-secondary animate-pulse">auto_awesome</span>
      <h2 class="font-headline-md text-on-surface mt-4">Generating your itinerary</h2>
      <p class="font-body-md text-on-surface-variant mt-2">
        Building places, routes, weather and local insights.
      </p>
    </div>
  `;
}

function renderError(error) {
  result.innerHTML = `
    <div class="p-stack-lg flex flex-col items-center justify-center min-h-[600px] text-center">
      <span class="material-symbols-outlined text-6xl text-error">error</span>
      <h2 class="font-headline-md text-on-surface mt-4">Could not generate itinerary</h2>
      <p class="font-body-md text-on-surface-variant mt-2">${error.message}</p>
    </div>
  `;
}

function renderItinerary(itinerary) {
  const selectedDay = itinerary.days[selectedDayIndex] || itinerary.days[0];
  const coverImage = itinerary.cover_image?.url || "";

  result.innerHTML = `
    <div class="flex-grow flex flex-col h-full z-10 overflow-y-auto">
      ${renderCover(itinerary, coverImage)}
      ${renderDayTabs(itinerary.days)}
      ${renderDay(selectedDay, itinerary)}
      ${renderActionBar(itinerary)}
    </div>
  `;

  drawRouteMap(selectedDay);
}

function renderCover(itinerary, coverImage) {
  return `
    <div class="relative h-48 w-full shrink-0">
      <div
        class="absolute inset-0 bg-surface-container-high bg-cover bg-center"
        style="background-image: url('${coverImage}')">
      </div>
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
      <div class="absolute bottom-0 left-0 p-stack-lg w-full flex justify-between items-end">
        <div>
          <span class="inline-block px-3 py-1 bg-white/20 backdrop-blur-md rounded-full font-label-sm text-white mb-2 border border-white/30">
            ${itinerary.city} Trip
          </span>
          <h2 class="font-headline-xl text-white drop-shadow-md">${itinerary.title}</h2>
        </div>
      </div>
    </div>
  `;
}

function renderDayTabs(days) {
  return `
    <div class="bg-surface border-b border-outline-variant/30 flex overflow-x-auto hide-scrollbar">
      ${days.map((day, index) => `
        <button
          data-day-index="${index}"
          class="px-6 py-4 font-label-md flex-shrink-0 border-b-2 transition-colors ${
            index === selectedDayIndex
              ? "text-primary border-primary bg-surface-container-lowest"
              : "text-on-surface-variant hover:bg-surface-container border-transparent"
          }">
          ${day.date_label || `Day ${day.day}`}
        </button>
      `).join("")}
    </div>
  `;
}

function renderDay(day, itinerary) {
  return `
    <div class="p-stack-lg flex flex-col gap-stack-lg relative">
      ${renderWeatherCard(day, itinerary)}
      <div class="absolute left-[51px] top-[48px] bottom-[280px] w-0.5 bg-outline-variant/30 border-l border-dashed border-outline-variant/50"></div>
      ${day.items.map((item) => renderTimelineItem(item)).join("")}
      ${renderRouteMap(day)}
    </div>
  `;
}

function renderTimelineItem(item) {
  const photo = item.place?.photo_url;
  const insights = item.insights || [];

  return `
    <div class="flex gap-stack-md relative z-10">
      <div class="w-10 h-10 shrink-0 bg-primary text-on-primary rounded-full flex items-center justify-center shadow-sm z-10 border-4 border-surface-container-lowest">
        <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">
          ${getCategoryIcon(item.category)}
        </span>
      </div>

      <div class="flex-grow bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-stack-md hover:shadow-[0px_4px_20px_rgba(13,77,77,0.08)] transition-shadow">
        ${photo ? `
          <img src="${photo}" alt="${item.title}" class="mb-4 h-44 w-full rounded-lg object-cover">
        ` : ""}

        <div class="flex justify-between items-start mb-1">
          <span class="font-label-md text-secondary">${item.time}</span>
          <span class="px-2 py-0.5 bg-surface-container text-on-surface-variant font-label-sm rounded-full">
            ${item.category}
          </span>
        </div>

        <h3 class="font-headline-md text-on-surface mb-2">${item.title}</h3>
        <p class="font-body-md text-on-surface-variant">${item.description}</p>

        ${renderPlaceMeta(item)}
        ${renderWeatherInline(item.weather)}
        ${renderInsights(insights)}
      </div>
    </div>

    ${item.travel_to_next ? renderTravelLabel(item.travel_to_next) : ""}
  `;
}

function renderTravelLabel(label) {
  return `
    <div class="flex items-center gap-2 ml-[19px] -my-2 relative z-10">
      <div class="bg-surface-container text-on-surface-variant font-label-sm px-3 py-1 rounded-full flex items-center gap-1 border border-outline-variant/30 shadow-sm">
        <span class="material-symbols-outlined text-[14px]">directions_car</span>
        ${label}
      </div>
    </div>
  `;
}

function renderPlaceMeta(item) {
  if (!item.place?.address) return "";

  return `
    <p class="mt-3 text-sm text-on-surface-variant">
      ${item.place.address}
    </p>
  `;
}

function renderInsights(insights) {
  if (!insights.length) return "";

  return insights.map((insight) => `
    <div class="mt-stack-sm bg-secondary-fixed/20 border border-secondary-fixed-dim/40 rounded p-2 flex gap-2 items-start">
      <span class="material-symbols-outlined text-secondary text-sm">info</span>
      <span class="font-body-sm text-on-surface-variant text-sm">${insight.text}</span>
    </div>
  `).join("");
}

function getCategoryIcon(category = "") {
  const value = category.toLowerCase();

  if (value.includes("food")) return "restaurant";
  if (value.includes("museum")) return "museum";
  if (value.includes("nature")) return "park";
  if (value.includes("historical")) return "temple_buddhist";
  if (value.includes("architecture")) return "architecture";

  return "place";
}

function renderWeatherInline(weather) {
  if (!weather || weather.status !== "available") {
    return `
      <div class="mt-3 rounded bg-surface-container p-2 text-sm text-on-surface-variant">
        Weather unavailable for this stop.
      </div>
    `;
  }

  return `
    <div class="mt-3 rounded bg-surface-container p-2 text-sm text-on-surface-variant">
      ${weather.condition || "Weather"} · ${weather.temp_c ?? "-"}°C · Rain ${weather.rain_probability ?? "-"}%
    </div>
  `;
}

function renderWeatherCard(day, itinerary) {
  const weather = day.weather;
  const shouldRegenerate = itinerary.itinerary_weather?.recommend_regeneration;

  if (!weather || weather.status !== "available") {
    return "";
  }

  return `
    <div class="absolute right-stack-lg top-stack-lg -mt-8 z-20">
      <div class="flex flex-col gap-2 bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-3 shadow-[0px_4px_12px_rgba(0,0,0,0.1)] backdrop-blur-sm max-w-[220px]">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-blue-500 text-3xl" style="font-variation-settings: 'FILL' 1;">
            ${getWeatherIcon(weather)}
          </span>
          <div>
            <h4 class="font-headline-md text-on-surface leading-none mb-1">${weather.max_temp_c ?? "-"}°C</h4>
            <p class="font-label-sm text-on-surface-variant">${weather.rain_probability ?? "-"}% Rain</p>
          </div>
        </div>

        ${shouldRegenerate ? `
          <button id="regenerate-weather-btn" class="w-full mt-1 bg-surface-container hover:bg-surface-variant text-on-surface font-label-sm py-1.5 px-2 rounded border border-outline-variant/30 transition-colors flex items-center justify-center gap-1">
            <span class="material-symbols-outlined text-[14px]">refresh</span>
            Regenerate for bad weather
          </button>
        ` : ""}
      </div>
    </div>
  `;
}

function getWeatherIcon(weather) {
  const condition = String(weather.condition || "").toLowerCase();

  if (condition.includes("rain")) return "rainy";
  if (condition.includes("cloud")) return "cloud";
  if (condition.includes("storm")) return "thunderstorm";
  if (condition.includes("snow")) return "weather_snowy";

  return "wb_sunny";
}

function renderRouteMap(day) {
  const distanceKm = day.route?.total_distance_meters
    ? (day.route.total_distance_meters / 1000).toFixed(1)
    : null;

  return `
    <div class="mt-4 w-full h-64 bg-surface-container rounded-xl border border-outline-variant/50 overflow-hidden relative z-10 shadow-sm">
      <div id="route-map-${day.day}" class="h-full w-full"></div>

      <div class="absolute left-4 bottom-4 z-20 bg-surface-container-lowest/95 backdrop-blur px-5 py-2.5 rounded-full shadow-md border border-outline-variant/30 flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary">map</span>
        <span class="font-label-md text-on-surface">
          ${distanceKm ? `${distanceKm} km route` : "Route map"}
        </span>
      </div>
    </div>
  `;
}

function drawRouteMap(day) {
  const mapElement = document.querySelector(`#route-map-${day.day}`);

  if (!mapElement) {
    return;
  }

  if (!window.google || !google.maps) {
    mapElement.innerHTML = `
      <div class="h-full w-full flex items-center justify-center text-on-surface-variant">
        Google Maps is not loaded.
      </div>
    `;
    return;
  }

  const stops = day.items
    .map((item) => item.place)
    .filter((place) => place?.latitude && place?.longitude)
    .map((place) => ({
      lat: place.latitude,
      lng: place.longitude,
      name: place.name,
    }));

  if (!stops.length) {
    mapElement.innerHTML = `
      <div class="h-full w-full flex items-center justify-center text-on-surface-variant">
        Route map unavailable
      </div>
    `;
    return;
  }

  const map = new google.maps.Map(mapElement, {
    center: { lat: stops[0].lat, lng: stops[0].lng },
    zoom: 12,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
  });

  const bounds = new google.maps.LatLngBounds();

  stops.forEach((stop, index) => {
    const position = {
      lat: stop.lat,
      lng: stop.lng,
    };

    bounds.extend(position);

    new google.maps.Marker({
      position,
      map,
      label: String(index + 1),
      title: stop.name || `Stop ${index + 1}`,
    });
  });

  const encodedPolyline = day.route?.polyline;

  if (encodedPolyline && google.maps.geometry?.encoding) {
    const path = google.maps.geometry.encoding.decodePath(encodedPolyline);

    const routeLine = new google.maps.Polyline({
      path,
      geodesic: true,
      strokeColor: "#003535",
      strokeOpacity: 1,
      strokeWeight: 4,
    });

    routeLine.setMap(map);
    path.forEach((point) => bounds.extend(point));
  }

  map.fitBounds(bounds);
}

function renderActionBar(itinerary) {
  return `
    <div class="mt-auto border-t border-outline-variant/30 bg-surface-container-lowest/90 backdrop-blur p-stack-md flex justify-between items-center sticky bottom-0 z-20 flex-wrap gap-4">
      <div class="flex items-center gap-2">
        <button class="font-label-sm text-on-surface-variant bg-surface-container hover:bg-surface-variant px-3 py-1.5 rounded border border-outline-variant/30 transition-colors">
          JSON
        </button>
      </div>
      <div class="flex items-center gap-3 ml-auto">
        <button class="font-label-md bg-secondary text-on-secondary px-6 py-2 rounded-lg shadow-sm hover:bg-secondary/90 transition-colors flex items-center gap-2">
          <span class="material-symbols-outlined">bookmark_add</span>
          Save Trip
        </button>
      </div>
    </div>
  `;
}

