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

def get_on_air_sites(tracker_path):
    on_air_sites = set()
    try:
        xl = pd.ExcelFile(tracker_path)
        for s in xl.sheet_names:
            if 'Summary' in s: continue
            df = pd.read_excel(tracker_path, sheet_name=s, header=1)
            if 'Site Name' in df.columns:
                sites = df['Site Name'].dropna().unique().tolist()
                on_air_sites.update([str(x).strip() for x in sites])
    except Exception as e:
        print(f"Error reading {tracker_path}: {e}")
    return on_air_sites

def generate_data():
    base_dir = r'E:\MBF Rollout Dashboard'
    on_air_path = os.path.join(base_dir, 'On Air Progress Tracker.xlsx')
    on_air_sites = get_on_air_sites(on_air_path)
    
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
        }

        for idx, row in df.iterrows():
            try:
                lat_val, lon_val = row.get(col_map['lat']), row.get(col_map['lon'])
                if pd.isna(lat_val) or pd.isna(lon_val): continue
                lat = float(str(lat_val).replace(',', '.'))
                lon = float(str(lon_val).replace(',', '.'))
                if not (8.0 < lat < 24.0 and 102.0 < lon < 110.0): continue
            except: continue
            
            rf, cdd, lock = clean_val(row.get(col_map['rf_approved'])), clean_val(row.get(col_map['cdd_approved'])), clean_val(row.get(col_map['lock_date']))
            site_name_raw = clean_val(row.get(col_map['site_name']))
            
            if site_name_raw in on_air_sites:
                status = "On-Air"
            elif lock != "-":
                status = "RFI Ready"
            else:
                status = "Pending"
            
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
                'site_name': clean_val(row.get(col_map['site_name'])),
                'province': province_val,
                'district': clean_val(row.get(col_map['district'])),
                'enodeb_id': enodeb_id, 'lat': lat, 'lon': lon,
                'vip': vip_val, 'is_vip': is_vip, 'scenario': clean_val(row.get(col_map['scenario'])),
                'site_type': clean_val(row.get(col_map['site_type'])), 'status': status
            }
            site['timeline'] = clean_val(row.get(col_map[f"timeline_{'north' if region_name=='North' else 'other'}"]))
            all_sites.append(site)

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
        f.write(";\nconst polygonData = ")
        json.dump(polygons, f, ensure_ascii=False, indent=2)
        f.write(";")
    print(f"Data saved to {output_path} ({len(all_sites)} sites)")

if __name__ == "__main__":
    generate_data()
