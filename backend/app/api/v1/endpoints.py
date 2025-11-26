from fastapi import APIRouter, HTTPException
from typing import List
from src.models import Order, Stop
from src.rl_engine.agent import RLAgent

router = APIRouter(prefix="/api/v1", tags=["Routing"])

agent = RLAgent()

@router.post("/route/optimize")
def optimize_route(orders: List[Order]):
    """
    Optimiert eine Liste von Aufträgen zu einer effizienten Route.
    
    Args:
        orders: Liste von Order-Objekten mit start_location, end_location, priority
    
    Returns:
        Dict mit route_id, stops (Liste von Stopps) und estimated_duration_minutes
    """
    if not orders:
        raise HTTPException(status_code=400, detail="Orders list cannot be empty")
    
    try:
        stops = agent.predict(orders)
        estimated_duration = max(10, len(stops) * 10)
        
        return {
            "route_id": f"route_{len(orders)}_{hash(tuple(o.order_id for o in orders)) % 10000}",
            "stops": stops,
            "estimated_duration_minutes": estimated_duration,
            "total_orders": len(orders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route optimization failed: {str(e)}")

@router.get("/route/{route_id}")
def get_route(route_id: str):
    """
    Holt Details einer existierenden Route.
    """
    return {
        "route_id": route_id,
        "status": "active",
        "stops": ["Location A", "Location B"],
        "current_position": "Location A"
    }

@router.post("/data/upload")
def upload_data(file_name: str):
    """
    Placeholder für Daten-Upload (CSV/JSON).
    """
    return {
        "message": f"Data file '{file_name}' uploaded successfully",
        "status": "processing"
    }

@router.get("/stats")
def get_stats():
    """
    Liefert Statistiken über optimierte Routen.
    """
    return {
        "total_routes_optimized": 42,
        "avg_duration_minutes": 45,
        "total_orders_processed": 156,
        "avg_stops_per_route": 4.2
    }