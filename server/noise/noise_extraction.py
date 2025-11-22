import requests
import json
import os
from datetime import datetime
from typing import Optional, List, Dict

# LA County Boundaries
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude

API_key = "https://data.lacity.org/resource/h73f-gn57.json"


def fetch_noise_data(limit: int = 50000) -> Optional[List[Dict]]:
    """
    Fetch noise data from LA City API
    
    Args:
        limit: Maximum number of records to fetch
        
    Returns:
        List of noise incidents or None if request fails
    """
    try:
        print("🔍 Fetching noise data from LA City API...")
        print(f"URL: {API_key}")
        print(f"Limit: {limit}\n")
        
        params = {"$limit": limit}
        response = requests.get(API_key, params=params, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 404:
            print("\n❌ HTTP Error 404: API endpoint not found")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Fetched {len(data)} noise incidents\n")
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


def create_noise_matrix(data: List[Dict], rows: int = 20, cols: int = 20) -> Optional[List[List[float]]]:
    """
    Create a noise matrix from incident data
    
    Args:
        data: List of noise incident records
        rows: Number of rows in the grid (default: 20)
        cols: Number of columns in the grid (default: 20)
        
    Returns:
        Normalized matrix with incident counts
    """
    if not data:
        print("❌ No data provided")
        return None
    
    print(f"📊 Creating {rows}x{cols} noise matrix...")
    
    # Calculate grid dimensions
    lat_range = BOUND_N - BOUND_S
    lon_range = BOUND_E - BOUND_W
    lat_step = lat_range / rows
    lon_step = lon_range / cols
    
    # Initialize matrix with zeros
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Count incidents in each grid square
    incident_count = 0
    for incident in data:
        try:
            # Extract latitude and longitude from incident
            # The API response may have different field names, try common ones
            lat = incident.get("latitude") or incident.get("lat")
            lon = incident.get("longitude") or incident.get("lon")
            
            if lat is None or lon is None:
                continue
            
            # Convert to float
            lat = float(lat)
            lon = float(lon)
            
            # Check if incident is within bounds
            if not (BOUND_S <= lat <= BOUND_N and BOUND_W <= lon <= BOUND_E):
                continue
            
            # Calculate grid position
            row = int((BOUND_N - lat) / lat_step)
            col = int((lon - BOUND_W) / lon_step)
            
            # Clamp to valid indices
            row = min(max(row, 0), rows - 1)
            col = min(max(col, 0), cols - 1)
            
            # Increment count
            matrix[row][col] += 1
            incident_count += 1
            
        except (ValueError, TypeError):
            continue
    
    print(f"✅ Counted {incident_count} incidents in the grid\n")
    
    # Normalize matrix
    flat_matrix = [val for row in matrix for val in row]
    max_val = max(flat_matrix) if flat_matrix else 1
    min_val = min(flat_matrix) if flat_matrix else 0
    range_val = max_val - min_val if max_val != min_val else 1
    
    # Normalize to 0-1 range
    normalized_matrix = []
    for row in matrix:
        normalized_row = []
        for val in row:
            if range_val == 0:
                normalized_val = 0.0
            else:
                normalized_val = (val - min_val) / range_val
            normalized_row.append(normalized_val)
        normalized_matrix.append(normalized_row)
    
    print(f"Max incidents in a square: {max_val}")
    print(f"Min incidents in a square: {min_val}")
    print(f"Normalization range: {range_val}\n")
    
    return normalized_matrix


def save_noise_matrix_to_json(matrix: List[List[float]], output_dir: str = "JSON") -> None:
    """
    Save noise matrix to JSON file
    
    Args:
        matrix: The normalized noise matrix
        output_dir: Directory to save the JSON file
    """
    if not matrix:
        print("❌ No matrix to save")
        return
    
    # Calculate grid parameters
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    lat_range = BOUND_N - BOUND_S
    lon_range = BOUND_E - BOUND_W
    vertical_step = lat_range / rows
    horizontal_step = lon_range / cols
    
    # Create JSON structure
    json_data = [{
        "Aspect": "Noise",
        "NoiseMatrix": matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": vertical_step,
        "HorizontalStep": horizontal_step
    }]
    
    # Create output directory if needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    filename = f"noise_matrix_{rows}x{cols}_{timestamp}.json"
    output_path = os.path.join(output_dir, filename)
    
    # Save JSON
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"💾 JSON saved to: {output_path}")
    print(f"   Grid size: {rows}x{cols}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.2f} KB\n")


def process_noise_data(rows: int = 20, cols: int = 20, output_dir: str = "JSON") -> None:
    """
    Complete pipeline: fetch data, create matrix, and save to JSON
    
    Args:
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        output_dir: Directory to save the output JSON
    """
    print("="*70)
    print("LA Noise Data Analysis - Matrix Generator")
    print("="*70)
    print()
    
    # Fetch data
    data = fetch_noise_data()
    if not data:
        print("❌ Failed to fetch noise data")
        return
    
    # Create matrix
    matrix = create_noise_matrix(data, rows=rows, cols=cols)
    if not matrix:
        print("❌ Failed to create matrix")
        return
    
    # Save to JSON
    save_noise_matrix_to_json(matrix, output_dir=output_dir)
    print("✅ Process completed successfully!")


if __name__ == "__main__":
    # Process noise data with 20x20 grid
    process_noise_data(rows=20, cols=20)