import requests
from datetime import datetime

# LISTA BLINDADA: Solo ciudades con modelos < 3 km de resolución
CITIES = {
    "Amsterdam": {"lat": 52.315, "lon": 4.790, "dry_months": [4, 5, 6]},
    "Helsinki":  {"lat": 60.327, "lon": 24.957, "dry_months": [5, 6]},
    "London":    {"lat": 51.505, "lon": 0.055, "dry_months": [4, 5, 6]},
    "Madrid":    {"lat": 40.466, "lon": -3.555, "dry_months": [6, 7, 8, 9]},
    "Milan":     {"lat": 45.631, "lon": 8.728, "dry_months": [7, 12, 1]},
    "Munich":    {"lat": 48.348, "lon": 11.813, "dry_months": [1, 2, 3]},
    "Paris":     {"lat": 48.967, "lon": 2.428, "dry_months": [3, 4, 5, 7, 8]},
    "Toronto":   {"lat": 43.679, "lon": -79.629, "dry_months": [8, 9]},
    "Warsaw":    {"lat": 52.163, "lon": 20.961, "dry_months": [9, 10]}
}


def get_window_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_gusts_10m", "cloud_cover", "precipitation", "precipitation_probability"],
        "timezone": "auto",
        "forecast_days": 1,
        "models": "best_match"
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        h = res["hourly"]
        # Ventana crítica: 10:00 a 20:00
        w_temp = h["temperature_2m"][10:21]
        w_wind = h["wind_speed_10m"][10:21]
        w_gusts = h["wind_gusts_10m"][10:21]
        w_clouds = h["cloud_cover"][10:21]
        w_rain = h["precipitation"][10:21]
        w_prob = h["precipitation_probability"][10:21]

        return {
            "max_temp": max(w_temp),
            "max_wind": max(w_wind),
            "max_gusts": max(w_gusts),
            "max_clouds": max(w_clouds),
            "total_rain": sum(w_rain),
            "max_prob": max(w_prob)
        }
    except:
        return None


def calculate_security_score(data, is_dry_season):
    if not data:
        return 0
    # KILL-SWITCH: Lluvia real, probabilidad > 30% o ráfagas > 35km/h
    if data["total_rain"] > 0 or data["max_prob"] > 30 or data["max_gusts"] > 35:
        return 0

    wind_penalty = max(0, data["max_wind"] - 15) * 4
    cloud_penalty = max(0, data["max_clouds"] - 20) * 2

    score = max(0, 100 - wind_penalty - cloud_penalty)
    if not is_dry_season:
        score *= 0.7
    return round(score, 2)


def main():
    current_month = datetime.now().month
    results = []
    print(f"\n--- ESCÁNER DE ALTA RESOLUCIÓN | Ventana: 10:00-20:00 ---")

    for city, info in CITIES.items():
        is_dry = current_month in info["dry_months"]
        data = get_window_weather(info["lat"], info["lon"])
        if data:
            score = calculate_security_score(data, is_dry)
            results.append({
                "city": city, "score": score, "pico": data["max_temp"],
                "wind": data["max_wind"], "gusts": data["max_gusts"],
                "rain": data["total_rain"], "clouds": data["max_clouds"], "dry": is_dry
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    # Cabecera ultra-alineada
    header = f"{'CIUDAD':<12} | {'SCORE':<7} | {'PICO':<8} | {'WIND':<9} | {'GUSTS':<9} | {'RAIN':<7} | {'CLOUDS':<6} | {'DRY'}"
    print(f"\n{header}\n{'-'*85}")

    for r in results:
        # Colores ANSI para la terminal
        GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"

        s_val = r['score']
        score_str = f"{s_val:<7}"
        if s_val == 0:
            score_str = f"{RED}{score_str}{RESET}"
        elif s_val > 90:
            score_str = f"{GREEN}{score_str}{RESET}"

        # Datos formateados
        pico = f"{r['pico']}°C"
        wind = f"{r['wind']}km/h"
        gusts = f"{r['gusts']}km/h"
        rain = f"{r['rain']:.1f}mm"
        clouds = f"{r['clouds']}%"
        dry = "SÍ" if r['dry'] else "NO"

        # Imprimimos la fila con alineación fija
        print(f"{r['city']:<12} | {score_str} | {pico:<8} | {wind:<9} | {gusts:<9} | {rain:<7} | {clouds:<6} | {dry}")


if __name__ == "__main__":
    main()
