"""Build-time only, optional: the "live" region, a live-sensor drill at the building where your GB10 is.

Uses that building's OpenStreetMap footprint, saved once from a Nominatim lookup into
data/raw/live/nom.json (the JSON result of a search with polygon_geojson=1 and extratags=1).
There is no disaster here and no imagery: the site is labeled a live drill, and its sensor
is the real WiFi signal of the GB10 (ruview_live.py).
Footprint (c) OpenStreetMap contributors, ODbL.

    python build_live.py
"""
import json
import math
from pathlib import Path

RAW = Path("data/raw/live/nom.json")
OUT = Path("data/regions/live")


def main():
    nom = json.loads(RAW.read_text())[0]
    lat, lon = float(nom["lat"]), float(nom["lon"])
    ring = nom["geojson"]["coordinates"][0]
    kx, ky = 111320 * math.cos(math.radians(lat)), 110540
    xy = [((p[0] - lon) * kx, (p[1] - lat) * ky) for p in ring]
    area = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]))) / 2
    extra = nom.get("extratags") or {}
    levels = extra.get("building:levels")

    OUT.mkdir(parents=True, exist_ok=True)
    site = {
        "id": "B-01", "name": "Building 1 (live drill)", "lat": round(lat, 6), "lon": round(lon, 6),
        "grade": 0, "grade_label": "No disaster (live drill)",
        "building_use": "Live drill", "use_detail": "",
        "kind": f"live drill{f' ({levels} floors)' if levels else ''}, live WiFi sensor",
        "footprint_m2": round(area), "outline": ring, "notation": "OpenStreetMap footprint",
        "det_method": "Live WiFi sensing (RuView RSSI), no damage data", "source": "openstreetmap+live-wifi",
    }
    meta = {
        "region": "Live drill", "aoi": "LIVE", "live": True,
        "event": "Live drill: no disaster, real WiFi sensor near the GB10",
        "source": "OpenStreetMap footprint; live WiFi via RuView",
        "attribution": "Footprint: (c) OpenStreetMap contributors, ODbL",
        "aoi_summary": {"buildings_graded": 0, "by_grade": {}, "method": "No damage grading: live drill"},
        "selection": "The building where the GB10 is", "sites": [site],
    }
    (OUT / "sites.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print(f"live drill: footprint {round(area)} m2, {levels} floors")


if __name__ == "__main__":
    main()
