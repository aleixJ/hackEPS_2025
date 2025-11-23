import requests
import json
from datetime import datetime
import os

# --- Configuration ---
# Bounding Box
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude
BBOX = (BOUND_S, BOUND_W, BOUND_N, BOUND_E)

# Grid dimensions
GRID_SIZE = 20

# Calculate step sizes
VERTICAL_STEP = (BOUND_N - BOUND_S) / GRID_SIZE      # Latitude step
HORIZONTAL_STEP = (BOUND_E - BOUND_W) / GRID_SIZE    # Longitude step

overpass_url = "http://overpass-api.de/api/interpreter"

# --- Overpass Query for Wheelchair Accessible Places ---
def get_wheelchair_query():
    """Generate Overpass query for wheelchair accessible places."""
    return f"""
[out:json][timeout:120];
(
  nwr["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="hospital"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="pharmacy"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="library"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="restaurant"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="cafe"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="parking"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="toilets"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="public_building"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["amenity"="community_centre"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["leisure"="park"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
  nwr["leisure"="playground"]["wheelchair"="yes"]({BOUND_S},{BOUND_W},{BOUND_N},{BOUND_E});
);
out body;
>;
out skel qt;
"""


def get_grid_cell(lat, lon):
    """
    Determine which grid cell a coordinate belongs to.
    Returns (row, col) where (0,0) is top-left (northwest)
    """
    # Calculate row (latitude): top is north (high values), bottom is south (low values)
    row = int((BOUND_N - lat) / VERTICAL_STEP)
    
    # Calculate column (longitude): left is west (low values), right is east (high values)
    col = int((lon - BOUND_W) / HORIZONTAL_STEP)
    
    # Clamp to grid bounds
    row = max(0, min(GRID_SIZE - 1, row))
    col = max(0, min(GRID_SIZE - 1, col))
    
    return row, col


def create_accessibility_matrix(places_list):
    """
    Create a 20x20 matrix of wheelchair accessible place counts.
    Each cell contains the count of accessible places in that grid square.
    """
    print("\n📊 Creating 20x20 accessibility matrix...")
    
    # Initialize 20x20 matrix with zeros
    matrix = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Count places in each grid cell
    for place in places_list:
        lat = place.get('lat')
        lon = place.get('lon')
        
        if lat is not None and lon is not None:
            row, col = get_grid_cell(lat, lon)
            matrix[row][col] += 1
    
    # Find max value for normalization
    max_value = max(max(row) for row in matrix) if any(any(row) for row in matrix) else 1
    
    if max_value == 0:
        max_value = 1
    
    # Normalize matrix (0-1 range)
    normalized_matrix = [[float(cell) / max_value for cell in row] for row in matrix]
    
    print(f"✅ Matrix created: {len(places_list)} places distributed across {GRID_SIZE}x{GRID_SIZE} grid")
    print(f"   Max places in single cell: {max_value}")
    
    return normalized_matrix


def save_accessibility_matrix_to_json(matrix):
    """
    Save the accessibility matrix to JSON file in the specified format.
    """
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    output_file = f"accessibility_matrix_20x20_{timestamp}.json"
    
    output_data = [
        {
            "Aspect": "Wheelchair Accessibility",
            "AccessibilityMatrix": matrix,
            "Norigin": BOUND_N,
            "WOrigin": BOUND_W,
            "VerticalStep": VERTICAL_STEP,
            "HorizontalStep": HORIZONTAL_STEP
        }
    ]
    
    output_path = os.path.join("../..", "JSON", output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Matrix saved to: {output_path}")
    return output_path


def fetch_wheelchair_accessible_places():
    """
    Fetch all wheelchair accessible places from OpenStreetMap,
    create a 20x20 matrix, and export to JSON.
    """
    print("="*70)
    print("🦽 WHEELCHAIR ACCESSIBILITY ANALYSIS - LA COUNTY")
    print("="*70)
    print(f"\n🔍 Querying OpenStreetMap for wheelchair accessible places...")
    print(f"   Bounding Box: N={BOUND_N}, S={BOUND_S}, E={BOUND_E}, W={BOUND_W}")
    print(f"   Grid: {GRID_SIZE}x{GRID_SIZE}")
    print(f"   Vertical Step: {VERTICAL_STEP:.6f}°")
    print(f"   Horizontal Step: {HORIZONTAL_STEP:.6f}°\n")
    
    try:
        wheelchair_query = get_wheelchair_query()
        response = requests.get(overpass_url, params={'data': wheelchair_query}, timeout=120)
        response.raise_for_status()
        data = response.json()
        elements = data.get('elements', [])
        
        print(f"✅ Found {len(elements)} elements from OpenStreetMap\n")
        
        # Process elements
        places_list = []
        
        for element in elements:
            tags = element.get('tags', {})
            
            # Skip elements without tags or not wheelchair accessible
            if not tags or tags.get('wheelchair') != 'yes':
                continue
            
            # Extract location info
            lat = element.get('lat')
            lon = element.get('lon')
            
            # If element is a way/relation, try to get center
            if lat is None and 'center' in element:
                lat = element['center'].get('lat')
                lon = element['center'].get('lon')
            
            if lat is not None and lon is not None:
                place_info = {
                    'name': tags.get('name', 'Unknown'),
                    'lat': lat,
                    'lon': lon,
                    'address': tags.get('addr:street', ''),
                }
                places_list.append(place_info)
        
        # --- Display Statistics ---
        print(f"📊 STATISTICS")
        print("="*70)
        print(f"  Total wheelchair accessible places: {len(places_list)}")
        print(f"  Region: Los Angeles County")
        print(f"  Grid size: {GRID_SIZE}x{GRID_SIZE} cells\n")
        
        if places_list:
            # Display first 20 places
            print(f"📍 SAMPLE OF ACCESSIBLE PLACES (showing first 20 of {len(places_list)})")
            print("="*70)
            for idx, place in enumerate(places_list[:20], 1):
                print(f"\n{idx}. {place['name']}")
                print(f"   Location: ({place['lat']:.6f}, {place['lon']:.6f})")
                if place['address']:
                    print(f"   Address: {place['address']}")
        else:
            print("❌ No wheelchair accessible places found\n")
        
        # --- Create and save matrix ---
        if places_list:
            matrix = create_accessibility_matrix(places_list)
            output_path = save_accessibility_matrix_to_json(matrix)
            
            print("\n" + "="*70)
            print("✅ WHEELCHAIR ACCESSIBILITY ANALYSIS COMPLETE")
            print("="*70)
        else:
            print("⚠️  No data to create matrix")
        
        return places_list
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout: Overpass API took too long to respond")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fetch_wheelchair_accessible_places()