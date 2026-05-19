import pandas as pd

tracker_file = r'E:\MBF Rollout Dashboard\On Air Progress Tracker.xlsx'

sheets = ['Ha Noi Progress', 'North 5G Progress', 'Middle Swap Progress ', 'Middle 5G  Progress', 'South 5G  Progress Tracker']

for sheet in sheets:
    df = pd.read_excel(tracker_file, sheet_name=sheet, nrows=2, header=None)
    print(f"\nTracker Sheet: {sheet}")
    for row in df.values.tolist():
        try:
            print([str(x).encode('utf-8') for x in row])
        except:
            pass
