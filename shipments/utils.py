import requests
from django.conf import settings

def get_optimized_route(origin: str, destination: str) -> dict:
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
      "origin": origin, "destination": destination,
      "mode": "driving", "optimizeWaypoints": "true",
      "key": settings.GOOGLE_MAPS_API_KEY,
    }
    r = requests.get(url, params=params).json()
    if r.get("status")!="OK" or not r.get("routes"): return {}
    leg = r["routes"][0]["legs"][0]
    return {
      "distance": leg["distance"],
      "duration": leg["duration"],
      "steps": [s["html_instructions"] for s in leg["steps"]],
    }

def get_map_url(lat: float, lon: float, dest: str) -> str:
    return (
      f"https://www.google.com/maps/dir/?api=1"
      f"&origin={lat},{lon}&destination={dest}"
      f"&key={settings.GOOGLE_MAPS_API_KEY}"
    )
