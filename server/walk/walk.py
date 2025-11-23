import requests
import time
import json
from pathlib import Path
from datetime import datetime

# URL de la API pública de Overpass
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Configuración de coordenadas (igual que en otros módulos)
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude

# "Factor Tyrion": Definimos qué buscamos y cuánto pesa cada cosa
# Formato: 'clave_osm': {'valor_osm': peso}
# Si el valor es '*', aplica a cualquier cosa con esa clave (ej. cualquier escuela)
WEIGHTS = {
    "amenity": {
        "restaurant": 1,      # Ocio básico
        "cafe": 1,            # Ocio básico
        "bar": 1,             # Ocio básico
        "pharmacy": 3,        # Salud esencial
        "clinic": 4,          # Salud crítica
        "school": 3,          # Educación
        "kindergarten": 3,    # Educación
        "library": 2,         # Cultura
        "cinema": 2,          # Cultura
        "place_of_worship": 1 # Comunidad
    },
    "shop": {
        "supermarket": 4,     # Alimentación crítica (Score alto)
        "convenience": 2,     # Alimentación básica
        "bakery": 1,          # Especializado
        "greengrocer": 2      # Saludable
    },
    "leisure": {
        "park": 3,            # Espacio verde (Vital)
        "fitness_centre": 2   # Salud
    }
}

def get_tyrion_score(bbox):
    """
    bbox: Tupla o lista (sur, oeste, norte, este) -> (min_lat, min_lon, max_lat, max_lon)
    Retorna: Un número entero (El Score)
    """
    
    # 1. Construimos la query para buscar TODO lo que nos interesa en una sola llamada
    # [out:json][timeout:25]; define formato y tiempo máximo de espera
    overpass_query = f"""
    [out:json][timeout:25];
    (
      nwr["amenity"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      nwr["shop"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      nwr["leisure"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out tags; 
    """
    
    # 2. Hacemos la llamada a la API
    try:
        response = requests.post(OVERPASS_URL, data=overpass_query)
        response.raise_for_status() # Lanzar error si falla la conexión
        data = response.json()
    except Exception as e:
        print(f"Error en la llamada API: {e}")
        return 0 # O manejar el reintento

    # 3. Calculamos el puntaje procesando los resultados
    score = 0
    elements = data.get('elements', [])
    
    for item in elements:
        tags = item.get('tags', {})
        
        # Revisamos nuestras categorías (amenity, shop, leisure)
        for category, values_dict in WEIGHTS.items():
            if category in tags:
                item_type = tags[category]
                
                # Si el tipo específico está en nuestra lista (ej. "restaurant")
                if item_type in values_dict:
                    score += values_dict[item_type]
                
                # (Opcional) Si quieres dar puntos genéricos a cosas no listadas
                # else:
                #    score += 0.5 
                    
    return score

def create_walkability_matrix_20x20():
    """
    Crea una matriz 20x20 con el walkability score de cada celda.
    Normaliza los valores entre 0 y 1.
    """
    # Calcular pasos
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    horizontal_step = lon_span / 20
    vertical_step = lat_span / 20
    
    # Crear matriz vacía
    matrix = [[0.0 for _ in range(20)] for _ in range(20)]
    
    print("\nProcesando matriz 20x20 de walkability...")
    print(f"Área: N:{BOUND_N}, S:{BOUND_S}, W:{BOUND_W}, E:{BOUND_E}")
    
    total_cells = 400
    processed = 0
    
    # Procesar cada celda de la matriz
    for i in range(20):
        for j in range(20):
            # Calcular bounding box de la celda
            # i = fila (de norte a sur)
            # j = columna (de oeste a este)
            north = BOUND_N - (i * vertical_step)
            south = BOUND_N - ((i + 1) * vertical_step)
            west = BOUND_W + (j * horizontal_step)
            east = BOUND_W + ((j + 1) * horizontal_step)
            
            bbox = (south, west, north, east)
            
            # Obtener score de la celda
            score = get_tyrion_score(bbox)
            matrix[i][j] = score
            
            processed += 1
            print(f"Celda [{i},{j}]: Score {score} | Progreso: {processed}/{total_cells}")
            
            # Pausa de cortesía para no sobrecargar la API
            time.sleep(1.5)
    
    # Encontrar el score máximo para normalizar
    max_score = 0
    for row in matrix:
        for val in row:
            if val > max_score:
                max_score = val
    
    print(f"\nScore máximo encontrado: {max_score}")
    
    # Normalizar entre 0 y 1
    normalized_matrix = []
    for row in matrix:
        normalized_row = [val / max_score if max_score > 0 else 0.0 for val in row]
        normalized_matrix.append(normalized_row)
    
    return normalized_matrix, vertical_step, horizontal_step, max_score

def save_walkability_matrix_json(nx=20, ny=20):
    """
    Genera el JSON de walkability similar al de noise y otros.
    """
    # Crear matriz
    matrix, vertical_step, horizontal_step, max_score = create_walkability_matrix_20x20()
    
    # Crear objeto JSON
    obj = [{
        "Aspect": "Walkability",
        "WalkabilityMatrix": matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": vertical_step,
        "HorizontalStep": horizontal_step,
        "MaxScore": max_score,
        "Unit": "walkability_index (normalized 0-1)"
    }]
    
    # Guardar en jsons/
    json_dir = Path(__file__).parent.parent / 'city_stats' / 'jsons'
    json_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = json_dir / f"walkability_matrix_{nx}x{ny}_{ts}.json"
    
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON guardado en: {out_path}")
    return out_path

if __name__ == "__main__":
    save_walkability_matrix_json()