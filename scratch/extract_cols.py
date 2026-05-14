import pandas as pd
import json

df = pd.read_excel(r'E:\MBF Rollout Dashboard\60086951_56A0US7_20260515002605.xlsm', sheet_name='Site Rollout Plan', header=None, nrows=3)

headers = df.values.tolist()
# headers[0] is level 0
# headers[1] is level 1 (sub-headers)
# headers[2] is level 2 (detail-headers)

col_info = {}

for i in range(len(headers[0])):
    h0 = str(headers[0][i]) if not pd.isna(headers[0][i]) else ""
    h1 = str(headers[1][i]) if not pd.isna(headers[1][i]) else ""
    h2 = str(headers[2][i]) if not pd.isna(headers[2][i]) else ""
    col_info[i] = [h0, h1, h2]

with open('col_info.json', 'w', encoding='utf-8') as f:
    json.dump(col_info, f, ensure_ascii=False, indent=2)
