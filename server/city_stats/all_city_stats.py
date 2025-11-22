"""Utilities to compute aggregated city statistics across parcel grids.

This module provides functions to divide the LA bounding box into an
`nx` by `ny` grid of parcels, count crimes that occurred in each parcel
during the last year using `get_paginated_crimes` from `crime_stats.py`,
and return the results in a JSON-serializable format.
"""

from crime_stats import save_crime_matrix_json



# Define LA bounding box locally so this module is self-contained.
# These values mirror the defaults previously used in `crime_stats.py`.
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude



if __name__ == "__main__":
    
    cols = 20
    rows = 20
    
    # Call the function to save the crime matrix JSON
    save_crime_matrix_json(nx=cols, ny=rows, max_records_per_parcel=10)
    
 
    
