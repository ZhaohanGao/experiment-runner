import pandas as pd
from pathlib import Path

# Path that holds all experiment folders
ROOT = Path("examples/energibridge-profiling/experiments/experiment3.0")
OUTPUT_FILE = ROOT / "all_run_tables_combined.csv"

all_frames = []

for csv_file in ROOT.rglob("run_table.csv"):
    try:
        # Example path:
        # experiments/experiment2.0/dijkstra_code_experiment_20250928_124701/run_table.csv
        folder_name = csv_file.parent.name
        # Remove the timestamp suffix (_YYYYMMDD_HHMMSS)
        # Keep only "dijkstra_code_experiment"
        if "_" in folder_name:
            experiment_name = "_".join(folder_name.split("_")[:-2])  # drop last 2 parts (date + time)
        else:
            experiment_name = folder_name

        df = pd.read_csv(csv_file)
        df.insert(0, "experiment_name", experiment_name)
        all_frames.append(df)
        print(f"✅ Collected {csv_file}")
    except Exception as e:
        print(f"⚠️ Skipped {csv_file}: {e}")

if not all_frames:
    print("❌ No run_table.csv files found.")
else:
    combined = pd.concat(all_frames, ignore_index=True)
    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"🎉 Combined CSV saved to: {OUTPUT_FILE}")
    print(f"Total rows: {len(combined)}")
