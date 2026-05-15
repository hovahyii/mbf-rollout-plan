import json
import re

content = open('rollout_data.js', encoding='utf-8').read()
data_match = re.search(r'rolloutData = (\[.*?\]);', content, re.S)
if data_match:
    data = json.loads(data_match.group(1))
    cran = [s for s in data if s['bbu_location'] != '-']
    if cran:
        print(json.dumps(cran[0], indent=2))
    else:
        print("No CRAN sites found in data")
else:
    print("Could not parse rolloutData")
