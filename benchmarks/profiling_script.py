import os
import pandas as pd
from pathlib import Path

DATA_DIR = Path("/home/bishamon/proyek/Spatial-Temporal-Data-Pipeline/data/bronze")
CSV_FILES = list(DATA_DIR.rglob("*.csv"))

total_size_bytes = 0
total_rows = 0
columns_set = set()
unique_areas = set()

print(f"Found {len(CSV_FILES)} CSV files. Profiling...")

for i, file_path in enumerate(CSV_FILES):
    size = os.path.getsize(file_path)
    total_size_bytes += size
    
    try:
        # Read header to find if 'Area' exists
        header_df = pd.read_csv(file_path, nrows=0)
        cols = list(header_df.columns)
        columns_set.update(cols)
        
        # If it's a water quality dataset, it should have 'Area' or similar. 
        # For simplicity, we'll try to read 'Area'. If not present, just count rows.
        if 'Area' in cols:
            df = pd.read_csv(file_path, usecols=['Area'])
            total_rows += len(df)
            unique_areas.update(df['Area'].dropna().unique())
        else:
            # Just count rows for CSVs without 'Area'
            df = pd.read_csv(file_path, usecols=[cols[0]])
            total_rows += len(df)

    except Exception as e:
        print(f"Skipping {file_path.name} due to error: {e}")

print("=" * 40)
print("PROFILING RESULTS")
print("=" * 40)
print(f"Total Files Analyzed : {len(CSV_FILES)}")
print(f"Total Size           : {total_size_bytes / (1024**3):.4f} GB ({total_size_bytes / (1024**2):.2f} MB)")
print(f"Total Rows           : {total_rows:,}")
print(f"Total Columns        : {len(columns_set)}")
print(f"Column Names         : {', '.join(list(columns_set)[:10])}... (truncated)")
print(f"Cardinality ('Area') : {len(unique_areas)}")
print("=" * 40)
