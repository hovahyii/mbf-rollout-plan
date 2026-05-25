import sys
sys.path.append('E:\\MBF Rollout Dashboard')
import generate_rollout_data as grd
import pandas as pd

path = 'E:\\MBF Rollout Dashboard\\MBF RAN Project - Phase 1 PO - Master Site List.xlsx'
df = pd.read_excel(path, sheet_name='South_Site', skiprows=3)
col = grd.find_col(df, ['Physcial Site Name', 'Physical Site Name'])

# Look for TGGD53
row = df[df[col] == 'TGGD53'].iloc[0]
with open('E:\\MBF Rollout Dashboard\\scratch\\south_site_cols.txt', 'w', encoding='utf-8') as f:
    for c in df.columns:
        val = row.get(c)
        if not pd.isna(val) and val != '':
            try:
                f.write(f"{c}: {val}\n")
            except:
                pass
