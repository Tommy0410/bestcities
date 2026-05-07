
import requests
from datetime import datetime

CITIES = {
    "Amsterdam": {"lat": 52.315, "lon": 4.790},
    "Helsinki":  {"lat": 60.327, "lon": 24.957},
    "London":    {"lat": 51.505, "lon": 0.055},
    "Madrid":    {"lat": 40.466, "lon": -3.555},
    "Milan":     {"lat": 45.631, "lon": 8.728},
    "Munich":    {"lat": 48.348, "lon": 11.813},
    "Paris":     {"lat": 48.967, "lon": 2.428},
    "Toronto":   {"lat": 43.679, "lon": -79.629},
    "Warsaw":    {"lat": 52.163, "lon": 20.961}
}


def get_window_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_gusts_10m", "cloud_cover", "precipitation", "precipitation_probability", "relative_humidity_2m"],
        "timezone": "auto",
        "forecast_days": 1,
        "models": "best_match"
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        h = res["hourly"]
        w_temp = h["temperature_2m"][10:21]
        w_wind = h["wind_speed_10m"][10:21]
        w_gusts = h["wind_gusts_10m"][10:21]
        w_clouds = h["cloud_cover"][10:21]
        w_rain = h["precipitation"][10:21]
        w_prob = h["precipitation_probability"][10:21]
        w_hum = h["relative_humidity_2m"][10:21]

        return {
            "max_temp": max(w_temp),
            "max_wind": max(w_wind),
            "max_gusts": max(w_gusts),
            "max_clouds": max(w_clouds),
            "total_rain": sum(w_rain),
            "max_prob": max(w_prob),
            "avg_hum": sum(w_hum) / len(w_hum)
        }
    except:
        return None


def calculate_security_score(data):
    if not data:
        return 0

    # KILL-SWITCHES
    if data["total_rain"] > 0 or data["max_prob"] > 30 or data["max_gusts"] > 35 or data["avg_hum"] > 85:
        return 0

    # PENALIZACIONES PROGRESIVAS
    wind_penalty = max(0, data["max_wind"] - 15) * 4
    cloud_penalty = max(0, data["max_clouds"] - 20) * 2
    hum_penalty = max(0, data["avg_hum"] - 50) * 0.5  # Aire seco = Dinero

    score = max(0, 100 - wind_penalty - cloud_penalty - hum_penalty)
    return round(score, 2)


def main():
    results = []
    # Colores
    G, R, RS = "\033[92m", "\033[91m", "\033[0m"

    print(f"\n--- ESCÁNER DE ALTA RESOLUCIÓN | Ventana: 10:00-20:00 ---")

    for city, info in CITIES.items():
        data = get_window_weather(info["lat"], info["lon"])
        if data:
            score = calculate_security_score(data)
            results.append({
                "city": city, "score": score, "pico": data["max_temp"],
                "gusts": data["max_gusts"], "rain": data["total_rain"],
                "hum": data["avg_hum"], "clouds": data["max_clouds"]
            })
        else:
            # Si falla la API, añadimos un marcador para que no falte en la lista
            results.append({"city": city, "score": "ERROR", "pico": 0,
                           "gusts": 0, "rain": 0, "hum": 0, "clouds": 0})

    # Ordenar (poniendo los errores al final)
    results.sort(key=lambda x: (isinstance(
        x['score'], (int, float)), x['score']), reverse=True)

    # Definimos anchos fijos para las columnas
    w_city, w_score, w_pico, w_gusts, w_rain, w_hum, w_cloud = 12, 7, 10, 12, 9, 6, 6

    header = f"{'CIUDAD':<{w_city}} | {'SCORE':<{w_score}} | {'PICO':<{w_pico}} | {'GUSTS':<{w_gusts}} | {'RAIN':<{w_rain}} | {'HUM':<{w_hum}} | {'CLOUDS':<{w_cloud}}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for r in results:
        # Preparamos los textos con sus unidades para que midan siempre lo mismo
        score_val = str(r['score'])
        pico_val = f"{r['pico']:.1f}°C"
        gusts_val = f"{r['gusts']:.1f}km/h"
        rain_val = f"{r['rain']:.1f}mm"
        hum_val = f"{int(r['hum'])}%"
        cloud_val = f"{int(r['clouds'])}%"

        # Elegimos el color según el score
        color = RS
        if r['score'] == 0 or r['score'] == "ERROR":
            color = R
        elif isinstance(r['score'], (int, float)) and r['score'] > 90:
            color = G

        # IMPRESIÓN: El secreto es que el separador '|' esté fuera de las variables con color
        print(f"{r['city']:<{w_city}} | "
              f"{color}{score_val:<{w_score}}{RS} | "
              f"{pico_val:<{w_pico}} | "
              f"{gusts_val:<{w_gusts}} | "
              f"{rain_val:<{w_rain}} | "
              f"{hum_val:<{w_hum}} | "
              f"{cloud_val:<{w_cloud}}")

    print("-" * len(header))


if __name__ == "__main__":
    main()
