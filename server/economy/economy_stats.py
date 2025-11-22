import requests
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# --- Constants: Your LA Perimeter ---
BOUND_W, BOUND_E = -118.6057, -118.1236
BOUND_N, BOUND_S = 34.3344, 33.8624

# 1. Fetch Income Data (Via Census API)
# Variable B19013_001E = Median Household Income
print("1. 📡 Fetching Income Data from Census API...")
api_url = "https://api.census.gov/data/2021/acs/acs5?get=NAME,B19013_001E&for=tract:*&in=state:06&in=county:037"
resp = requests.get(api_url)
data = resp.json()

# Convert to DataFrame
df_income = pd.DataFrame(data[1:], columns=data[0])
# Create a unique 'GEOID' to link tables (State + County + Tract)
df_income['GEOID'] = df_income['state'] + df_income['county'] + df_income['tract']
df_income['Median_Income'] = pd.to_numeric(df_income['B19013_001E'], errors='coerce')

# Remove invalid/sentinel values (Census uses -666666666 for missing data)
df_income = df_income[df_income['Median_Income'] > 0].copy()

# 2. Fetch Coordinate Data (Via Census Gazetteer)
# This file contains the Latitude/Longitude for every tract in California
print("2. 🗺️  Fetching Coordinate Data (Gazetteer)...")
geo_url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2021_Gazetteer/2021_gaz_tracts_06.txt"
# The gazetteer is a tab-separated text file
df_geo = pd.read_csv(geo_url, sep='\t', dtype={'GEOID': str})

# Clean up column names (they often have trailing spaces)
df_geo.columns = [c.strip() for c in df_geo.columns]
df_geo['INTPTLAT'] = pd.to_numeric(df_geo['INTPTLAT'], errors='coerce')
df_geo['INTPTLONG'] = pd.to_numeric(df_geo['INTPTLONG'], errors='coerce')

# 3. Merge Data
print("3. 🔄 Merging datasets...")
# We join on the 11-digit GEOID
df_merged = pd.merge(df_income, df_geo[['GEOID', 'INTPTLAT', 'INTPTLONG']], on='GEOID', how='inner')

# 4. Filter by Your Perimeter
print("4. 🔍 Applying spatial filter...")
df_filtered = df_merged[
    (df_merged['INTPTLONG'] >= BOUND_W) & 
    (df_merged['INTPTLONG'] <= BOUND_E) & 
    (df_merged['INTPTLAT']  >= BOUND_S) & 
    (df_merged['INTPTLAT']  <= BOUND_N)
].copy()

# 5. Results
print(f"\n✅ Found {len(df_filtered)} census tracts inside your perimeter.")
print("\n--- Sample Results (Lat/Lon included) ---")
# Select clean columns to display
display_cols = ['GEOID', 'Median_Income', 'INTPTLAT', 'INTPTLONG']
print(df_filtered[display_cols].head(10))

if not df_filtered.empty:
    avg_val = df_filtered['Median_Income'].mean()
    print(f"\nAverage Household Income in this specific area: ${avg_val:,.2f}")

# ... [Fetching logic from previous step would go here] ...
# For this example, I will assume 'df_filtered' is ready. 
# It must have columns: 'INTPTLAT', 'INTPTLONG', 'Median_Income'

def create_income_grid(df, bounds, grid_size=10):
    """
    Divides the area into a grid_size x grid_size matrix.
    Returns a matrix where each cell is the average income of tracts in that square.
    """
    w, e, n, s = bounds['w'], bounds['e'], bounds['n'], bounds['s']
    
    # 1. Define the edges of the grid cells
    # linspace creates specific cut points from West to East and South to North
    lat_bins = np.linspace(s, n, grid_size + 1)
    lon_bins = np.linspace(w, e, grid_size + 1)
    
    # 2. Create the empty matrix (using NaN for empty squares)
    # We use grid_size (rows) x grid_size (cols)
    income_matrix = np.full((grid_size, grid_size), np.nan)
    
    print(f"Dividing area into {grid_size}x{grid_size} squares...")
    
    # 3. Iterate through every square in the grid
    # i = row index (Latitude), j = col index (Longitude)
    # We go backwards on 'i' because matrices start from top-left (North), 
    # but lat increases bottom-up.
    for i in range(grid_size):
        for j in range(grid_size):
            
            # Define the small square boundaries
            # Lat (Rows): From Top (High Lat) to Bottom (Low Lat)
            cell_top = lat_bins[grid_size - i]     # e.g., Index 10
            cell_bottom = lat_bins[grid_size - i - 1] # e.g., Index 9
            
            # Lon (Cols): From Left (West) to Right (East)
            cell_left = lon_bins[j]
            cell_right = lon_bins[j+1]
            
            # 4. Filter: Find all tracts inside this tiny square
            # We check if the tract's center point is inside the cell
            tracts_in_cell = df[
                (df['INTPTLAT'] <= cell_top) & 
                (df['INTPTLAT'] > cell_bottom) & 
                (df['INTPTLONG'] >= cell_left) & 
                (df['INTPTLONG'] < cell_right)
            ]
            
            # 5. Calculate Average Income for this square
            if not tracts_in_cell.empty:
                # Filter out invalid values (negative or extremely small)
                valid_tracts = tracts_in_cell[tracts_in_cell['Median_Income'] > 0]
                
                if not valid_tracts.empty:
                    avg_income = valid_tracts['Median_Income'].mean()
                    income_matrix[i, j] = avg_income
                else:
                    income_matrix[i, j] = 0.0
                
                # Optional: Print debug for non-empty cells
                # print(f"Cell ({i},{j}): ${avg_income:,.0f} ({len(valid_tracts)} tracts)")
            else:
                # No tracts found in this square (ocean, mountain, or just empty)
                income_matrix[i, j] = 0.0 # Or np.nan
                
    return income_matrix, lat_bins, lon_bins

# --- EXECUTION ---
def main():
    """
    Main function: Fetch census data, create income grid, and display results
    """
    print("="*70)
    print("LA County Income Analysis - Census Data Grid")
    print("="*70)
    print()
    
    bounds = {'w': BOUND_W, 'e': BOUND_E, 'n': BOUND_N, 's': BOUND_S}
    
    try:
        # Let's make a 20x20 grid (400 regions total)
        grid_matrix, lats, lons = create_income_grid(df_filtered, bounds, grid_size=20)
        
        print("\n--- Resulting Income Matrix (USD) ---")
        print("Rows = North to South, Cols = West to East")
        
        # Normalize the matrix to 0-1 range for display
        valid_values = grid_matrix[~np.isnan(grid_matrix)]
        if len(valid_values) > 0:
            min_val = np.nanmin(grid_matrix)
            max_val = np.nanmax(grid_matrix)
            value_range = max_val - min_val if max_val != min_val else 1
            
            normalized_matrix = np.where(
                np.isnan(grid_matrix),
                np.nan,
                (grid_matrix - min_val) / value_range
            )
            
            print(f"\nIncome Range: ${min_val:,.0f} - ${max_val:,.0f}")
            print(f"\nNormalized Matrix (0.0 to 1.0):")
            
            for row in normalized_matrix:
                for val in row:
                    if np.isnan(val):
                        print("  N/A  ", end=" ")
                    else:
                        print(f"{val:.4f}", end=" ")
                print()
            
            # Save to JSON
            save_income_matrix_to_json(normalized_matrix, grid_size=20)
        else:
            print("❌ No valid income data found in the grid.")
            
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()


def save_income_matrix_to_json(matrix, grid_size=20, output_dir="JSON"):
    """
    Save the normalized income matrix to JSON file in the specified format
    
    Args:
        matrix: The normalized income matrix
        grid_size: Grid dimensions
        output_dir: Output directory for JSON file
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Calculate grid steps
        lat_range = BOUND_N - BOUND_S
        lon_range = BOUND_E - BOUND_W
        vertical_step = lat_range / grid_size
        horizontal_step = lon_range / grid_size
        
        # Convert NaN to 0 for JSON serialization
        matrix_clean = np.where(np.isnan(matrix), 0.0, matrix)
        
        # Create JSON in the specified format
        json_data = [{
            "Aspect": "mean_income",
            "matrix": matrix_clean.tolist(),
            "Norigin": BOUND_N,
            "WOrigin": BOUND_W,
            "VerticalStep": vertical_step,
            "HorizontalStep": horizontal_step
        }]
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        filename = f"income_matrix_{grid_size}x{grid_size}_{timestamp}.json"
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\n✅ JSON saved to: {output_path}")
        print(f"   Format: Normalized income matrix (0.0 to 1.0)")
        print(f"   Grid size: {grid_size}x{grid_size}")
        print(f"   North origin (Norigin): {BOUND_N}°")
        print(f"   West origin (WOrigin): {BOUND_W}°")
        print(f"   Vertical step: {vertical_step:.6f}°")
        print(f"   Horizontal step: {horizontal_step:.6f}°")
        
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")


if __name__ == "__main__":
    main()
