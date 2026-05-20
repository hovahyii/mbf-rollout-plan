import pandas as pd
import os
import glob
from datetime import datetime

def extract_site_lists():
    # Configuration
    base_dir = r'E:\MBF Rollout Dashboard'
    file_pattern = os.path.join(base_dir, 'MBF RAN Project - Phase 1 PO - Master Site List*.xlsx')
    
    # Regional configurations: (Sheet Name, Target Directory)
    regions = {
        'North_Site': 'North Region',
        'Middle_Site': 'Middle Region',
        'South_Site': 'South Region'
    }
    
    # Find the latest master file
    files = glob.glob(file_pattern)
    if not files:
        print("No master site list file found.")
        return
    
    # Sort by date in filename (assuming YYYYMMDD format)
    latest_file = sorted(files)[-1]
    print(f"Processing latest file: {latest_file}")
    
    for sheet_name, target_folder in regions.items():
        print(f"Extracting {sheet_name}...")
        
        # Define output path
        output_dir = os.path.join(base_dir, target_folder)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, f"{sheet_name}.xlsx")
        
        try:
            # Read the sheet, skipping first 3 rows (Excel 1, 2, 3)
            # This makes Excel Row 4 the header.
            df = pd.read_excel(latest_file, sheet_name=sheet_name, skiprows=3)
            
            # Limit to columns A through CL (first 90 columns)
            # Use iloc to avoid errors if the sheet has fewer columns
            df = df.iloc[:, :90]
            
            # Save to the target directory
            df.to_excel(output_file, index=False)
            print(f"Saved to {output_file}")
            
        except Exception as e:
            print(f"Error processing {sheet_name}: {e}")

if __name__ == "__main__":
    extract_site_lists()
