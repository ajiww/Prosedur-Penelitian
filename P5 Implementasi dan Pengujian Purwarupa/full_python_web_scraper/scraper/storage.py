# scraper/storage.py
import json
import os
from config import DB_PATH

def save_data(data):
    # Pastikan folder ada
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

