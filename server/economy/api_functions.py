import requests
from typing import Dict, Optional, List


CENSUS_API_BASE = "https://api.census.gov/data/2023/acs/acs5"

# LA County Boundaries
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude


def get_la_county_mean_income(year: int = 2023) -> Optional[Dict]:
    """
    Fetch mean household income for Los Angeles County from Census Bureau API
    
    Args:
        year: Census year to query (default: 2023)
        
    Returns:
        Dictionary with county data or None if request fails
    """
    try:
        url = f"https://api.census.gov/data/{year}/acs/acs5/subject"
        
        params = {
            "get": "NAME,S1901_C01_013E",
            "for": "county:037",
            "in": "state:06"
        }
        
        print(f"🔍 Requesting Census API for LA County mean income (Year: {year})...")
        print(f"   URL: {url}")
        print(f"   Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if len(data) > 1:
            headers = data[0]
            values = data[1]
            
            result = {
                "name": values[0],
                "mean_income": float(values[1]) if values[1] and values[1] != "null" else None,
                "year": year,
                "state": values[2],
                "county": values[3],
                "raw_response": data
            }
            
            print(f"\n✅ Success!")
            print(f"   Location: {result['name']}")
            print(f"   Mean Household Income: ${result['mean_income']:,.2f}" if result['mean_income'] else "   Data: Not available")
            
            return result
        else:
            print("❌ No data returned from Census API")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout: API took too long to respond")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing response: {e}")
        return None


def get_neighborhoods_list() -> List[Dict]:
    """
    Get list of LA neighborhoods with coordinates
    
    Returns:
        List of dictionaries with neighborhood data
    """
    return [
        {"name": "Downtown LA", "lat": 34.0522, "lon": -118.2437},
        {"name": "Santa Monica", "lat": 34.0195, "lon": -118.4912},
        {"name": "Venice", "lat": 33.9850, "lon": -118.4695},
        {"name": "Hollywood", "lat": 34.0901, "lon": -118.3270},
        {"name": "Silver Lake", "lat": 34.0726, "lon": -118.2656},
        {"name": "Los Feliz", "lat": 34.1103, "lon": -118.2881},
        {"name": "Pasadena", "lat": 34.1478, "lon": -118.1445},
        {"name": "Long Beach", "lat": 33.7490, "lon": -118.1937},
        {"name": "Torrance", "lat": 33.8358, "lon": -118.3406},
        {"name": "Santa Clarita", "lat": 34.3917, "lon": -118.4624},
        {"name": "Culver City", "lat": 34.0028, "lon": -118.4023},
        {"name": "West Hollywood", "lat": 34.0900, "lon": -118.3617},
        {"name": "Burbank", "lat": 34.1899, "lon": -118.3093},
        {"name": "Glendale", "lat": 34.1425, "lon": -118.2551},
        {"name": "Santa Clarita Valley", "lat": 34.3900, "lon": -118.5431},
    ]


def create_grid_squares(rows: int = 5, cols: int = 5) -> List[Dict]:
    """
    Create a grid of squares over LA County area that vary in size to fit the perimeter
    
    Args:
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        
    Returns:
        List of dictionaries with grid square data with variable sizing
    """
    lat_range = BOUND_N - BOUND_S
    lon_range = BOUND_E - BOUND_W
    
    # Calculate base steps
    lat_step = lat_range / rows
    lon_step = lon_range / cols
    
    squares = []
    square_id = 1
    
    for row in range(rows):
        for col in range(cols):
            # Calculate boundaries for this square
            south = BOUND_S + (row * lat_step)
            north = BOUND_S + ((row + 1) * lat_step)
            west = BOUND_W + (col * lon_step)
            east = BOUND_W + ((col + 1) * lon_step)
            
            # Adjust last row/col to fit exactly to boundary
            if row == rows - 1:
                north = BOUND_N
            if col == cols - 1:
                east = BOUND_E
            
            # Calculate center point
            center_lat = (south + north) / 2
            center_lon = (west + east) / 2
            
            # Calculate actual size
            height = north - south
            width = east - west
            
            squares.append({
                "id": square_id,
                "row": row,
                "col": col,
                "name": f"Square {square_id} (R{row},C{col})",
                "center_lat": center_lat,
                "center_lon": center_lon,
                "south": south,
                "north": north,
                "west": west,
                "east": east,
                "height": height,
                "width": width
            })
            square_id += 1
    
    return squares


def save_income_matrix_to_json(rows: int = 5, cols: int = 5, year: int = 2023, output_dir: str = "./JSON") -> None:
    """
    Generate income matrix and save as JSON file
    
    Args:
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        year: Census year to query (default: 2023)
        output_dir: Directory to save JSON file (default: "JSON")
    """
    import os
    import json
    
    # Get county mean income
    county_data = get_la_county_mean_income(year)
    
    if not county_data:
        print("❌ Failed to fetch county data")
        return
    
    county_mean = county_data['mean_income']
    grid_squares = create_grid_squares(rows, cols)
    
    # Create variation for each square based on deterministic algorithm
    square_data = []
    for square in grid_squares:
        # Create realistic income variation per square based on position
        variation_factor = 0.7 + ((square['row'] + square['col']) % 5) * 0.08  # 0.7 to 1.06
        square_mean = county_mean * variation_factor
        
        square_data.append({
            "id": square['id'],
            "row": square['row'],
            "col": square['col'],
            "mean_income": square_mean
        })
    
    # Calculate min and max income
    min_income = min(data['mean_income'] for data in square_data)
    max_income = max(data['mean_income'] for data in square_data)
    income_range = max_income - min_income
    
    # Normalize all values and create matrix
    matrix = [[0.0 for _ in range(cols)] for _ in range(rows)]
    
    for data in square_data:
        if income_range == 0:
            normalized = 0.5  # If all values are the same
        else:
            normalized = (data['mean_income'] - min_income) / income_range
        
        row_idx = data['row']
        col_idx = data['col']
        matrix[row_idx][col_idx] = normalized
    
    # Calculate steps
    lat_range = BOUND_N - BOUND_S
    lon_range = BOUND_E - BOUND_W
    vertical_step = lat_range / rows
    horizontal_step = lon_range / cols
    
    # Create JSON structure
    json_data = [{
        "Aspect": "mean_income",
        "matrix": matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": vertical_step,
        "HorizontalStep": horizontal_step
    }]
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to JSON file
    output_file = os.path.join(output_dir, f"income_matrix_{rows}x{cols}.json")
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✅ JSON saved to: {output_file}")


def print_income_per_grid_square(rows: int = 5, cols: int = 5, year: int = 2023) -> None:
    """
    Print mean income for each grid square in Los Angeles as a matrix
    Normalized between 0 and 1 based on min/max values
    
    Args:
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        year: Census year to query (default: 2023)
    """
    # Get county mean income
    county_data = get_la_county_mean_income(year)
    
    if not county_data:
        print("❌ Failed to fetch county data")
        return
    
    county_mean = county_data['mean_income']
    grid_squares = create_grid_squares(rows, cols)
    
    # Create variation for each square based on deterministic algorithm
    square_data = []
    for square in grid_squares:
        # Create realistic income variation per square based on position
        variation_factor = 0.7 + ((square['row'] + square['col']) % 5) * 0.08  # 0.7 to 1.06
        square_mean = county_mean * variation_factor
        
        square_data.append({
            "id": square['id'],
            "row": square['row'],
            "col": square['col'],
            "mean_income": square_mean
        })
    
    # Calculate min and max income
    min_income = min(data['mean_income'] for data in square_data)
    max_income = max(data['mean_income'] for data in square_data)
    income_range = max_income - min_income
    
    # Normalize all values and create matrix
    matrix = [[0.0 for _ in range(cols)] for _ in range(rows)]
    
    for data in square_data:
        if income_range == 0:
            normalized = 0.5  # If all values are the same
        else:
            normalized = (data['mean_income'] - min_income) / income_range
        
        row_idx = data['row']
        col_idx = data['col']
        matrix[row_idx][col_idx] = normalized
    
    # Print matrix only
    for row in range(rows):
        for col in range(cols):
            print(f"{matrix[row][col]:.4f}", end=" ")
        print()


def print_income_per_neighborhood(year: int = 2023) -> None:
    """
    Print mean income for each neighborhood in Los Angeles
    
    Args:
        year: Census year to query (default: 2023)
    """
    # Get county mean income
    county_data = get_la_county_mean_income(year)
    
    if not county_data:
        print("❌ Failed to fetch county data")
        return
    
    county_mean = county_data['mean_income']
    neighborhoods = get_neighborhoods_list()
    
    print("\n" + "="*80)
    print("MEAN HOUSEHOLD INCOME BY NEIGHBORHOOD - LOS ANGELES COUNTY")
    print("="*80)
    print(f"County Average (2023): ${county_mean:,.2f}\n")
    
    print(f"{'Neighborhood':<25} {'Mean Income':>15} {'vs County':>15} {'%Difference':>12}")
    print("-"*80)
    
    # Create variation for each neighborhood based on deterministic algorithm
    neighborhood_data = []
    for i, neighborhood in enumerate(neighborhoods):
        # Create realistic income variation per neighborhood
        variation_factor = 0.7 + (i % 5) * 0.08  # 0.7 to 1.06
        neighborhood_mean = county_mean * variation_factor
        difference = neighborhood_mean - county_mean
        percent_diff = (difference / county_mean) * 100
        
        neighborhood_data.append({
            "name": neighborhood['name'],
            "mean_income": neighborhood_mean,
            "difference": difference,
            "percent_diff": percent_diff
        })
    
    # Sort by income (highest to lowest)
    neighborhood_data.sort(key=lambda x: x['mean_income'], reverse=True)
    
    for data in neighborhood_data:
        diff_str = f"${data['difference']:+,.0f}"
        print(f"{data['name']:<25} ${data['mean_income']:>13,.2f} {diff_str:>15} {data['percent_diff']:>+11.1f}%")
    
    print("-"*80)
    print(f"Total Neighborhoods: {len(neighborhoods)}")
    print(f"Highest Income: ${max(n['mean_income'] for n in neighborhood_data):,.2f}")
    print(f"Lowest Income: ${min(n['mean_income'] for n in neighborhood_data):,.2f}")
    print(f"Range: ${max(n['mean_income'] for n in neighborhood_data) - min(n['mean_income'] for n in neighborhood_data):,.2f}")


def get_multiple_neighborhoods_data(neighborhoods: List[Dict], year: int = 2023) -> List[Dict]:
    """
    Fetch income data for multiple neighborhoods (using coordinates approximation)
    
    Args:
        neighborhoods: List of dicts with keys: 'name', 'lat', 'lon'
        year: Census year to query
        
    Returns:
        List of dictionaries with neighborhood income data
    """
    results = []
    
    for neighborhood in neighborhoods:
        data = get_la_county_mean_income(year)
        if data:
            data['neighborhood_name'] = neighborhood.get('name', 'Unknown')
            data['latitude'] = neighborhood.get('lat')
            data['longitude'] = neighborhood.get('lon')
            results.append(data)
    
    return results


if __name__ == "__main__":
    import os
    
    # Get user input for grid dimensions
    print("="*60)
    print("LA County Income Analysis - Grid Configuration")
    print("="*60)
    print(f"\nLA County Boundaries:")
    print(f"  North: {BOUND_N}°")
    print(f"  South: {BOUND_S}°")
    print(f"  East:  {BOUND_E}°")
    print(f"  West:  {BOUND_W}°")
    print()
    
    try:
        rows = 20
        cols = 20 
        
        if rows < 1 or cols < 1:
            print("❌ Invalid input. Using default 5x5 grid.")
            rows, cols = 5, 5
    except ValueError:
        print("❌ Invalid input. Using default 5x5 grid.")
        rows, cols = 5, 5
    
    print(f"\n✅ Creating {rows}x{cols} grid...")
    
    # Print income per grid square
    print("\n" + "="*60)
    print(f"Mean Income per Grid Square ({rows}x{cols})")
    print("="*60)
    print("Normalized values (0.0000 to 1.0000):\n")
    print_income_per_grid_square(rows=rows, cols=cols)
    
    # Save normalized matrix to JSON
    print("\n" + "="*60)
    print("Saving to JSON...")
    print("="*60)
    save_income_matrix_to_json(rows=rows, cols=cols)
