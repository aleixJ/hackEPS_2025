import requests
import json
from datetime import datetime

# --- Configuration ---
# Bounding Box (South, West, North, East)
BBOX = (33.8624, -118.6057, 34.3344, -118.1236)
BOUND_S, BOUND_W, BOUND_N, BOUND_E = BBOX

overpass_url = "http://overpass-api.de/api/interpreter"

# --- Overpass Query for Wheelchair Accessible Places ---
wheelchair_query = f"""
[out:json][timeout:60];
(
  // --- WHEELCHAIR ACCESSIBLE AMENITIES ---
  nwr["wheelchair"="yes"]{BBOX};
  
  // --- SPECIFIC WHEELCHAIR ACCESSIBLE PLACES ---
  nwr["amenity"="hospital"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="pharmacy"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="library"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="restaurant"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="cafe"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="parking"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="toilets"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="public_building"]["wheelchair"="yes"]{BBOX};
  nwr["amenity"="community_centre"]["wheelchair"="yes"]{BBOX};
  nwr["leisure"="park"]["wheelchair"="yes"]{BBOX};
  nwr["leisure"="playground"]["wheelchair"="yes"]{BBOX};
  nwr["shop"]["wheelchair"="yes"]{BBOX};
);
out body;
>;
out skel qt;
"""


def classify_wheelchair_place(tags):
    """Classify a wheelchair accessible place by its type."""
    
    # Hospitals & Medical
    if tags.get('amenity') == 'hospital': return 'Hospital'
    if tags.get('amenity') == 'pharmacy': return 'Pharmacy'
    if tags.get('amenity') == 'clinic': return 'Clinic'
    
    # Dining & Food
    if tags.get('amenity') == 'restaurant': return 'Restaurant'
    if tags.get('amenity') == 'cafe': return 'Cafe'
    if tags.get('amenity') == 'bar': return 'Bar'
    
    # Public Services
    if tags.get('amenity') == 'library': return 'Library'
    if tags.get('amenity') == 'community_centre': return 'Community Center'
    if tags.get('amenity') == 'public_building': return 'Public Building'
    if tags.get('amenity') == 'toilets': return 'Accessible Restrooms'
    
    # Shopping
    if tags.get('shop'): return 'Shop'
    
    # Recreation
    if tags.get('leisure') == 'park': return 'Accessible Park'
    if tags.get('leisure') == 'playground': return 'Accessible Playground'
    
    # Parking & Transport
    if tags.get('amenity') == 'parking': return 'Accessible Parking'
    if tags.get('public_transport'): return 'Public Transport'
    
    # Generic wheelchair accessible
    if tags.get('wheelchair') == 'yes': return 'Wheelchair Accessible Place'
    
    return 'Other'


def fetch_wheelchair_accessible_places():
    """
    Fetch all wheelchair accessible places from OpenStreetMap
    and display results in PowerShell
    """
    print("="*70)
    print("🦽 WHEELCHAIR ACCESSIBLE PLACES IN LA COUNTY")
    print("="*70)
    print(f"\n🔍 Querying OpenStreetMap for wheelchair accessible places...")
    print(f"   Bounding Box: {BBOX}\n")
    
    try:
        response = requests.get(overpass_url, params={'data': wheelchair_query}, timeout=60)
        response.raise_for_status()
        data = response.json()
        elements = data.get('elements', [])
        
        print(f"✅ Found {len(elements)} elements from OSM\n")
        
        # Classify and count elements
        place_stats = {}
        places_list = []
        
        for element in elements:
            tags = element.get('tags', {})
            
            # Skip elements without tags
            if not tags:
                continue
            
            # Skip if not explicitly wheelchair accessible
            if tags.get('wheelchair') != 'yes':
                continue
            
            category = classify_wheelchair_place(tags)
            place_stats[category] = place_stats.get(category, 0) + 1
            
            # Extract location info
            lat = element.get('lat')
            lon = element.get('lon')
            
            # If element is a way/relation, try to get center
            if lat is None and 'center' in element:
                lat = element['center'].get('lat')
                lon = element['center'].get('lon')
            
            place_info = {
                'name': tags.get('name', 'Unknown'),
                'type': category,
                'lat': lat,
                'lon': lon,
                'address': tags.get('addr:street', ''),
                'phone': tags.get('phone', ''),
                'website': tags.get('website', ''),
            }
            places_list.append(place_info)
        
        # --- Display Statistics ---
        print("📊 WHEELCHAIR ACCESSIBLE PLACES BY TYPE")
        print("="*70)
        
        if place_stats:
            for place_type in sorted(place_stats.keys()):
                count = place_stats[place_type]
                print(f"  {place_type}: {count}")
            
            total = sum(place_stats.values())
            print(f"\n  TOTAL: {total} wheelchair accessible places found\n")
        else:
            print("❌ No wheelchair accessible places found\n")
        
        # --- Display Detailed List ---
        print("\n📍 DETAILED LIST OF ACCESSIBLE PLACES")
        print("="*70)
        
        for idx, place in enumerate(places_list[:50], 1):  # Show first 50
            print(f"\n{idx}. {place['name']}")
            print(f"   Type: {place['type']}")
            if place['address']:
                print(f"   Address: {place['address']}")
            if place['lat'] and place['lon']:
                print(f"   Location: ({place['lat']:.4f}, {place['lon']:.4f})")
            if place['phone']:
                print(f"   Phone: {place['phone']}")
            if place['website']:
                print(f"   Website: {place['website']}")
        
        if len(places_list) > 50:
            print(f"\n... and {len(places_list) - 50} more places")
        
        # --- Save to JSON ---
        output_file = "la_wheelchair_accessible.json"
        output_data = {
            "Aspect": "Wheelchair Accessibility",
            "TotalPlaces": len(places_list),
            "Statistics": place_stats,
            "Places": places_list,
            "BoundingBox": {
                "North": BOUND_N,
                "South": BOUND_S,
                "East": BOUND_E,
                "West": BOUND_W
            },
            "Timestamp": datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n\n✅ Data saved to: {output_file}")
        print("="*70)
        
        return places_list
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout: Overpass API took too long to respond")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fetch_wheelchair_accessible_places()