"""Utilities to compute aggregated city statistics across parcel grids.

This module provides a function to divide the LA bounding box (from
`crime_stats.py`) into an `nx` by `ny` grid of parcels and count the number
of crimes that occurred in each parcel during the last year using
`get_paginated_crimes` from `crime_stats.py`.

Note: This implementation calls the API once per parcel via
`get_paginated_crimes`. For large grids this results in many API calls.
"""
from typing import List, Dict, Any

# Try several import paths so this file can be executed either as a
# package module or directly as a script from the same directory.
try:
	from .crime_stats import get_paginated_crimes
except Exception:
	try:
		# When running from the repository root using module path
		from server.city_stats.crime_stats import get_paginated_crimes
	except Exception:
		# When running directly from the `city_stats` folder
		from crime_stats import get_paginated_crimes

# Define LA bounding box locally so this module is self-contained.
# These values mirror the defaults previously used in `crime_stats.py`.
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude


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

	# iterate columns (x) then rows (y). j runs south->north
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


if __name__ == "__main__":
	# Simple demo: divide into a small grid and print summary counts.
	import pprint

	nx_demo = 10
	ny_demo = 10
	print(f"Computing crime counts for a {nx_demo}x{ny_demo} grid...")
	parcels = crime_counts_by_parcels(nx_demo, ny_demo, max_records_per_parcel=1000)

	total = sum(p["count"] for p in parcels)
	print(f"Total crimes fetched across parcels: {total}")

	# Print a compact grid view (rows = ny from north to south)
	grid = [[0 for _ in range(nx_demo)] for _ in range(ny_demo)]
	for p in parcels:
		grid[p["j"]][p["i"]] = p["count"]

	print("Counts grid (rows: south->north, cols: west->east):")
	pprint.pprint(grid)
