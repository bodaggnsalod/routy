from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Order, RouteResponse, StatsResponse
from app.services.rl_agent import RLAgent

router = APIRouter()

agent = RLAgent()

@router.post("/route/optimize", response_model=RouteResponse, tags=["routing"])
def optimize_route(orders: List[Order]):
    """
    Optimiert eine Route basierend auf Aufträgen.
    
    - **orders**: Liste von Aufträgen mit Start, Ziel und Priorität
    - **returns**: Optimierte Route mit Stops und geschätzter Dauer
    """
    if not orders:
        raise HTTPException(status_code=400, detail="Orders list cannot be empty")
    
    try:
        stops = agent.predict(orders)
        estimated_duration = max(10, len(stops) * 10)
        
        return RouteResponse(
            route_id=f"route_{len(orders)}_{hash(tuple(o.order_id for o in orders)) % 10000}",
            stops=stops,
            estimated_duration_minutes=estimated_duration,
            total_orders=len(orders)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/route/{route_id}", tags=["routing"])
def get_route(route_id: str):
    """Holt Details einer existierenden Route"""
    return {
        "route_id": route_id,
        "status": "active",
        "stops": ["Location A", "Location B"],
        "current_position": "Location A"
    }

@router.get("/stats", response_model=StatsResponse, tags=["monitoring"])
def get_stats():
    """Statistiken über optimierte Routen"""
    return StatsResponse(
        total_routes_optimized=42,
        avg_duration_minutes=45,
        total_orders_processed=156,
        avg_stops_per_route=4.2
    )

@router.post("/data/upload", tags=["data"])
def upload_data(file_name: str):
    """Placeholder für Daten-Upload"""
    return {
        "message": f"Data file '{file_name}' uploaded successfully",
        "status": "processing"
    }