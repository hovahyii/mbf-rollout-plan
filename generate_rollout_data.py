import pandas as pd
import json
import os
import glob
import shapefile

def find_col(df, keywords):
    for col in df.columns:
        if any(k.lower() in str(col).lower() for k in keywords):
            return col
    return None

def clean_val(val):
    if pd.isna(val) or str(val).lower().strip() in ['nan', 'none', 'null', '', 'nat']:
        return "-"
    return str(val).strip()

def get_geojson_from_shp(shp_folder):
    try:
        # Find the .shp file in the folder
        shp_files = glob.glob(os.path.join(shp_folder, "*.shp"))
        if not shp_files: return None
        shp_path = shp_files[0]
        
        sf = shapefile.Reader(shp_path)
        fields = [f[0] for f in sf.fields[1:]]
        features = []
        for sr in sf.shapeRecords():
            if sr.shape.shapeType == 0: continue
            geom = sr.shape.__geo_interface__
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": dict(zip(fields, sr.record))
            })
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        print(f"Error reading shapefile in {shp_folder}: {e}")
        return None

def get_on_air_info(tracker_path):
    on_air_info = {} # site_name -> rat
    try:
        xl = pd.ExcelFile(tracker_path)
        for s in xl.sheet_names:
            if 'Summary' in s: continue
            df = pd.read_excel(tracker_path, sheet_name=s, header=None)
            # Find which row is the header (contains "Site Name")
            header_idx = -1
            for r in range(min(5, len(df))):
                row_vals = [str(x).strip() for x in df.iloc[r].tolist()]
                if 'Site Name' in row_vals:
                    header_idx = r
                    break
            
            if header_idx == -1: continue
            
            header = [str(x).strip() for x in df.iloc[header_idx].tolist()]
            name_col = header.index('Site Name')
            
            # 4G Day is always 3 columns after Site Name
            # 5G Day is always 6 columns after Site Name
            for idx, row in df.iloc[header_idx+1:].iterrows():
                site_name = str(row[name_col]).strip()
                if not site_name or site_name == 'nan' or site_name == 'None': continue
                
                # Check if it's on-air for 4G or 5G
                try:
                    is_4g_on_air = not pd.isna(row[name_col + 3])
                    is_5g_on_air = not pd.isna(row[name_col + 6])
                except: continue
                
                rat = []
                if is_4g_on_air: rat.append("4G")
                if is_5g_on_air: rat.append("5G")
                
                if rat:
                    on_air_info[site_name] = "+".join(rat)
    except Exception as e:
        print(f"Error reading {tracker_path}: {e}")
    return on_air_info

def get_rollout_details(file_path):
    details = {} # site_id -> {rfi, on_air, bbu, type}
    try:
        print(f"Loading rollout details from {file_path}...")
        df = pd.read_excel(file_path, sheet_name='Site Rollout Plan', skiprows=2)
        
        # 108: Main Site Name (BBU Location)
        # 158: Site Type (IBC/Macro/CRAN)
        # 99: Lat, 106: Lon
        
        # Possible On-Air columns (Actual End Date)
        on_air_cols = [283, 326, 244, 253, 258, 131] 
        # Possible RFI columns (Actual End Date)
        rfi_cols = [321]
        
        for idx, row in df.iterrows():
            try:
                # Use both Column 0 and Column 1 as possible site names
                site_id = clean_val(row.iloc[0]).upper()
                site_name_alt = clean_val(row.iloc[1]).upper()
                
                if site_id == '-': continue
                
                bbu = clean_val(row.iloc[108]).upper()
                stype = clean_val(row.iloc[158])
                
                # Extract coordinates from Rollout Plan
                rl_lat, rl_lon = None, None
                try:
                    rl_lat = float(str(row.iloc[99]).replace(',', '.'))
                    rl_lon = float(str(row.iloc[106]).replace(',', '.'))
                except: pass

                # Check multiple columns for the most advanced status
                on_air = "-"
                for c in on_air_cols:
                    val = clean_val(row.iloc[c])
                    if val != "-":
                        on_air = val
                        break
                
                rfi = "-"
                for c in rfi_cols:
                    val = clean_val(row.iloc[c])
                    if val != "-":
                        rfi = val
                        break
                
                entry = {
                    'rfi_date': rfi, 'on_air_date': on_air,
                    'bbu_location': bbu if bbu != site_id and bbu != site_name_alt else "-",
                    'detailed_type': stype, 'lat': rl_lat, 'lon': rl_lon
                }
                details[site_id] = entry
                if site_name_alt != '-': details[site_name_alt] = entry
                
            except: continue
        print(f"Loaded {len(details)} site details.")
    except Exception as e:
        print(f"Error reading rollout details: {e}")
    return details

def generate_data():
    base_dir = r'E:\MBF Rollout Dashboard'
    
    # New source file
    rollout_file = os.path.join(base_dir, '60086951_56A0US7_20260515002605.xlsm')
    rollout_details = get_rollout_details(rollout_file) if os.path.exists(rollout_file) else {}

    on_air_path = os.path.join(base_dir, 'On Air Progress Tracker.xlsx')
    on_air_info = get_on_air_info(on_air_path)
    
    file_pattern = os.path.join(base_dir, 'MBF RAN Project - Phase 1 PO - Master Site List - *.xlsx')
    
    files = glob.glob(file_pattern)
    if not files:
        print("No master file found.")
        return
    latest_file = sorted(files)[-1]
    print(f"Reading {latest_file}...")
    
    sheets = {'North_Site': 'North', 'Middle_Site': 'Middle', 'South_Site': 'South'}
    all_sites = []
    
    for sheet_name, region_name in sheets.items():
        print(f"Processing {sheet_name}...")
        df = pd.read_excel(latest_file, sheet_name=sheet_name, skiprows=3)
        
        col_map = {
            'po': find_col(df, ['PO']),
            'site_name': find_col(df, ['Physical Site Name', 'Main Site Name']),
            'province': find_col(df, ['Province', 'New Province']),
            'district': find_col(df, ['District']),
            'enodeb_id': find_col(df, ['Existing eNodeB ID', 'eNodeB ID']),
            'lat': find_col(df, ['Lat']),
            'lon': find_col(df, ['Long', 'Lon']),
            'vip': find_col(df, ['VIP Site']),
            'scenario': find_col(df, ['Scenario']),
            'site_type': find_col(df, ['Physical Site Type']),
            'timeline_north': find_col(df, ['Delivery plan W']),
            'timeline_other': find_col(df, ['Delivery Week', 'swap week']),
            'rf_approved': find_col(df, ['RF Approved']),
            'cdd_approved': find_col(df, ['CDD Approved']),
            'lock_date': find_col(df, ['Site configure Lock Date']),
            '4g_type': find_col(df, ['4G Type']),
            '5g_scenario': find_col(df, ['5G Scenario']),
        }

        for idx, row in df.iterrows():
            try:
                lat_val, lon_val = row.get(col_map['lat']), row.get(col_map['lon'])
                if pd.isna(lat_val) or pd.isna(lon_val): continue
                lat = float(str(lat_val).replace(',', '.'))
                lon = float(str(lon_val).replace(',', '.'))
                if not (8.0 < lat < 24.0 and 102.0 < lon < 110.0): continue
            except: continue
            
            site_name_raw = clean_val(row.get(col_map['site_name']))
            site_name_upper = site_name_raw.upper()
            
            # Enrich with rollout details
            site_detail = rollout_details.get(site_name_upper, {})
            rfi_date = site_detail.get('rfi_date', "-")
            on_air_date = site_detail.get('on_air_date', "-")
            bbu_location = site_detail.get('bbu_location', "-")
            detailed_type = site_detail.get('detailed_type', "-")

            # Determine status
            if on_air_date != "-" or site_name_upper in [k.upper() for k in on_air_info.keys()]:
                status = "On-Air"
            elif rfi_date != "-":
                status = "RFI Ready"
            else:
                status = "Pending"
                
            rat_list = []
            if clean_val(row.get(col_map['4g_type'])) != "-": rat_list.append("4G")
            if clean_val(row.get(col_map['5g_scenario'])) != "-": rat_list.append("5G")
            rat_val = "+".join(rat_list) if rat_list else "-"
            
            vip_val = clean_val(row.get(col_map['vip'])).upper()
            if vip_val == "-": vip_val = "NO"
            is_vip = vip_val in ['SVIP', 'VVIP', 'VIP']
            
            enodeb_raw = row.get(col_map['enodeb_id'])
            enodeb_id = str(enodeb_raw).strip() if not pd.isna(enodeb_raw) else "-"
            if enodeb_id.endswith('.0'): enodeb_id = enodeb_id[:-2]
                
            final_region = region_name
            province_val = clean_val(row.get(col_map['province']))
            if final_region == 'North' and province_val.lower() in ['ha noi', 'hanoi']:
                final_region = 'Ha Noi'
                
            site = {
                'region': final_region, 'po': clean_val(row.get(col_map['po'])),
                'site_name': site_name_raw,
                'province': province_val,
                'district': clean_val(row.get(col_map['district'])),
                'enodeb_id': enodeb_id, 'lat': lat, 'lon': lon,
                'vip': vip_val, 'is_vip': is_vip, 'scenario': clean_val(row.get(col_map['scenario'])),
                'site_type': clean_val(row.get(col_map['site_type'])), 
                'detailed_type': detailed_type,
                'status': status, 'rat': rat_val,
                'rfi_date': rfi_date, 'on_air_date': on_air_date,
                'bbu_location': bbu_location
            }
            site['timeline'] = clean_val(row.get(col_map[f"timeline_{'north' if region_name=='North' else 'other'}"]))
            all_sites.append(site)

    # Create a global coordinate lookup for all sites (from master and rollout)
    coord_lookup = {}
    for s in all_sites:
        coord_lookup[s['site_name'].upper()] = [s['lat'], s['lon']]
        if s['enodeb_id'] != '-': coord_lookup[s['enodeb_id'].upper()] = [s['lat'], s['lon']]
    
    for sid, d in rollout_details.items():
        if d['lat'] and d['lon']:
            # Prioritize rollout plan coordinates if available for the site name
            coord_lookup[sid.upper()] = [d['lat'], d['lon']]

    # Load official Polygons from specific paths
    polygons = {"North": None, "Middle": None, "South": None}
    
    paths = {
        'North': os.path.join(base_dir, 'North Region', 'Hanoi Swap Cluster Polygon for simulation-0423'),
        'Middle': os.path.join(base_dir, 'Middle Region', 'Middle Cluster Polygon_01042026'),
        'South': os.path.join(base_dir, 'South Region', 'South Region Cluster_0410', '20260410')
    }
    
    for region, path in paths.items():
        if os.path.exists(path):
            polygons[region] = get_geojson_from_shp(path)
            if polygons[region]: print(f"Loaded official polygons for {region}")
    
    output_path = os.path.join(base_dir, 'rollout_data.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("const rolloutData = ")
        json.dump(all_sites, f, ensure_ascii=False, indent=2)
        f.write(";\nconst coordLookup = ")
        json.dump(coord_lookup, f, ensure_ascii=False, indent=2)
        f.write(";\nconst polygonData = ")
        json.dump(polygons, f, ensure_ascii=False, indent=2)
        f.write(";")
    print(f"Data saved to {output_path} ({len(all_sites)} sites, {len(coord_lookup)} coords)")

if __name__ == "__main__":
    generate_data()
