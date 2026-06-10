import re

with open('generate_rollout_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'def get_on_air_info\(tracker_path, target_sheets=None\):.*?return on_air_info', content, re.DOTALL)
if not match:
    print('Not found')
    import sys; sys.exit(1)

new_func = """def get_on_air_info(tracker_path, target_sheets=None):
    on_air_info = {}
    try:
        import pandas as pd
        xl = pd.ExcelFile(tracker_path)
        for s in xl.sheet_names:
            if 'Summary' in s: continue
            
            matched = False
            if target_sheets:
                for ts in target_sheets:
                    if ts.strip().lower() == s.strip().lower():
                        matched = True
                        break
            if target_sheets and not matched: continue
            
            df = pd.read_excel(tracker_path, sheet_name=s, header=None)
            
            header_idx = -1
            for r in range(min(5, len(df))):
                row_vals = [str(x).strip() for x in df.iloc[r].tolist()]
                if 'Physical Site Name' in row_vals or 'Site Name' in row_vals:
                    header_idx = r
                    break
            
            if header_idx == -1: continue
            
            header = [str(x).strip() for x in df.iloc[header_idx].tolist()]
            name_col = header.index('Physical Site Name') if 'Physical Site Name' in header else header.index('Site Name')
            
            on_air_day_cols = [i for i, x in enumerate(header) if x == 'On-air Day']
            site_status_col = header.index('Site Status') if 'Site Status' in header else -1
            
            is_swap_sheet = 'swap' in s.lower()
            is_5g_only_sheet = '5g' in s.lower() and not is_swap_sheet
            
            def is_past_date(val):
                if not pd.notna(val) or str(val).strip().lower() in ['nan', 'none', '']:
                    return False
                try:
                    d = pd.to_datetime(val)
                    return d <= pd.Timestamp.now()
                except:
                    val_str = str(val).strip().lower()
                    if 'on air' in val_str or 'ok' in val_str: return True
                    return False

            for idx, row in df.iloc[header_idx+1:].iterrows():
                site_name = str(row[name_col]).strip()
                if not site_name or site_name.lower() in ['nan', 'none', '']: continue
                
                date_4g = None
                date_5g = None
                
                if is_swap_sheet:
                    if len(on_air_day_cols) > 0:
                        val = row[on_air_day_cols[0]]
                        if is_past_date(val): date_4g = val
                    if len(on_air_day_cols) > 1:
                        val = row[on_air_day_cols[1]]
                        if is_past_date(val): date_5g = val
                else:
                    for c_idx in reversed(on_air_day_cols):
                        val = row[c_idx]
                        if is_past_date(val):
                            date_5g = val
                            break
                
                if site_status_col != -1 and str(row[site_status_col]).strip().lower() in ['on air', 'ok']:
                    if not date_4g and not date_5g:
                        if is_5g_only_sheet: date_5g = 'On-Air'
                        else: date_4g = 'On-Air'
                
                if date_4g or date_5g:
                    def format_date(d):
                        if not d: return "-"
                        if d == 'On-Air': return 'On-Air'
                        if hasattr(d, 'strftime'): return d.strftime('%Y-%m-%d')
                        return str(d).split(' ')[0]
                        
                    date_4g_str = format_date(date_4g)
                    date_5g_str = format_date(date_5g)
                        
                    on_air_info[site_name.upper()] = {
                        'on_air_4g': date_4g_str,
                        'on_air_5g': date_5g_str
                    }
    except Exception as e:
        print(f"Error reading {tracker_path}: {e}")
    return on_air_info"""

content = content[:match.start()] + new_func + content[match.end():]
with open('generate_rollout_data.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced successfully')
