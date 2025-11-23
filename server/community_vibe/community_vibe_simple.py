"""
Script simplificado: Community Vibe usando SOLO datos de LADBS
No requiere API keys - Datos públicos de la ciudad de LA

Detecta zonas de inversión/gentrificación basándose únicamente en
permisos de construcción recientes (últimos 2 años).
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

# Configuración de coordenadas
BOUND_W = -118.6057
BOUND_E = -118.1236
BOUND_N = 34.3344
BOUND_S = 33.8624

LADBS_PERMITS_URL = 'https://data.lacity.org/resource/yv23-pmwf.json'

def assign_to_cell(lat: float, lon: float):
    """Asigna coordenada a celda 20x20"""
    if not (BOUND_S <= lat <= BOUND_N and BOUND_W <= lon <= BOUND_E):
        return None, None
    
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    
    j = int((lon - BOUND_W) / (lon_span / 20))
    i = int((BOUND_N - lat) / (lat_span / 20))
    
    if 0 <= i < 20 and 0 <= j < 20:
        return i, j
    return None, None

def download_and_process_permits():
    """Descarga permisos y calcula inversión por celda"""
    print("Descargando permisos de LADBS (esto puede tardar 1-2 minutos)...")
    
    two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT%H:%M:%S')
    
    all_permits = []
    offset = 0
    limit = 50000
    
    while True:
        params = {
            '$limit': limit,
            '$offset': offset,
            '$where': f"issue_date > '{two_years_ago}'",
            '$select': 'latitude,longitude,valuation,permit_type',
            '$order': 'issue_date DESC'
        }
        
        try:
            response = requests.get(LADBS_PERMITS_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            all_permits.extend(data)
            print(f"  Descargados {len(all_permits)} permisos...")
            
            if len(data) < limit:
                break
                
            offset += limit
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    if not all_permits:
        print("No se encontraron permisos")
        return {}
    
    df = pd.DataFrame(all_permits)
    
    # Limpiar datos
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['valuation'] = pd.to_numeric(df['valuation'], errors='coerce')
    
    df = df.dropna(subset=['latitude', 'longitude', 'valuation'])
    df = df[df['valuation'] > 20000]  # Solo permisos > $20k
    
    print(f"\nPermisos válidos después de filtrar: {len(df)}")
    print(f"Inversión total: ${df['valuation'].sum():,.0f}")
    print(f"Promedio por permiso: ${df['valuation'].mean():,.0f}")
    
    # Agrupar por celda
    cell_investments = {}
    
    for _, row in df.iterrows():
        i, j = assign_to_cell(row['latitude'], row['longitude'])
        if i is not None:
            key = (i, j)
            cell_investments[key] = cell_investments.get(key, 0) + row['valuation']
    
    print(f"\nCeldas con inversión: {len(cell_investments)}")
    
    # Normalizar
    if cell_investments:
        max_inv = max(cell_investments.values())
        cell_investments = {k: v/max_inv for k, v in cell_investments.items()}
        print(f"Inversión máxima en una celda: ${max_inv:,.0f}")
    
    return cell_investments

def create_simple_matrix():
    """Genera matriz 20x20 basada solo en permisos"""
    print("\n=== Community Vibe Matrix (LADBS Only) ===\n")
    
    investments = download_and_process_permits()
    
    matrix = [[0.0 for _ in range(20)] for _ in range(20)]
    
    for i in range(20):
        for j in range(20):
            matrix[i][j] = investments.get((i, j), 0.0)
    
    max_score = max(max(row) for row in matrix)
    
    return matrix, max_score

def save_json():
    """Guarda el JSON"""
    matrix, max_score = create_simple_matrix()
    
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    
    obj = [{
        "Aspect": "CommunityVibe",
        "CommunityVibMatrix": matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": lat_span / 20,
        "HorizontalStep": lon_span / 20,
        "MaxScore": max_score,
        "Unit": "investment_index (normalized 0-1)",
        "Source": "LADBS Building Permits (2 years, >$20k)"
    }]
    
    json_dir = Path(__file__).parent.parent / 'city_stats' / 'jsons'
    json_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = json_dir / f"community_vibe_matrix_20x20_{ts}.json"
    
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON guardado en: {out_path}")
    print("\n✓ Listo para integrarse en app.py (índice 10)")

if __name__ == "__main__":
    save_json()
