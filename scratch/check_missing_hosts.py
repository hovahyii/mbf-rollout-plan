import json
import re

content = open('rollout_data.js', encoding='utf-8').read()
data_match = re.search(r'rolloutData = (\[.*?\]);', content, re.S)

if data_match:
    data = json.loads(data_match.group(1))
    site_names = {s['site_name'].upper() for s in data}
    site_ids = {s['enodeb_id'].upper() for s in data if s['enodeb_id'] != '-'}
    
    missing_hosts = {}
    for s in data:
        bbu = s['bbu_location'].upper()
        if bbu != '-' and bbu not in site_names and bbu not in site_ids:
            missing_hosts[bbu] = missing_hosts.get(bbu, 0) + 1
            
    print(f"Total sites: {len(data)}")
    print(f"Unique missing host names: {len(missing_hosts)}")
    
    # Sort by frequency
    sorted_missing = sorted(missing_hosts.items(), key=lambda x: x[1], reverse=True)
    print("Top 10 missing host names (count):")
    for host, count in sorted_missing[:10]:
        print(f"  {host}: {count}")
else:
    print("Could not parse data")
