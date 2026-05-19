import pandas as pd

tracker_file = r'E:\MBF Rollout Dashboard\On Air Progress Tracker.xlsx'
wb = pd.ExcelFile(tracker_file)

for sheet in wb.sheet_names:
    df = pd.read_excel(tracker_file, sheet_name=sheet, header=1) # Row 2 header
    
    if 'Site Name' in df.columns:
        site_names = df['Site Name'].dropna().astype(str).tolist()
        chi_dong_sites = [s for s in site_names if 'CHI_DONG' in s.upper()]
        if chi_dong_sites:
            print(f"Sheet {sheet} has CHI_DONG: {chi_dong_sites}")
    else:
        # maybe header was row 1
        df = pd.read_excel(tracker_file, sheet_name=sheet, header=0)
        if 'Site Name' in df.columns:
            site_names = df['Site Name'].dropna().astype(str).tolist()
            chi_dong_sites = [s for s in site_names if 'CHI_DONG' in s.upper()]
            if chi_dong_sites:
                print(f"Sheet {sheet} has CHI_DONG: {chi_dong_sites}")
