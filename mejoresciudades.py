import requests
from datetime import datetime

# LISTA BLINDADA: Solo ciudades con modelos < 3 km de resolución
CITIES = {
    # ALADIN (2.3 km)
    "Amsterdam": {"lat": 52.315, "lon": 4.790, "dry_months": [4, 5, 6]},
    # ALADIN (2.3 km)
    "Helsinki": {"lat": 60.327, "lon": 24.957, "dry_months": [5, 6]},
    # ICON-D2 (2.2 km)
    "London": {"lat": 51.505, "lon": 0.055, "dry_months": [4, 5, 6]},
    # ALADIN (2.3 km)
    "Madrid": {"lat": 40.466, "lon": -3.555, "dry_months": [6, 7, 8, 9]},
    # ALADIN (2.3 km)
    "Milan": {"lat": 45.631, "lon": 8.728, "dry_months": [7, 12, 1]},
    # ICON-D2 (2.2 km)
    "Munich": {"lat": 48.348, "lon": 11.813, "dry_months": [1, 2, 3]},

    # AROME-HD (1.3 km)
    "Paris": {"lat": 48.967, "lon": 2.428, "dry_months": [3, 4, 5, 7, 8]},
    # HRDPS (2.5 km)
    "Toronto": {"lat": 43.679, "lon": -79.629, "dry_months": [8, 9]},
    # ALADIN (2.3 km)
    "Warsaw": {"lat": 52.163, "lon": 20.961, "dry_months": [9, 10]}
}


def get_window_weather(lat, lon):
    """Analiza la ventana de 10:00 a 20:00 para detectar riesgos ocultos."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": ["temperature_2m", "wind_speed_10m", "cloud_cover", "precipitation"],
        "timezone": "auto",
        "forecast_days": 1
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        # Escaneamos el bloque crítico del día
        window_clouds = res["hourly"]["cloud_cover"][10:21]
        window_wind = res["hourly"]["wind_speed_10m"][10:21]
        window_rain = res["hourly"]["precipitation"][10:21]

        return {
            "max_temp": max(res["hourly"]["temperature_2m"][10:21]),
            "max_wind": max(window_wind),
            "max_clouds": max(window_clouds),
            "total_rain": sum(window_rain)
        }
    except:
        return None


def calculate_security_score(data, is_dry_season):
    if not data:
        return 0
    # KILL-SWITCH: Si llueve en la ventana o hay demasiada nube/viento, score 0
    if data["total_rain"] > 0 or data["max_wind"] > 22 or data["max_clouds"] > 25:
        return 0

    # Penalización agresiva para asegurar 'cielo despejado' real
    wind_penalty = max(0, data["max_wind"] - 10) * 5
    cloud_penalty = max(0, data["max_clouds"] - 5) * 4

    score = max(0, 100 - wind_penalty - cloud_penalty)
    if not is_dry_season:
        score *= 0.7

    return round(score, 2)


def main():
    current_month = datetime.now().month
    results = []
    print(f"--- ESCÁNER DE ALTA RESOLUCIÓN (<3KM) | Ventana: 10:00-20:00 ---")

    for city, info in CITIES.items():
        is_dry = current_month in info["dry_months"]
        data = get_window_weather(info["lat"], info["lon"])
        if data:
            score = calculate_security_score(data, is_dry)
            results.append({
                "city": city, "score": score, "pico": data["max_temp"],
                "wind": data["max_wind"], "clouds": data["max_clouds"], "dry": is_dry
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    header = f"{'CIUDAD':<12} | {'SCORE':<7} | {'PICO TEMP':<10} | {'MAX WIND':<9} | {'MAX CLOUDS':<10} | {'DRY'}"
    print(f"\n{header}\n{'-'*75}")
    for r in results:
        print(f"{r['city']:<12} | {r['score']:<7} | {r['pico']:<10} | {r['wind']:<9} | {r['clouds']:<10} | {'SÍ' if r['dry'] else 'NO'}")


if __name__ == "__main__":
    main()
