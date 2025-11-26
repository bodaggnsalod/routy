from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Order(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": 1,
                "start_location": "Berlin",
                "end_location": "München",
                "priority": 1
            }
        }
    )
    
    order_id: int = Field(..., description="Unique order ID")
    start_location: str = Field(..., description="Start location")
    end_location: str = Field(..., description="End location")
    priority: Optional[int] = Field(1, ge=1, le=10, description="Priority (1=highest)")

class Vehicle(BaseModel):
    vehicle_id: str
    capacity: Optional[int] = 100

class Stop(BaseModel):
    location: str
    eta_minutes: Optional[int] = None

class RouteResponse(BaseModel):
    route_id: str
    stops: List[str]
    estimated_duration_minutes: int
    total_orders: int

class StatsResponse(BaseModel):
    total_routes_optimized: int
    avg_duration_minutes: float
    total_orders_processed: int
    avg_stops_per_route: float