import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(path: str | None = None) -> Dict[str, Any]:
    p = Path(path or Path(__file__).parents[1] / "config" / "settings.yaml")
    if not p.exists():
        # fallback to project config location
        p = Path.cwd() / "config" / "settings.yaml"
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

from pydantic import BaseModel
from typing import Optional

class Order(BaseModel):
    order_id: int
    start_location: str
    end_location: str
    priority: Optional[int] = 1

class Vehicle(BaseModel):
    vehicle_id: str
    capacity: Optional[int] = None

class Stop(BaseModel):
    location: str
    eta_minutes: Optional[int] = None