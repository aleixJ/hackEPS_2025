"""
Script para generar el índice de "Vibra Comunitaria" (Community Vibe Index)
Combina datos de:
1. Yelp Fusion API - "Vibra del barrio" (negocios, precios, categorías trendy)
2. LADBS Building Permits - Inversión inmobiliaria reciente

Índice 10 en la matriz unificada
"""

import requests
import pandas as pd
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple

# Configuración de coordenadas (LA bounding box)
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude

# API Keys (configura como variables de entorno o directamente aquí)
YELP_API_KEY = os.environ.get('YELP_API_KEY', 'kk7fncw1g8iPJ7zvCcixh8QME0NUndJPq-Cn617smrVFCTsTyj-DCDLLhsFTJkb5LPrCM4vlPX8wzljct4Bc3wPpseKxERsdwCL4ffpdATqC0Gjn4e1CmKmoIWYiaXYx')

# URLs de APIs
YELP_API_URL = 'https://api.yelp.com/v3/businesses/search'
LADBS_PERMITS_URL = 'https://data.lacity.org/resource/yv23-pmwf.json'  # Building and Safety Permit Information

# Categorías "trendy" para el índice hipster
TRENDY_CATEGORIES = [
    'coffee', 'coffeeroasteries', 'coffeeshops',
    'vegan', 'vegetarian',
    'yoga', 'pilates',
    'cocktailbars', 'wine_bars', 'breweries',
    'vintage', 'vintage_fashion',
    'galleries', 'artsandcrafts'
]

def get_cell_center(i: int, j: int) -> Tuple[float, float]:
    """Calcula el centro de una celda en la grid 20x20"""
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    
    horizontal_step = lon_span / 20
    vertical_step = lat_span / 20
    
    # Centro de la celda
    lat = BOUND_N - (i * vertical_step) - (vertical_step / 2)
    lon = BOUND_W + (j * horizontal_step) + (horizontal_step / 2)
    
    return lat, lon

def query_yelp_for_cell(lat: float, lon: float, radius: int = 1000) -> Dict:
    """
    Consulta Yelp API para obtener negocios cerca del centro de una celda
    
    Returns:
        Dict con métricas: avg_price, trendy_ratio, review_density, total_businesses
    """
    if not YELP_API_KEY:
        print("WARNING: YELP_API_KEY no configurada")
        return {
            'avg_price': 0,
            'trendy_ratio': 0,
            'review_density': 0,
            'total_businesses': 0
        }
    
    headers = {
        'Authorization': f'Bearer {YELP_API_KEY}'
    }
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'radius': radius,  # metros
        'limit': 50,
        'sort_by': 'review_count'
    }
    
    try:
        response = requests.get(YELP_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        businesses = data.get('businesses', [])
        
        if not businesses:
            return {
                'avg_price': 0,
                'trendy_ratio': 0,
                'review_density': 0,
                'total_businesses': 0
            }
        
        # 1. Índice de Precio Promedio (1-4 basado en $ signos)
        prices = []
        for biz in businesses:
            price = biz.get('price', '')
            if price:
                prices.append(len(price))  # '$' = 1, '$$' = 2, etc.
        
        avg_price = sum(prices) / len(prices) if prices else 0
        
        # 2. Ratio de Categorías "Trendy"
        trendy_count = 0
        for biz in businesses:
            categories = biz.get('categories', [])
            for cat in categories:
                alias = cat.get('alias', '')
                if alias in TRENDY_CATEGORIES:
                    trendy_count += 1
                    break
        
        trendy_ratio = trendy_count / len(businesses) if businesses else 0
        
        # 3. Densidad de Reviews (vibrancia)
        total_reviews = sum(biz.get('review_count', 0) for biz in businesses)
        
        return {
            'avg_price': avg_price,
            'trendy_ratio': trendy_ratio,
            'review_density': total_reviews,
            'total_businesses': len(businesses)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error consultando Yelp para ({lat}, {lon}): {e}")
        return {
            'avg_price': 0,
            'trendy_ratio': 0,
            'review_density': 0,
            'total_businesses': 0
        }

def download_ladbs_permits() -> pd.DataFrame:
    """
    Descarga permisos de construcción de LADBS (últimos 2 años)
    Filtra por valuación > $20,000 y tipos relevantes
    """
    print("Descargando permisos de construcción de LADBS...")
    
    # Fecha de hace 2 años
    two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT%H:%M:%S')
    
    # Parámetros de consulta Socrata
    params = {
        '$limit': 50000,  # Límite alto para obtener muchos registros
        '$where': f"issue_date > '{two_years_ago}'",
        '$select': 'latitude,longitude,permit_type,status_date,permit_sub_type,valuation',
        '$order': 'issue_date DESC'
    }
    
    try:
        response = requests.get(LADBS_PERMITS_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data)
        
        if df.empty:
            print("No se encontraron permisos")
            return df
        
        # Convertir lat/lon a float
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['valuation'] = pd.to_numeric(df['valuation'], errors='coerce')
        
        # Filtrar valores nulos
        df = df.dropna(subset=['latitude', 'longitude', 'valuation'])
        
        # Filtrar por valuación > $20,000
        df = df[df['valuation'] > 20000]
        
        # Filtrar por tipos relevantes (remodelación, adición)
        relevant_types = ['Bldg-Alter/Repair', 'Bldg-Addition', 'New Building']
        if 'permit_type' in df.columns:
            df = df[df['permit_type'].isin(relevant_types)]
        
        print(f"Permisos filtrados: {len(df)}")
        
        return df
        
    except Exception as e:
        print(f"Error descargando permisos LADBS: {e}")
        return pd.DataFrame()

def assign_permit_to_cell(lat: float, lon: float) -> Tuple[int, int]:
    """Asigna una coordenada a una celda de la grid 20x20"""
    if not (BOUND_S <= lat <= BOUND_N and BOUND_W <= lon <= BOUND_E):
        return None, None
    
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    
    horizontal_step = lon_span / 20
    vertical_step = lat_span / 20
    
    j = int((lon - BOUND_W) / horizontal_step)
    i = int((BOUND_N - lat) / vertical_step)
    
    # Validar límites
    if 0 <= i < 20 and 0 <= j < 20:
        return i, j
    return None, None

def calculate_permits_score_per_cell(df: pd.DataFrame) -> Dict[Tuple[int, int], float]:
    """
    Calcula el score de inversión por celda basado en permisos
    Score = Suma de valuaciones / área de celda
    """
    cell_investments = {}
    
    for _, row in df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        valuation = row['valuation']
        
        i, j = assign_permit_to_cell(lat, lon)
        
        if i is not None and j is not None:
            key = (i, j)
            if key not in cell_investments:
                cell_investments[key] = 0
            cell_investments[key] += valuation
    
    # Normalizar por área (todas las celdas tienen la misma área, así que es proporcional)
    # Convertir a score 0-1
    if cell_investments:
        max_investment = max(cell_investments.values())
        if max_investment > 0:
            cell_investments = {k: v/max_investment for k, v in cell_investments.items()}
    
    return cell_investments

def create_community_vibe_matrix_20x20():
    """
    Genera la matriz 20x20 del índice de vibra comunitaria
    Combina datos de Yelp y LADBS
    """
    print("\n=== Generando Community Vibe Matrix 20x20 ===\n")
    
    # Paso 1: Descargar permisos de construcción
    permits_df = download_ladbs_permits()
    permits_scores = calculate_permits_score_per_cell(permits_df) if not permits_df.empty else {}
    
    # Paso 2: Consultar Yelp para cada celda
    matrix = [[0.0 for _ in range(20)] for _ in range(20)]
    max_score = 0
    
    total_cells = 20 * 20
    current = 0
    
    for i in range(20):
        for j in range(20):
            current += 1
            lat, lon = get_cell_center(i, j)
            
            print(f"[{current}/{total_cells}] Procesando celda ({i}, {j}) - Centro: ({lat:.4f}, {lon:.4f})")
            
            # Obtener datos de Yelp
            yelp_data = query_yelp_for_cell(lat, lon)
            
            # Obtener score de permisos
            permits_score = permits_scores.get((i, j), 0)
            
            # Calcular score combinado
            # Normalizar componentes de Yelp
            price_score = yelp_data['avg_price'] / 4.0  # 0-1 (asumiendo max $$$$ = 4)
            trendy_score = yelp_data['trendy_ratio']  # Ya está 0-1
            vibrancy_score = min(yelp_data['review_density'] / 1000.0, 1.0)  # Cap a 1000 reviews
            
            # Fórmula del Community Vibe Index
            # 40% Yelp (precio + trendy + vibrancia) + 60% Inversión (permisos)
            yelp_component = (price_score * 0.3 + trendy_score * 0.4 + vibrancy_score * 0.3)
            combined_score = (yelp_component * 0.4) + (permits_score * 0.6)
            
            matrix[i][j] = combined_score
            max_score = max(max_score, combined_score)
            
            # Rate limiting para Yelp (si está configurado)
            if YELP_API_KEY:
                time.sleep(0.2)  # 5 requests/sec máximo
    
    # Normalizar a 0-1
    if max_score > 0:
        for i in range(20):
            for j in range(20):
                matrix[i][j] = matrix[i][j] / max_score
    
    print(f"\n✓ Matriz generada. Score máximo: {max_score:.2f}")
    
    return matrix, max_score

def save_community_vibe_json():
    """Guarda la matriz de community vibe en formato JSON"""
    matrix, max_score = create_community_vibe_matrix_20x20()
    
    lon_span = BOUND_E - BOUND_W
    lat_span = BOUND_N - BOUND_S
    vertical_step = lat_span / 20
    horizontal_step = lon_span / 20
    
    obj = [{
        "Aspect": "CommunityVibe",
        "CommunityVibMatrix": matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": vertical_step,
        "HorizontalStep": horizontal_step,
        "MaxScore": max_score,
        "Unit": "community_vibe_index (normalized 0-1)",
        "Components": {
            "yelp": "Price index + Trendy ratio + Review density (40%)",
            "permits": "Construction investment valuation (60%)"
        }
    }]
    
    # Guardar en jsons/
    json_dir = Path(__file__).parent.parent / 'city_stats' / 'jsons'
    json_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = json_dir / f"community_vibe_matrix_20x20_{ts}.json"
    
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON guardado en: {out_path}")
    return out_path

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  Community Vibe Index Generator                              ║
    ║  Combina Yelp (vibra) + LADBS (inversión)                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    IMPORTANTE: Para usar Yelp API necesitas configurar:
    export YELP_API_KEY='tu_api_key_aqui'
    
    Obtén tu API key en: https://www.yelp.com/developers
    
    Si no tienes API key, el script usará solo datos de LADBS.
    """)
    
    save_community_vibe_json()
