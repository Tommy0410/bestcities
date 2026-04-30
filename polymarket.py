import requests
import json

def get_event_details(slug):
    # Usamos el endpoint que encontraste en la documentación
    url = f"https://gamma-api.polymarket.com/events/slug/{slug}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"📊 Analizando: {data.get('title')}")
        
        grados_ordenados = []
        
        # Recorremos los mercados anidados en el evento
        for m in data.get('markets', []):
            label = m.get('groupItemTitle') # Ejemplo: "25°C"
            precios = m.get('outcomePrices') #
            
            if label and precios:
                grados_ordenados.append({
                    "grado": label,
                    "precio_si": float(json.loads(precios)[0]), # Convertimos el string a float
                    "token_id": json.loads(m.get('clobTokenIds'))[0] # Necesario para operar
                })
        
        # Ordenamos por temperatura para ver el sándwich claro
        grados_ordenados.sort(key=lambda x: x['grado'])
        
        for g in grados_ordenados:
            print(f"  🌡️ {g['grado']}: {g['precio_si']*100:.1f}¢ | ID: {g['token_id'][:10]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Ejemplo con el slug de Seúl que pusiste antes
    get_event_details("highest-temperature-in-seoul-on-april-30-2026")