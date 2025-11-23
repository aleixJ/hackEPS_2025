"""Utilities to compute aggregated city statistics across parcel grids.

This module drives the JSON generation for all city-level statistics
modules (crime, mobility, education). Run as a script to generate and
save the crime-like JSON outputs for each dataset.
"""

from typing import Dict
from crime_stats import save_crime_matrix_json
from mobility_stats import mobility_crimelike_json, save_mobility_crimelike_json
from education_stats import education_crimelike_json, save_education_crimelike_json


# Define LA bounding box locally so this module is self-contained.
# These values mirror the defaults previously used in `crime_stats.py`.
BOUND_W = -118.6057  # West Longitude
BOUND_E = -118.1236  # East Longitude
BOUND_N = 34.3344    # North Latitude
BOUND_S = 33.8624    # South Latitude


def generate_all_json(nx: int = 20, ny: int = 20) -> Dict[str, str]:
    """Generate and save JSON files for crime, mobility, and education.

    Returns a dict mapping dataset name to saved file path.
    """
    results: Dict[str, str] = {}

    # 1) Crime: use existing crime_stats saver
    crime_path = save_crime_matrix_json(nx=nx, ny=ny, max_records_per_parcel=10000)
    results["crime"] = str(crime_path)

    # 2) Mobility: build crime-like normalized JSON and save
    mob_data = mobility_crimelike_json(nx, ny)
    mob_path = save_mobility_crimelike_json(mob_data)
    results["mobility"] = mob_path

    # 3) Education: build crime-like normalized JSON and save
    edu_data = education_crimelike_json(nx, ny)
    edu_path = save_education_crimelike_json(edu_data)
    results["education"] = edu_path

    return results


if __name__ == "__main__":
    cols = 20
    rows = 20
    saved = generate_all_json(nx=cols, ny=rows)
    for k, v in saved.items():
        print(f"Saved {k} JSON to: {v}")
