import h3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Configuración de coordenadas (igual que en crime_stats)
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude

def load_and_process_connectivity_data(csv_path):
    """
    Carga el CSV de conectividad y filtra por condado de LA (FIPS 6037).
    Convierte H3 a coordenadas lat/lon.
    """
    print("Cargando datos de conectividad...")
    df = pd.read_csv(csv_path)
    
    # Filtrar condado de LA (FIPS 06037)
    df = df[df['block_geoid'].astype(str).str.startswith('6037')]
    print(f"Registros en condado LA: {len(df)}")
    
    # Filtrar solo fibra de alta velocidad (>= 100 Mbps)
    df = df[df['max_advertised_download_speed'] >= 100]
    print(f"Registros con velocidad >= 100 Mbps: {len(df)}")
    
    # Convertir H3 a Lat/Lon
    df['lat'] = df['h3_res8_id'].apply(lambda x: h3.cell_to_latlng(x)[0])
    df['lon'] = df['h3_res8_id'].apply(lambda x: h3.cell_to_latlng(x)[1])
    
    # Filtrar por bounding box de LA ciudad
    df = df[
        (df['lat'] >= BOUND_S) & (df['lat'] <= BOUND_N) &
        (df['lon'] >= BOUND_W) & (df['lon'] <= BOUND_E)
    ]
    print(f"Registros dentro del área objetivo: {len(df)}")
    
    return df

def create_connectivity_matrix_20x20(df):
    """
    Crea una matriz 20x20 con la velocidad promedio de internet en cada celda.
    Normaliza los valores entre 0 y 1.
    """
    # Crear matriz vacía
    matrix = [[[] for _ in range(20)] for _ in range(20)]
    
    # Calcular pasos
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    horizontal_step = lon_span / 20
    vertical_step = lat_span / 20
    
    print("\nProcesando matriz 20x20...")
    
    # Asignar cada punto a una celda
    for idx, row in df.iterrows():
        lat, lon, speed = row['lat'], row['lon'], row['max_advertised_download_speed']
        
        # Calcular índices de la celda
        j = int((lon - BOUND_W) / horizontal_step)
        i = int((BOUND_N - lat) / vertical_step)
        
        # Validar índices
        if 0 <= i < 20 and 0 <= j < 20:
            matrix[i][j].append(speed)
    
    # Calcular promedios y encontrar max para normalizar
    speed_matrix = []
    max_speed = 0
    
    for i in range(20):
        row = []
        for j in range(20):
            if len(matrix[i][j]) > 0:
                avg_speed = sum(matrix[i][j]) / len(matrix[i][j])
                row.append(avg_speed)
                max_speed = max(max_speed, avg_speed)
            else:
                row.append(0.0)
        speed_matrix.append(row)
    
    # Normalizar entre 0 y 1
    normalized_matrix = []
    for row in speed_matrix:
        normalized_row = [val / max_speed if max_speed > 0 else 0.0 for val in row]
        normalized_matrix.append(normalized_row)
    
    print(f"Velocidad máxima encontrada: {max_speed} Mbps")
    
    return normalized_matrix, vertical_step, horizontal_step, max_speed

def save_connectivity_matrix_json(nx=20, ny=20):
    """
    Genera el JSON de conectividad similar al de criminalidad.
    """
    csv_path = Path(__file__).parent / 'bdc_06_FibertothePremises_fixed_broadband_D24_11nov2025.csv'
    
    # Cargar y procesar datos
    df = load_and_process_connectivity_data(csv_path)
    
    if len(df) == 0:
        print("Error: No hay datos después del filtrado")
        return None
    
    # Crear matriz
    matrix, vertical_step, horizontal_step, max_speed = create_connectivity_matrix_20x20(df)
    
    # Crear objeto JSON
    obj = [{
        "Aspect": "Connectivity",
        "ConnectivityMatrix": matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": vertical_step,
        "HorizontalStep": horizontal_step,
        "MaxSpeed": max_speed,
        "Unit": "Mbps (normalized 0-1)"
    }]
    
    # Guardar en jsons/
    json_dir = Path(__file__).parent.parent / 'city_stats' / 'jsons'
    json_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = json_dir / f"connectivity_matrix_{nx}x{ny}_{ts}.json"
    
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON guardado en: {out_path}")
    return out_path

if __name__ == "__main__":
    save_connectivity_matrix_json()