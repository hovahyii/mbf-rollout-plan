import json
import re

content = open('rollout_data.js', encoding='utf-8').read()
data_match = re.search(r'rolloutData = (\[.*?\]);', content, re.S)
coord_match = re.search(r'coordLookup = (\{.*?\});', content, re.S)

if data_match and coord_match:
    data = json.loads(data_match.group(1))
    coord_lookup = json.loads(coord_match.group(1))
    
    sites_by_name = {s['site_name'].upper(): s for s in data}
    mismatches = []
    
    for s in data:
        bbu = s['bbu_location'].upper()
        if bbu != '-' and bbu in sites_by_name:
            host_site = sites_by_name[bbu]
            lookup_coords = coord_lookup.get(bbu)
            
            if lookup_coords:
                # Check if distance is significant (> 10 meters roughly)
                lat_diff = abs(lookup_coords[0] - host_site['lat'])
                lon_diff = abs(lookup_coords[1] - host_site['lon'])
                
                if lat_diff > 0.0001 or lon_diff > 0.0001:
                    mismatches.append({
                        'remote': s['site_name'],
                        'bbu_host': bbu,
                        'lookup_coords': lookup_coords,
                        'actual_host_coords': [host_site['lat'], host_site['lon']]
                    })
    
    print(f"Total sites: {len(data)}")
    print(f"Total mismatches: {len(mismatches)}")
    if mismatches:
        print("Example mismatches:")
        print(json.dumps(mismatches[:5], indent=2))
else:
    print("Could not parse data or coordLookup")
