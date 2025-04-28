import json
from pathlib import Path
from typing import List, Dict

FILE = Path(__file__).with_name("doctors.json")

def load_data() -> List[Dict]:
    return json.loads(FILE.read_text(encoding="utf8"))

def get_session():
    yield load_data()        # FastAPI dependency
