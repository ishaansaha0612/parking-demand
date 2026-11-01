"""One command: generate scans, load SQLite, run SQL, chart, simulate the pilot."""
import json
from pathlib import Path
from src.generate_data import generate, lots_table
from src.analysis import run

Path("data").mkdir(exist_ok=True)
generate().to_csv("data/permit_scans.csv", index=False)
lots_table().to_csv("data/lots.csv", index=False)
r = run("data/permit_scans.csv", "data/lots.csv", "outputs")
print(json.dumps(r, indent=2))
print("\nSee outputs/SUMMARY.md")
