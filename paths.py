import os
import shutil
import sys
from pathlib import Path

FROZEN = getattr(sys, 'frozen', False)

def resource_path(name):
    """Read-only files bundled into the exe (or next to the .py files when developing)."""
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    return base / name

if FROZEN:
    DATA_DIR = Path(os.environ['LOCALAPPDATA']) / 'EPBInventory'
    DATA_DIR.mkdir(parents=True, exist_ok=True)
else:
    DATA_DIR = Path(__file__).parent   # dev: keep using the project folder

DB_PATH = DATA_DIR / 'EPB_point_shoe_inv.db'
if not DB_PATH.exists():
    shutil.copy(resource_path('EPB_point_shoe_inv.db'), DB_PATH)

FILTERS_PATH = resource_path('filters.yaml')
REPORT_PATH = DATA_DIR / 'inventory_report.csv'