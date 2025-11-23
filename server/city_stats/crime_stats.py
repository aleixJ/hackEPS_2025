import requests
import json
import time
from datetime import datetime, timedelta

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

    
    
    