import requests
import json
import numpy as np
from datetime import datetime

# --- Configuration ---
# Bounding Box (South, West, North, East)
BBOX = (33.8624, -118.6057, 34.3344, -118.1236)
BOUND_S, BOUND_W, BOUND_N, BOUND_E = BBOX

# --- Overpass Query ---
# We query specifically for elements related to mental and physical wellbeing
query = f"""
[out:json][timeout:60];
(
  // --- 1. NATURE & RELAXATION (Green/Blue Spaces) ---
  nwr["leisure"="park"]{BBOX};
  nwr["leisure"="garden"]{BBOX};
  nwr["leisure"="nature_reserve"]{BBOX};
  nwr["natural"="beach"]{BBOX};
  nwr["natural"="wood"]{BBOX};      // Woods
  nwr["landuse"="forest"]{BBOX};    // Forests
  nwr["natural"="water"]{BBOX};     // Lakes/Ponds

  // --- 2. ACTIVE LIVING (Physical Health) ---
  nwr["leisure"="playground"]{BBOX};      // Kids/Family
  nwr["leisure"="pitch"]{BBOX};           // Soccer, Baseball, Tennis courts
  nwr["leisure"="fitness_station"]{BBOX}; // Outdoor gyms/Calisthenics
  nwr["leisure"="track"]{BBOX};           // Running tracks
  nwr["sport"="swimming"]{BBOX};

  // --- 3. COMMUNITY & AMENITIES (Social/Comfort) ---
  nwr["amenity"="library"]{BBOX};          // Mental wellbeing/Quiet space
  nwr["amenity"="community_centre"]{BBOX}; // Social wellbeing
  nwr["amenity"="drinking_water"]{BBOX};   // Basic health necessity
  nwr["place"="square"]{BBOX};             // Public plazas
);
out body;
>;
out skel qt;
"""

URL = "https://overpass-api.de/api/interpreter"


def create_wellbeing_matrix(elements, grid_size=20):
    """
    Creates a matrix representing the BBOX divided into grid_size x grid_size squares.
    Each element contains the count of wellbeing features in that grid square.
    
    Args:
        elements: List of OSM elements with lat/lon coordinates
        grid_size: Number of rows/columns in the grid (default: 20)
        
    Returns:
        tuple: (normalized_matrix, matrix, lat_bins, lon_bins)
    """
    print(f"\n📊 Creating {grid_size}x{grid_size} wellbeing matrix...")
    
    # Define grid boundaries
    lat_bins = np.linspace(BOUND_S, BOUND_N, grid_size + 1)
    lon_bins = np.linspace(BOUND_W, BOUND_E, grid_size + 1)
    
    # Initialize matrix with zeros
    matrix = np.zeros((grid_size, grid_size))
    
    # Count elements in each grid square
    for element in elements:
        tags = element.get('tags', {})
        
        # Skip elements without tags or location data
        if not tags:
            continue
        
        # Get coordinates
        lat = None
        lon = None
        
        if 'lat' in element and 'lon' in element:
            lat = element['lat']
            lon = element['lon']
        
        # If element is a way or relation, try to get centroid
        if lat is None and 'center' in element:
            lat = element['center'].get('lat')
            lon = element['center'].get('lon')
        
        if lat is None or lon is None:
            continue
        
        # Check if element is within bounds
        if not (BOUND_S <= lat <= BOUND_N and BOUND_W <= lon <= BOUND_E):
            continue
        
        # Find grid cell
        # Row: from North (top) to South (bottom)
        row = np.searchsorted(lat_bins, lat, side='right') - 1
        # Col: from West (left) to East (right)
        col = np.searchsorted(lon_bins, lon, side='right') - 1
        
        # Clamp to valid indices
        row = np.clip(row, 0, grid_size - 1)
        col = np.clip(col, 0, grid_size - 1)
        
        # Increment count in grid cell
        matrix[grid_size - 1 - row][col] += 1  # Flip row so (0,0) is northwest
    
    print(f"✅ Processed {len(elements)} elements")
    print(f"   Total features in matrix: {int(np.sum(matrix))}")
    
    # Normalize matrix to 0-1 range
    max_val = np.max(matrix)
    if max_val > 0:
        normalized_matrix = matrix / max_val
    else:
        normalized_matrix = matrix
    
    return normalized_matrix, matrix, lat_bins, lon_bins


def save_wellbeing_matrix_to_json(normalized_matrix, grid_size=20, output_dir="JSON"):
    """
    Save the wellbeing matrix to JSON file
    
    Args:
        normalized_matrix: The normalized wellbeing matrix
        grid_size: Grid dimensions
        output_dir: Output directory for JSON file
    """
    try:
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Calculate grid steps
        lat_range = BOUND_N - BOUND_S
        lon_range = BOUND_E - BOUND_W
        vertical_step = lat_range / grid_size
        horizontal_step = lon_range / grid_size
        
        # Create JSON structure
        json_data = [{
            "Aspect": "Wellbeing",
            "WellbeingMatrix": normalized_matrix.tolist(),
            "Norigin": BOUND_N,
            "WOrigin": BOUND_W,
            "VerticalStep": vertical_step,
            "HorizontalStep": horizontal_step
        }]
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        filename = f"wellbeing_matrix_{grid_size}x{grid_size}_{timestamp}.json"
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\n✅ JSON saved to: {output_path}")
        print(f"   Grid size: {grid_size}x{grid_size}")
        print(f"   North origin: {BOUND_N}°")
        print(f"   West origin: {BOUND_W}°")
        print(f"   Vertical step: {vertical_step:.6f}°")
        print(f"   Horizontal step: {horizontal_step:.6f}°")
        
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")


def classify_element(tags):
    """Helper to categorize an OSM element based on its tags."""
    # Green Spaces
    if tags.get('leisure') == 'park': return 'Parks'
    if tags.get('leisure') == 'garden': return 'Gardens'
    if tags.get('leisure') == 'nature_reserve': return 'Nature Reserves'
    if tags.get('natural') == 'wood' or tags.get('landuse') == 'forest': return 'Forests/Woods'
    if tags.get('natural') == 'water': return 'Lakes/Water Bodies'
    if tags.get('natural') == 'beach': return 'Beaches'
    
    # Active Living
    if tags.get('leisure') == 'playground': return 'Playgrounds'
    if tags.get('leisure') == 'pitch': return 'Sports Fields/Courts'
    if tags.get('leisure') == 'fitness_station': return 'Outdoor Gyms'
    if tags.get('leisure') == 'track': return 'Running Tracks'
    if tags.get('sport') == 'swimming': return 'Swimming Pools'
    
    # Community
    if tags.get('amenity') == 'library': return 'Libraries'
    if tags.get('amenity') == 'community_centre': return 'Community Centers'
    if tags.get('amenity') == 'drinking_water': return 'Drinking Water Points'
    if tags.get('place') == 'square': return 'Public Squares'
    
    return 'Other'

def fetch_wellbeing_stats():
    print(f"Querying OpenStreetMap for wellbeing elements in bbox {BBOX}...")
    try:
        response = requests.get(URL, params={'data': query})
        response.raise_for_status()
        data = response.json()
        elements = data.get('elements', [])
        
        stats = {}
        
        print(f"\nProcessing {len(elements)} raw map elements...")
        
        for el in elements:
            tags = el.get('tags', {})
            # We only count elements that actually have tags (skipping geometry nodes)
            if not tags: continue
            
            category = classify_element(tags)
            if category != 'Other':
                stats[category] = stats.get(category, 0) + 1
                
        # --- Display Results ---
        print("\n====== CITY WELLBEING INDEX (COUNTS) ======")
        
        print("\n--- 🌿 Nature & Relaxation ---")
        for k in ['Parks', 'Gardens', 'Nature Reserves', 'Forests/Woods', 'Beaches', 'Lakes/Water Bodies']:
            if k in stats: print(f"{k}: {stats[k]}")

        print("\n--- 🏃 Active Living ---")
        for k in ['Playgrounds', 'Sports Fields/Courts', 'Outdoor Gyms', 'Running Tracks', 'Swimming Pools']:
            if k in stats: print(f"{k}: {stats[k]}")

        print("\n--- 🤝 Community & Amenities ---")
        for k in ['Libraries', 'Community Centers', 'Drinking Water Points', 'Public Squares']:
            if k in stats: print(f"{k}: {stats[k]}")

        # Create wellbeing matrix
        normalized_matrix, raw_matrix, lat_bins, lon_bins = create_wellbeing_matrix(elements, grid_size=20)
        
        # Display matrix statistics
        print("\n====== WELLBEING MATRIX STATISTICS ======")
        print(f"Matrix size: 20x20")
        print(f"Total wellbeing features: {int(np.sum(raw_matrix))}")
        print(f"Max features in a cell: {int(np.max(raw_matrix))}")
        print(f"Min features in a cell: {int(np.min(raw_matrix))}")
        print(f"Average features per cell: {np.mean(raw_matrix):.2f}")
        
        # Display normalized matrix
        print("\n--- Normalized Wellbeing Matrix (0.0 to 1.0) ---")
        print("(0,0) = Northwest corner\n")
        for row in normalized_matrix:
            for val in row:
                print(f"{val:.4f}", end=" ")
            print()
        
        # Save to JSON
        save_wellbeing_matrix_to_json(normalized_matrix, grid_size=20)
        
        # Save raw data
        with open("la_wellbeing_data.json", "w") as f:
            json.dump(data, f)
        print("\n[INFO] Full dataset saved to 'la_wellbeing_data.json'")

    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()




if __name__ == "__main__":
    fetch_wellbeing_stats()
