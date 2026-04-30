import requests
from datetime import datetime

# Diccionario de ciudades (29)
CITIES = {
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "dry_months": [4, 5, 6]},
    "Ankara": {"lat": 39.9334, "lon": 32.8597, "dry_months": [7, 8, 9]},
    "Beijing": {"lat": 39.9042, "lon": 116.4074, "dry_months": [10, 11, 12, 1, 2, 3]},
    "Buenos Aires": {"lat": -34.6037, "lon": -58.3816, "dry_months": [6, 7, 8]},
    "Busan": {"lat": 35.1796, "lon": 129.0756, "dry_months": [10, 11, 12, 1]},
    "Chengdu": {"lat": 30.5728, "lon": 104.0668, "dry_months": [12, 1, 2]},
    "Chongqing": {"lat": 29.5630, "lon": 106.5516, "dry_months": [12, 1]},
    "Guangzhou": {"lat": 23.1291, "lon": 113.2644, "dry_months": [10, 11, 12]},
    "Helsinki": {"lat": 60.1695, "lon": 24.9354, "dry_months": [5, 6]},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "dry_months": [10, 11, 12]},
    "Istanbul": {"lat": 41.0082, "lon": 28.9784, "dry_months": [7, 8]},
    "London": {"lat": 51.5074, "lon": -0.1278, "dry_months": [4, 5, 6]},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462, "dry_months": [10, 11, 2, 3]},
    "Madrid": {"lat": 40.4168, "lon": -3.7038, "dry_months": [6, 7, 8, 9]},
    "Milan": {"lat": 45.4642, "lon": 9.1900, "dry_months": [7, 12, 1]},
    "Moscow": {"lat": 55.7558, "lon": 37.6173, "dry_months": [5, 8]},
    "Munich": {"lat": 48.1351, "lon": 11.5820, "dry_months": [1, 2, 3]},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "dry_months": [3, 4, 5, 7, 8]},
    "Qingdao": {"lat": 36.0671, "lon": 120.3826, "dry_months": [11, 12, 1]},
    "Seoul": {"lat": 37.5665, "lon": 126.9780, "dry_months": [10, 11, 1, 2]},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737, "dry_months": [10, 11, 12]},
    "Shenzhen": {"lat": 22.5431, "lon": 114.0579, "dry_months": [10, 11, 12]},
    "Taipei": {"lat": 25.0330, "lon": 121.5654, "dry_months": [11, 12]},
    "Tel Aviv": {"lat": 32.0853, "lon": 34.7818, "dry_months": [5, 6, 7, 8, 9, 10]},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917, "dry_months": [12, 1, 2]},
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "dry_months": [8, 9]},
    "Warsaw": {"lat": 52.2297, "lon": 21.0122, "dry_months": [9, 10]},
    "Wellington": {"lat": -41.2865, "lon": 174.7762, "dry_months": [12, 1, 2]},
    "Wuhan": {"lat": 30.5928, "lon": 114.3055, "dry_months": [10, 11, 12]}
}

def get_full_weather(lat, lon):
    """Obtiene datos actuales y el resumen diario para mayor seguridad."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": ["wind_speed_10m", "cloud_cover", "temperature_2m"],
        "daily": ["precipitation_sum"],
        "timezone": "auto",
        "forecast_days": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10).json()
        return {
            "temp": response["current"]["temperature_2m"],
            "wind": response["current"]["wind_speed_10m"],
            "clouds": response["current"]["cloud_cover"],
            "daily_rain": response["daily"]["precipitation_sum"][0]
        }
    except:
        return None

def calculate_security_score(data, is_dry_season):
    if not data: return 0
    
    # CRÍTICO: Si va a llover hoy (aunque no esté lloviendo ahora), score 0
    if data["daily_rain"] > 0: return 0
    
    # Límites operativos
    if data["wind"] > 25 or data["clouds"] > 20: return 0
    
    # Algoritmo de precisión
    wind_penalty = max(0, data["wind"] - 15) * 5
    cloud_penalty = max(0, data["clouds"] - 10) * 5
    
    score = max(0, 100 - wind_penalty - cloud_penalty)
    if not is_dry_season: score *= 0.8 # Penalizar si no es su temporada ideal
    
    return round(score, 2)

def main():
    current_month = datetime.now().month
    final_list = []

    print(f"--- Escáner Atmosférico Avanzado | Mes: {current_month} ---")

    for city, info in CITIES.items():
        is_dry = current_month in info["dry_months"]
        weather = get_full_weather(info["lat"], info["lon"])
        
        if weather:
            score = calculate_security_score(weather, is_dry)
            final_list.append({
                "city": city, "score": score, "temp": weather["temp"],
                "wind": weather["wind"], "clouds": weather["clouds"],
                "rain_today": weather["daily_rain"], "season": "SÍ" if is_dry else "NO"
            })

    # ORDENAR TODAS LAS CIUDADES
    final_list.sort(key=lambda x: x["score"], reverse=True)

    header = f"{'CIUDAD':<15} | {'SCORE':<7} | {'TEMP':<7} | {'VIENTO':<10} | {'NUBES':<7} | {'LLUVIA/DÍA':<10} | {'EST. SECA'}"
    print(f"\n{header}")
    print("-" * len(header))
    
    for r in final_list:
        print(f"{r['city']:<15} | {r['score']:<7} | {r['temp']:<7} | {r['wind']:<10} | {r['clouds']:<7} | {r['rain_today']:<10} | {r['season']}")

if __name__ == "__main__":
    main()