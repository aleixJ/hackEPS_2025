"""Utilities to compute aggregated city statistics across parcel grids.

This module provides functions to divide the LA bounding box into an
`nx` by `ny` grid of parcels, count crimes that occurred in each parcel
during the last year using `get_paginated_crimes` from `crime_stats.py`,
and return the results in a JSON-serializable format.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Try several import paths so this file can be executed either as a
"""Utilities to compute aggregated city statistics across parcel grids.

This module provides functions to divide the LA bounding box into an
`nx` by `ny` grid of parcels, count crimes that occurred in each parcel
during the last year using `get_paginated_crimes` from `crime_stats.py`,
and return the results in a JSON-serializable format.
"""

import json
from typing import List, Dict, Any

# Try several import paths so this file can be executed either as a
"""Utilities to compute aggregated city statistics across parcel grids.

This module provides functions to divide the LA bounding box into an
`nx` by `ny` grid of parcels, count crimes that occurred in each parcel
during the last year using `get_paginated_crimes` from `crime_stats.py`,
and return the results in a JSON-serializable format.
"""

import json
from typing import List, Dict, Any


# Try several import paths so this file can be executed either as a
# package module or directly as a script from the same directory.
try:
	from .crime_stats import get_paginated_crimes
except Exception:
	try:
		from server.city_stats.crime_stats import get_paginated_crimes
	except Exception:
		try:
			from crime_stats import get_paginated_crimes
		except Exception:
			get_paginated_crimes = None


# If the dynamic import failed, provide a stub so the module still
# compiles; attempting to call the stub will raise a clear ImportError.
if get_paginated_crimes is None:
	def get_paginated_crimes(*args, **kwargs):
		raise ImportError("get_paginated_crimes import failed; ensure crime_stats.py is importable")


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
		row = (ny - 1) - p["j"]
		col = p["i"]
		matrix[row][col] = p["count"]

	lon_span = BOUND_E - BOUND_W
	lat_span = BOUND_N - BOUND_S

	horizontal_step = lon_span / nx
	vertical_step = lat_span / ny

	obj = [
		{
			"Aspect": "Crime",
			"CrimeMatrix": matrix,
			"Norigin": BOUND_N,
			"WOrigin": BOUND_W,
			"VerticalStep": vertical_step,
			"HorizontalStep": horizontal_step,
		}
	]

	if as_json:
		return json.dumps(obj)
	return obj


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


if __name__ == "__main__":
    #(nx=5, ny=5, max_records_per_parcel=10, as_json=True)
    save_crime_matrix_json(nx=4, ny=4, max_records_per_parcel=10)
    
 
    
