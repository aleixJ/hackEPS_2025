import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# --- Configuration ---
# Base URL for the LA City Data Portal (Socrata Open Data API)
BASE_URL = "https://data.lacity.org/resource"

# Resource ID for the dataset you want to query.
# This example uses the 'Crime Data from 2020 to Present' dataset.
RESOURCE_ID = "2nrs-mtv8" 

# --- Constants for SODA API ---
SODA_MAX_LIMIT = 1000 # Maximum number of records SODA returns per single request

# --- Geographic Boundary Constants for Filtering ---
# Coordinates provided by the user for the bounding box
BOUND_W = -118.6057 # West Longitude
BOUND_E = -118.1236 # East Longitude
BOUND_N = 34.3344   # North Latitude
BOUND_S = 33.8624   # South Latitude

# --- API Interaction Function ---
# Fetch data from the LA City Open Data Portal using SODA API
def fetch_la_data(resource_id: str, params: dict, max_retries: int = 3):
    """
    Fetches data from the LA City Open Data Portal using the SODA API.

    Args:
        resource_id (str): The unique ID of the dataset (e.g., '2nrs-mtv8').
        params (dict): Dictionary of SODA API query parameters (e.g., $limit, $where).
        max_retries (int): Maximum number of times to retry on connection errors.

    Returns:
        list or None: A list of dictionaries containing the data, or None on failure.
    """
    api_endpoint = f"{BASE_URL}/{resource_id}.json"
    
    for attempt in range(max_retries):
        try:
            # Make the GET request to the SODA API
            response = requests.get(api_endpoint, params=params, timeout=15)
            
            # Check for HTTP errors (4xx or 5xx)
            response.raise_for_status()
            
            # If successful, parse the JSON data
            data = response.json()
            return data

        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP error codes (4xx or 5xx)
            print(f"HTTP Error on attempt {attempt + 1}: {e}")
            print(f"Response content: {response.text}")
            return None 
            
        except requests.exceptions.RequestException as e:
            # Handle network/connection errors (Timeout, ConnectionError, etc.)
            print(f"Request failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff before retrying
                sleep_time = 2 ** attempt
                print(f"Retrying in {sleep_time} seconds seconds...")
                time.sleep(sleep_time)
            else:
                print("Max retries reached. Giving up.")
                return None
    return None

# --- Crime Data Retrieval with Pagination and Filtering ---
def _get_filters(include_date_range: bool = True, bounds: dict = None):
    """
    Internal helper to generate a list of SOQL WHERE clause filters.
    
    Args:
        include_date_range (bool): If True, adds the last 365 days filter.
        bounds (dict): A dictionary with 'N', 'S', 'E', 'W' keys for geographic filtering.
        
    Returns:
        str: A concatenated SOQL WHERE clause string.
    """
    filters = []
    
    # 1. Date Filter (Last 365 days)
    if include_date_range:
        today = datetime.now()
        one_year_ago = today - timedelta(days=365) 
        start_date_str = one_year_ago.strftime("%Y-%m-%dT00:00:00.000")
        end_date_str = today.strftime("%Y-%m-%dT23:59:59.999")
        date_filter = f"date_occ > '{start_date_str}' AND date_occ < '{end_date_str}'"
        filters.append(date_filter)

    # 2. Geographic Filter (Bounding Box)
    # FIX: Use simple comparisons on 'lat' and 'lon' columns because 'location' 
    # is a Text field, not a Geo-Spatial Point field, causing the type-mismatch error.
    if bounds and all(k in bounds for k in ['N', 'S', 'E', 'W']):
        geo_filter = (
            # Latitude: must be between South (min) and North (max)
            f"lat <= {bounds['N']} AND lat >= {bounds['S']} AND "
            # Longitude: must be between West (min) and East (max)
            f"lon <= {bounds['E']} AND lon >= {bounds['W']}"
        )
        filters.append(geo_filter)

    # Combine all filters with 'AND'
    return " AND ".join(filters)

# --- Main Function to Get Paginated Crimes ---
def get_paginated_crimes(max_records: int = 10000, bounds: dict = None):
    """
    Fetches a large number of crime records using pagination, optionally filtering
    by the last year and a geographic bounding box.

    Args:
        max_records (int): The maximum total number of records to retrieve across all pages.
        bounds (dict): Optional dictionary with 'N', 'S', 'E', 'W' keys for geographic filtering.

    Returns:
        list: A concatenated list of crime records.
    """
    all_data = []
    
    # Get the combined filter string for date and optional bounds
    filter_string = _get_filters(include_date_range=True, bounds=bounds)
    
    filter_description = "Crimes from the Last Year"
    if bounds:
        filter_description += " AND Within Bounding Box"
    
    print(f"\n--- Running Paginated Query: {filter_description} (Max {max_records} Records) ---")

    for offset in range(0, max_records, SODA_MAX_LIMIT):
        query_params = {
            "$limit": SODA_MAX_LIMIT,
            "$offset": offset,
            "$where": filter_string, 
            "$order": "date_occ DESC"
        }

        print(f"Fetching page at offset: {offset}...")
        
        page_data = fetch_la_data(RESOURCE_ID, query_params)
        
        if page_data is None:
            print("Stopping due to API error on this page.")
            break

        if not page_data:
            print("Reached the end of the available data.")
            break
            
        all_data.extend(page_data)
        
        # Stop if we've retrieved enough data or the page was less than the limit
        if len(page_data) < SODA_MAX_LIMIT:
            break

        # A small delay to be polite to the API server
        time.sleep(0.5)

    return all_data

# EXAMPLE USAGE
    # Define the coordinates provided by the user
    user_bounds = {
        'N': BOUND_N, 
        'S': BOUND_S, 
        'E': BOUND_E, 
        'W': BOUND_W
    }
    
    # Fetch up to 100 crimes that occurred in the last year and within the box
    # If the bounding box is small, 10,000 records might be enough to cover all relevant data.
    data_geo_filtered = get_paginated_crimes(max_records=100, bounds=user_bounds) 

# Print the number of records fetched per parcel
def crime_counts_by_parcels(nx: int, ny: int, max_records_per_parcel: int = 10000) -> List[Dict[str, Any]]:
	"""
	Divide the LA bounding box into an `nx` by `ny` grid and count crimes
	in each parcel over the last year.

	Args:
		nx (int): Number of parcels along the longitude (x) axis.
		ny (int): Number of parcels along the latitude (y) axis.
		max_records_per_parcel (int): Maximum records to fetch per parcel
			(passed to `get_paginated_crimes`). If a parcel contains more
			crimes than this limit the returned count will be limited.

	Returns:
		List[Dict]: A list of parcel dictionaries. Each dictionary contains:
			- `i`, `j`: grid indices (0-based)
			- `bounds`: dict with `N`, `S`, `E`, `W` keys
			- `center`: (lat, lon) tuple of parcel center
			- `count`: number of crime records fetched for that parcel
			- `records`: (optional) the raw records list (only included when
			  `max_records_per_parcel` is small; keep in mind memory usage).
	"""

	if nx <= 0 or ny <= 0:
		raise ValueError("nx and ny must be positive integers")

	lon_span = BOUND_E - BOUND_W
	lat_span = BOUND_N - BOUND_S

	lon_step = lon_span / nx
	lat_step = lat_span / ny

	results: List[Dict[str, Any]] = []

	# iterate columns (x) then rows (y). j runs south->north (0 = south)
	for i in range(nx):
		for j in range(ny):
			w = BOUND_W + i * lon_step
			e = w + lon_step
			s = BOUND_S + j * lat_step
			n = s + lat_step

			bounds = {"N": n, "S": s, "E": e, "W": w}

			# Fetch crimes for this parcel; get_paginated_crimes already
			# filters to the last year by default.
			records = get_paginated_crimes(max_records=max_records_per_parcel, bounds=bounds)

			count = len(records) if records else 0

			center_lat = (n + s) / 2.0
			center_lon = (e + w) / 2.0

			results.append(
				{
					"i": i,
					"j": j,
					"bounds": bounds,
					"center": (center_lat, center_lon),
					"count": count,
					"records": records,
				}
			)

	return results

# Function to normalize the crimes on each parcel
# Normalize a 2D crime matrix so that its maximum value becomes `target_max`.
def normalize_matrix(matrix: List[List[float]], target_max: float = 1.0) -> List[List[float]]:
	"""
	Normalize values in a 2D matrix such that the largest element becomes
	`target_max` and all other elements are scaled proportionally.

	Args:
		matrix: 2D list of numeric values (rows x cols). Rows may be empty.
		target_max: desired maximum after normalization (default 1.0).

	Returns:
		A new 2D list with normalized float values. Original matrix is not modified.

	Behavior:
		- If the matrix is empty or all-zero, the function returns a matrix
		  of the same shape filled with zeros.
		- If the maximum value is already equal to `target_max`, a copy
		  of the matrix (as floats) is returned.
	"""

	# Defensive: handle None
	if matrix is None:
		return []

	# Compute max value across the matrix
	max_val = None
	for row in matrix:
		for v in row:
			# treat non-numeric as zero via float conversion exception handling
			try:
				fv = float(v)
			except Exception:
				fv = 0.0
			if max_val is None or fv > max_val:
				max_val = fv

	if max_val is None:
		# matrix had no elements
		return [list(map(float, row)) for row in matrix]

	if max_val == 0:
		# avoid division by zero; return zero matrix of same shape
		return [[0.0 for _ in row] for row in matrix]

	scale = float(target_max) / float(max_val)

	normalized = []
	for row in matrix:
		normalized.append([float(v) * scale for v in row])

	return normalized

# Function to build the crime matrix JSON
def crime_matrix_json(nx: int, ny: int, max_records_per_parcel: int = 10000, as_json: bool = False) -> Any:
	"""
	Return a JSON-serializable structure describing crime counts across an nx-by-ny grid.

	The returned value is a list with a single object matching the requested schema:
	[{
		"Aspect": "Crime",
		"CrimeMatrix": [[...]],          # rows ordered from North to South
		"Norigin": <north_latitude>,
		"WOrigin": <west_longitude>,
		"VerticalStep": <latitude_step>,
		"HorizontalStep": <longitude_step>,
	}]

	Args:
		nx, ny: grid dimensions
		max_records_per_parcel: forwarded to `crime_counts_by_parcels`
		as_json: if True, returns a JSON string instead of Python objects
	"""

	if nx <= 0 or ny <= 0:
		raise ValueError("nx and ny must be positive integers")

	parcels = crime_counts_by_parcels(nx, ny, max_records_per_parcel=max_records_per_parcel)

	# Build matrix with rows ordered from North to South (row 0 = north)
	matrix = [[0 for _ in range(nx)] for _ in range(ny)]

	for p in parcels:
		# each parcel is a dict with keys 'i','j','count'
		row = (ny - 1) - int(p["j"])
		col = int(p["i"])
		matrix[row][col] = int(p["count"]) if p["count"] is not None else 0

	# Normalize numeric matrix so its max becomes 1.0
	normalized_matrix = normalize_matrix(matrix, target_max=1.0)

	lon_span = BOUND_E - BOUND_W
	lat_span = BOUND_N - BOUND_S

	horizontal_step = lon_span / nx
	vertical_step = lat_span / ny

	obj = [
		{
			"Aspect": "Crime",
			"CrimeMatrix": normalized_matrix,
			"Norigin": BOUND_N,
			"WOrigin": BOUND_W,
			"VerticalStep": vertical_step,
			"HorizontalStep": horizontal_step,
		}
	]

	if as_json:
		return json.dumps(obj)
	return obj

# Function to save the crime matrix JSON to a file
def save_crime_matrix_json(
	nx: int,
	ny: int,
	max_records_per_parcel: int = 10000,
	json_dir: str | Path = None,
	filename: str | None = None,
) -> Path:
	"""
	Generate the crime matrix and save it as a pretty-printed JSON file inside
	a `jsons` folder located next to this module by default.

	Args:
		nx, ny: grid dimensions
		max_records_per_parcel: forwarded to `crime_matrix_json`
		json_dir: optional directory to write to. Defaults to `server/city_stats/jsons`.
		filename: optional filename override. If omitted a timestamped name is used.

	Returns:
		Path to the saved JSON file.
	"""

	# Build the object (not a string) so we write a nicely indented file
	obj = crime_matrix_json(nx, ny, max_records_per_parcel=max_records_per_parcel, as_json=False)

	# Default folder: sibling `jsons` directory
	module_dir = Path(__file__).parent
	default_dir = module_dir / "jsons"
	out_dir = Path(json_dir) if json_dir is not None else default_dir
	out_dir.mkdir(parents=True, exist_ok=True)

	if filename:
		out_path = out_dir / filename
	else:
		ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
		out_path = out_dir / f"crime_matrix_{nx}x{ny}_{ts}.json"

	# Write pretty JSON
	with out_path.open("w", encoding="utf-8") as fh:
		json.dump(obj, fh, indent=2, ensure_ascii=False)

	return out_path


    
    