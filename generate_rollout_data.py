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

def get_on_air_info(tracker_path, target_sheets=None):
    on_air_info = {}
    try:
        xl = pd.ExcelFile(tracker_path)
        for s in xl.sheet_names:
            if 'Summary' in s: continue
            if target_sheets and s not in target_sheets: continue
            df = pd.read_excel(tracker_path, sheet_name=s, header=None)
            
            header_idx = -1
            for r in range(min(5, len(df))):
                row_vals = [str(x).strip() for x in df.iloc[r].tolist()]
                if 'Site Name' in row_vals or 'Physical Site Name' in row_vals:
                    header_idx = r
                    break
            
            if header_idx == -1: continue
            
            header = [str(x).strip() for x in df.iloc[header_idx].tolist()]
            
            name_col = -1
            if 'Site Name' in header:
                name_col = header.index('Site Name')
            elif 'Physical Site Name' in header:
                name_col = header.index('Physical Site Name')
            else:
                continue
            
            # Additional names
            additional_name_cols = []
            for col_name in ['NEname_Old_4G_NSN', 'NEName_New4G', 'NEName_New5G', 'OMC Site name (Short)', 'OMC Site name']:
                if col_name in header:
                    additional_name_cols.append(header.index(col_name))
            
            # 4G and 5G detection
            on_air_day_cols = [i for i, x in enumerate(header) if x == 'On-air Day']
            
            # If the sheet name implies 5G only
            is_5g_only_sheet = '5G' in s.upper() and 'SWAP' not in s.upper()
            
            for idx, row in df.iloc[header_idx+1:].iterrows():
                site_name = str(row[name_col]).strip()
                if not site_name or site_name.lower() in ['nan', 'none', '']: continue
                
                date_4g = None
                date_5g = None
                
                # Check based on on-air day presence
                if is_5g_only_sheet:
                    # Treat first On-air Day column as 5G
                    if len(on_air_day_cols) > 0:
                        val = row[on_air_day_cols[0]]
                        if not pd.isna(val) and str(val).strip().lower() not in ['nan', 'none', '']:
                            date_5g = val
                    if len(on_air_day_cols) > 1 and not date_5g:
                        val = row[on_air_day_cols[1]]
                        if not pd.isna(val) and str(val).strip().lower() not in ['nan', 'none', '']:
                            date_5g = val
                else:
                    # Treat first as 4G, second as 5G
                    if len(on_air_day_cols) > 0:
                        val = row[on_air_day_cols[0]]
                        if not pd.isna(val) and str(val).strip().lower() not in ['nan', 'none', '']:
                            date_4g = val
                    if len(on_air_day_cols) > 1:
                        val = row[on_air_day_cols[1]]
                        if not pd.isna(val) and str(val).strip().lower() not in ['nan', 'none', '']:
                            date_5g = val
                            
                # Fallback: check Site Status column
                site_status_col = header.index('Site Status') if 'Site Status' in header else -1
                if site_status_col != -1:
                    status_val = str(row[site_status_col]).strip().lower()
                    if status_val == 'on air':
                        if is_5g_only_sheet:
                            if not date_5g: date_5g = 'On-Air'
                        else:
                            if not date_4g: date_4g = 'On-Air'
                
                if date_4g or date_5g:
                    def format_date(d):
                        if not d: return "-"
                        if d == 'On-Air': return 'On-Air'
                        if hasattr(d, 'strftime'): return d.strftime('%Y-%m-%d')
                        return str(d).split(' ')[0]
                        
                    date_4g_str = format_date(date_4g)
                    date_5g_str = format_date(date_5g)
                        
                    entry = {
                        'on_air_4g': date_4g_str,
                        'on_air_5g': date_5g_str
                    }
                    on_air_info[site_name.upper()] = entry
                    
                    for ac in additional_name_cols:
                        try:
                            ac_name = str(row.iloc[ac]).strip().upper()
                            if ac_name and ac_name.lower() not in ['nan', 'none']:
                                on_air_info[ac_name] = entry
                        except: pass
    except Exception as e:
        print(f"Error reading {tracker_path}: {e}")
    return on_air_info

def get_rollout_details(file_path):
    details = {} # site_id -> {rfi, on_air, bbu, type}
    try:
        print(f"Loading rollout details from {file_path}...")
        df = pd.read_excel(file_path, sheet_name='Site Rollout Plan', skiprows=2)
        
        # 108: Main Site Name (BBU Location)
        # Removed on_air_cols parsing as on-air status must strictly come from On Air Progress Tracker.xlsx
        # User requested explicitly using Column MF (index 343) for RFI Ready
        rfi_cols = [343]
        
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

                # (On Air checking removed here per user constraint)
                rfi = "-"
                for c in rfi_cols:
                    val = clean_val(row.iloc[c])
                    if val != "-":
                        rfi = val
                        break
                
                entry = {
                    'rfi_date': rfi, 'on_air_date': '-', # Enforced: must come from On Air Progress Tracker
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
    
    # New source file (match both .xlsm and .xlsx)
    rollout_files = glob.glob(os.path.join(base_dir, '60086951_56A0US7_*.xlsm'))
    rollout_files += glob.glob(os.path.join(base_dir, '60086951_56A0US7_*.xlsx'))
    if rollout_files:
        rollout_file = sorted(rollout_files)[-1]
    else:
        rollout_file = os.path.join(base_dir, '60086951_56A0US7_20260518214245.xlsm')
    rollout_details = get_rollout_details(rollout_file) if os.path.exists(rollout_file) else {}

    ep_files = glob.glob(os.path.join(base_dir, 'EP_Existing_*.xlsx'))
    
    on_air_path = os.path.join(base_dir, 'On Air Progress Tracker.xlsx')
    on_air_sheet_mapping = {
        'North': ['Ha Noi Progress', 'North 5G Progress'],
        'Middle': ['Middle Swap Progress', 'Middle 5G Progress'],
        'South': ['South Swap Progress', 'South 5G New Progress']
    }
    
    file_pattern = os.path.join(base_dir, 'MBF RAN Project - Phase 1 PO - Master Site List*.xlsx')
    
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
        
        target_sheets = on_air_sheet_mapping.get(region_name, [])
        on_air_info = get_on_air_info(on_air_path, target_sheets)
        
        df = pd.read_excel(latest_file, sheet_name=sheet_name, skiprows=3)
        
        col_map = {
            'po': find_col(df, ['PO']),
            'site_name': find_col(df, ['Physcial Site Name', 'Physical Site Name']),
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
            'bbu_location_master': find_col(df, ['Main Site Name (BBU Location)', 'bbu location']),
            'bbu_solution': find_col(df, ['CRAN BBU Solution', 'bbu solution']),
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
            
            is_on_air_in_tracker = site_name_upper in on_air_info
            
            if is_on_air_in_tracker:
                ep_entry = on_air_info[site_name_upper]
                on_air_4g = ep_entry.get('on_air_4g', '-')
                on_air_5g = ep_entry.get('on_air_5g', '-')
                
                if on_air_4g != '-' and on_air_5g != '-':
                    status = "4G & 5G On-Air"
                elif on_air_4g != '-':
                    status = "4G On-Air"
                elif on_air_5g != '-':
                    status = "5G On-Air"
                else:
                    status = "Pending"
                    
                on_air_date = "On-Air"
            else:
                on_air_date = "-"
                on_air_4g = "-"
                on_air_5g = "-"
                if rfi_date != "-":
                    status = "RFI Ready"
                else:
                    status = "Pending"
            
            bbu_location_master = clean_val(row.get(col_map['bbu_location_master']))
            if bbu_location_master != "-" and bbu_location_master.upper() != site_name_upper:
                bbu_location = bbu_location_master
            else:
                bbu_location = "-"
                
            detailed_type = site_detail.get('detailed_type', "-")
            bbu_solution = clean_val(row.get(col_map['bbu_solution']))
                
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
                
            try:
                cluster_val = clean_val(row.iloc[54])
            except IndexError:
                cluster_val = "-"
                
            site = {
                'region': final_region, 'po': clean_val(row.get(col_map['po'])),
                'site_name': site_name_raw,
                'province': province_val,
                'district': clean_val(row.get(col_map['district'])),
                'cluster': cluster_val,
                'enodeb_id': enodeb_id, 'lat': lat, 'lon': lon,
                'vip': vip_val, 'is_vip': is_vip, 'scenario': clean_val(row.get(col_map['scenario'])),
                'site_type': clean_val(row.get(col_map['site_type'])), 
                'detailed_type': detailed_type,
                'status': status, 'rat': rat_val,
                'rfi_date': rfi_date, 'on_air_date': on_air_date,
                'on_air_4g': on_air_4g, 'on_air_5g': on_air_5g,
                'bbu_location': bbu_location,
                'bbu_solution': bbu_solution
            }
            site['timeline'] = clean_val(row.get(col_map[f"timeline_{'north' if region_name=='North' else 'other'}"]))
            all_sites.append(site)

    # Create a global coordinate lookup for all sites (from master and rollout)
    coord_lookup = {}
    for s in all_sites:
        coord_lookup[s['site_name'].upper()] = [s['lat'], s['lon']]
        if s['enodeb_id'] != '-': coord_lookup[s['enodeb_id'].upper()] = [s['lat'], s['lon']]
    
    for sid, d in rollout_details.items():
        if sid.upper() not in coord_lookup and d['lat'] and d['lon']:
            # Only use rollout plan coordinates if missing from master site list
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
            
    # Compute missing clusters using ray casting on polygons
    def point_in_polygon(point, poly):
        x, y = point
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(1, n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def point_in_feature(point, feature):
        geom = feature['geometry']
        geom_type = geom['type']
        if geom_type == 'Polygon':
            return point_in_polygon(point, geom['coordinates'][0])
        elif geom_type == 'MultiPolygon':
            for poly in geom['coordinates']:
                if point_in_polygon(point, poly[0]):
                    return True
        return False
        
    for reg, feature_collection in polygons.items():
        if not feature_collection: continue
        for feature in feature_collection['features']:
            feature['properties']['computed_cluster'] = None
            cluster_counts = {}
            sites_in_poly = []
            
            for s in all_sites:
                if s['lat'] and s['lon']:
                    pt = (s['lon'], s['lat'])
                    if point_in_feature(pt, feature):
                        sites_in_poly.append(s)
                        c = s.get('cluster', '-')
                        if c != '-':
                            cluster_counts[c] = cluster_counts.get(c, 0) + 1
            
            if cluster_counts:
                best_cluster = max(cluster_counts.items(), key=lambda x: x[1])[0]
                feature['properties']['computed_cluster'] = best_cluster
                for s in sites_in_poly:
                    s['cluster'] = best_cluster
    
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
