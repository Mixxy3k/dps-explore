"""
Geocode all unique locations from KRDO dataset using Nominatim (OpenStreetMap).
Saves coordinates to a JSON file for use in the explorer page.
"""
import csv
import json
import time
import requests
from urllib.parse import quote

CSV_FILE = "krdo_dps_poland.csv"
OUTPUT_FILE = "locations_geo.json"

HEADERS = {
    "User-Agent": "KRDO-Explorer/1.0 (for personal use; helping grandma find care homes)"
}

def load_locations():
    """Extract unique location strings from the CSV."""
    locs = {}
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc = row["lokalizacja"].strip()
            if loc:
                # Also extract city from address for better geocoding
                addr = row["adres"].replace("\n", " ").replace("\t", " ").strip()
                if loc not in locs:
                    locs[loc] = {"addresses": set(), "rows": []}
                # Get just the city from address (last part after postcode)
                parts = [p.strip() for p in addr.split(",")]
                city = parts[-1] if parts else ""
                locs[loc]["addresses"].add(city)
                locs[loc]["rows"].append(row)
    return locs

def geocode_location(loc_name, sample_cities):
    """Geocode a location using Nominatim API."""
    # Try different query strategies
    queries = []
    
    # Strategy 1: If it starts with "Powiat", search for the powiat
    if loc_name.lower().startswith("powiat"):
        powiat_name = loc_name[len("Powiat "):].strip()
        queries.append(f"{powiat_name}, Polska")
    
    # Strategy 2: If it's a city name (no "Powiat"), search for the city
    if not loc_name.lower().startswith("powiat"):
        queries.append(f"{loc_name}, Polska")
    
    # Strategy 3: Use a sample city from the addresses
    for city in sample_cities:
        if city and not any(kw in city.lower() for kw in ["ul.", "ulica", "www", "@"]):
            queries.append(f"{city}, Polska")
            break
    else:
        # Strategy 4: Search for the powiat name even without "Powiat" prefix
        queries.append(f"{loc_name}, Polska")
    
    for query in queries[:3]:  # Try up to 3 queries
        url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1&accept-language=pl"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display_name": data[0]["display_name"],
                    "query": query,
                }
        except Exception as e:
            print(f"  Error geocoding '{query}': {e}")
    
    return None

def main():
    print("Loading locations from CSV...")
    locs = load_locations()
    print(f"Found {len(locs)} unique locations")
    
    # Load existing cache if any
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached coordinates")
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {}
    
    results = dict(cache)  # Keep existing results
    
    new_geocoded = 0
    skipped = 0
    
    for i, (loc_name, data) in enumerate(locs.items()):
        if loc_name in results:
            skipped += 1
            continue
        
        print(f"[{i+1}/{len(locs)}] Geocoding: {loc_name}")
        sample_cities = list(data["addresses"])[:3]
        result = geocode_location(loc_name, sample_cities)
        
        if result:
            results[loc_name] = result
            new_geocoded += 1
            print(f"  ✓ {result['lat']:.4f}, {result['lon']:.4f} ({result['display_name'][:60]})")
        else:
            results[loc_name] = None
            print(f"  ✗ Not found")
        
        # Be nice to Nominatim - 1 request per second
        time.sleep(1.1)
        
        # Save periodically
        if (i + 1) % 20 == 0:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  [Saved {len(results)} locations to {OUTPUT_FILE}]")
    
    # Final save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    successful = sum(1 for v in results.values() if v is not None)
    failed = sum(1 for v in results.values() if v is None)
    print(f"\n=== Done ===")
    print(f"Total unique locations: {len(locs)}")
    print(f"Geocoded (new): {new_geocoded}")
    print(f"Skipped (cached): {skipped}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
