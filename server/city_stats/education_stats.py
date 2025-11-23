"""Education statistics using OpenStreetMap (Overpass API).

This module mirrors `mobility_stats.py` but counts education-related
features (schools, colleges, universities, kindergartens, libraries).

It batch-fetches all relevant OSM elements for the LA bounding box,
assigns elements to tiles, builds per-category matrices and a combined
TotalMatrix, applies min-max normalization and can save a crime-like
JSON file compatible with the format used elsewhere in the project.
"""

from typing import Any, Dict, List, Optional, Tuple
import time
import json
import os
import requests

# same LA bounding box used elsewhere
BOUND_W = -118.6057
BOUND_E = -118.1236
BOUND_N = 34.3344
BOUND_S = 33.8624

DEFAULT_OVERPASS = "https://overpass-api.de/api/interpreter"

# Education-related tags to match
CATEGORY_TAGS = {
    "school": [("amenity", "school")],
    "college": [("amenity", "college")],
    "university": [("amenity", "university")],
    "kindergarten": [("amenity", "kindergarten")],
    "library": [("amenity", "library")],
}


def _build_overpass_query(bbox: Tuple[float, float, float, float]) -> str:
    south, west, north, east = bbox
    parts: List[str] = []
    for tags in CATEGORY_TAGS.values():
        for k, v in tags:
            parts.append(f'node["{k}"="{v}"]({south},{west},{north},{east});')
            parts.append(f'way["{k}"="{v}"]({south},{west},{north},{east});')
            parts.append(f'relation["{k}"="{v}"]({south},{west},{north},{east});')
    joined = "\n".join(parts)
    return f"[out:json][timeout:25];\n(\n{joined}\n);\nout center;"


def _fetch_overpass(bbox: Tuple[float, float, float, float], overpass_url: str = DEFAULT_OVERPASS) -> List[Dict[str, Any]]:
    q = _build_overpass_query(bbox)
    try:
        resp = requests.post(overpass_url, data={"data": q}, timeout=60)
        resp.raise_for_status()
        return resp.json().get("elements", [])
    except Exception:
        return []


def _classify_element(tags: Dict[str, str]) -> Optional[str]:
    if not tags:
        return None
    for cat, taglist in CATEGORY_TAGS.items():
        for k, v in taglist:
            if tags.get(k) == v:
                return cat
    return None


def education_counts_by_parcels(nx: int, ny: int, *, overpass_url: str = DEFAULT_OVERPASS) -> List[Dict[str, Any]]:
    """Batch-fetch LA elements and assign to nx x ny tiles; return parcels."""
    if nx <= 0 or ny <= 0:
        raise ValueError("nx and ny must be positive integers")

    lon_step = (BOUND_E - BOUND_W) / float(nx)
    lat_step = (BOUND_N - BOUND_S) / float(ny)

    elements = _fetch_overpass((BOUND_S, BOUND_W, BOUND_N, BOUND_E), overpass_url=overpass_url)

    tile_counts: List[List[Dict[str, int]]] = [[{k: 0 for k in CATEGORY_TAGS} for _ in range(nx)] for _ in range(ny)]
    tile_totals: List[List[int]] = [[0 for _ in range(nx)] for _ in range(ny)]

    def _get_latlon(el: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        if "lat" in el and "lon" in el:
            return float(el["lat"]), float(el["lon"])
        c = el.get("center")
        if isinstance(c, dict) and "lat" in c and "lon" in c:
            return float(c["lat"]), float(c["lon"])
        return None

    for el in elements:
        latlon = _get_latlon(el)
        if not latlon:
            continue
        lat, lon = latlon
        i = int((lon - BOUND_W) / lon_step)
        j = int((lat - BOUND_S) / lat_step)
        i = max(0, min(nx - 1, i))
        j = max(0, min(ny - 1, j))
        cat = _classify_element(el.get("tags", {}))
        if cat:
            tile_counts[j][i][cat] += 1
            tile_totals[j][i] += 1

    parcels: List[Dict[str, Any]] = []
    for i in range(nx):
        w = BOUND_W + i * lon_step
        e = w + lon_step
        for j in range(ny):
            s = BOUND_S + j * lat_step
            n = s + lat_step
            parcels.append({
                "i": i,
                "j": j,
                "bounds": {"W": w, "E": e, "N": n, "S": s},
                "center": {"lon": (w + e) / 2.0, "lat": (s + n) / 2.0},
                "counts": tile_counts[j][i],
                "total": tile_totals[j][i],
            })

    return parcels


def education_matrix_json(nx: int, ny: int, *, overpass_url: str = DEFAULT_OVERPASS) -> Dict[str, Any]:
    parcels = education_counts_by_parcels(nx, ny, overpass_url=overpass_url)
    category_matrices = {k: [[0 for _ in range(nx)] for _ in range(ny)] for k in CATEGORY_TAGS}
    total_matrix = [[0 for _ in range(nx)] for _ in range(ny)]
    for p in parcels:
        i = int(p["i"])
        j = int(p["j"])  # south-based
        row = (ny - 1) - j
        for cat, val in p["counts"].items():
            category_matrices[cat][row][i] = val
            total_matrix[row][i] += val

    return {
        "Aspect": "Education",
        "CategoryMatrices": category_matrices,
        "TotalMatrix": total_matrix,
        "Norigin": BOUND_N,
        "WOrigin": BOUND_W,
        "VerticalStep": (BOUND_N - BOUND_S) / float(ny),
        "HorizontalStep": (BOUND_E - BOUND_W) / float(nx),
        "generated_at": int(time.time()),
    }


def normalize_matrix_minmax(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix or not matrix[0]:
        return matrix
    min_v = None
    max_v = None
    for row in matrix:
        for v in row:
            fv = float(v) if v is not None else 0.0
            if min_v is None or fv < min_v:
                min_v = fv
            if max_v is None or fv > max_v:
                max_v = fv
    if min_v is None or max_v is None or max_v == min_v:
        return [[0.0 for _ in row] for row in matrix]
    denom = float(max_v - min_v)
    return [[(float(v) - min_v) / denom for v in row] for row in matrix]


def education_crimelike_json(nx: int, ny: int, *, overpass_url: str = DEFAULT_OVERPASS) -> List[Dict[str, Any]]:
    obj = education_matrix_json(nx, ny, overpass_url=overpass_url)
    total = obj.get("TotalMatrix", [])
    normalized = normalize_matrix_minmax(total)
    return [
        {
            "Aspect": "Education",
            "CrimeMatrix": normalized,
            "Norigin": obj.get("Norigin", BOUND_N),
            "WOrigin": obj.get("WOrigin", BOUND_W),
            "VerticalStep": obj.get("VerticalStep"),
            "HorizontalStep": obj.get("HorizontalStep"),
        }
    ]


def save_education_crimelike_json(data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    base_dir = os.path.join(os.path.dirname(__file__), "jsons")
    os.makedirs(base_dir, exist_ok=True)
    if not filename:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        filename = f"education_matrix_{stamp}.json"
    path = os.path.join(base_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    return path


def save_education_matrix_json(obj: Dict[str, Any], filename: Optional[str] = None) -> str:
    base_dir = os.path.join(os.path.dirname(__file__), "jsons")
    os.makedirs(base_dir, exist_ok=True)
    if not filename:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        filename = f"education_matrix_{stamp}.json"
    path = os.path.join(base_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    return path


if __name__ == "__main__":
    # default CLI: generate and save a 20x20 education crime-like JSON
    nx = 20
    ny = 20
    data = education_crimelike_json(nx, ny)
    out = save_education_crimelike_json(data)
    print(f"Saved education crime-like JSON to: {out}")
