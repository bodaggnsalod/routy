from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from app.models.schemas import Order, RouteResponse, StatsResponse
from app.services.rl_agent import RLAgent
from app.services.road_network import road_network
from app.services.travel_time_predictor import travel_predictor

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


@router.get("/travel-time/predict", tags=["travel-time"])
def predict_travel_time(
    start: str, 
    end: str, 
    departure_time: str = None
):
    """
    Vorhersagt Reisezeit für eine spezifische Route und Abfahrtszeit.
    
    - **start**: Startort
    - **end**: Zielort  
    - **departure_time**: ISO-Format datetime (optional, default: jetzt)
    """
    if not road_network.has_location(start):
        raise HTTPException(status_code=404, detail=f"Start location '{start}' not found")
    if not road_network.has_location(end):
        raise HTTPException(status_code=404, detail=f"End location '{end}' not found")
    
    # Parse departure time
    if departure_time:
        try:
            dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format.")
    else:
        dt = datetime.now()
    
    prediction = travel_predictor.predict_travel_time(start, end, dt)
    
    if 'error' in prediction:
        raise HTTPException(status_code=404, detail=prediction['error'])
    
    return prediction


@router.get("/travel-time/optimal-departure", tags=["travel-time"])
def get_optimal_departure(
    start: str,
    end: str,
    earliest_departure: str = None,
    latest_arrival: str = None,
    hours_window: int = 12
):
    """
    Findet optimalen Startzeitpunkt für eine Route.
    
    - **start**: Startort
    - **end**: Zielort
    - **earliest_departure**: Früheste Abfahrt (ISO, optional)
    - **latest_arrival**: Späteste Ankunft (ISO, optional)
    - **hours_window**: Suchfenster in Stunden (default: 12)
    """
    if not road_network.has_location(start):
        raise HTTPException(status_code=404, detail=f"Start location '{start}' not found")
    if not road_network.has_location(end):
        raise HTTPException(status_code=404, detail=f"End location '{end}' not found")
    
    # Parse times
    earliest = None
    latest = None
    
    if earliest_departure:
        try:
            earliest = datetime.fromisoformat(earliest_departure.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid earliest_departure format")
    
    if latest_arrival:
        try:
            latest = datetime.fromisoformat(latest_arrival.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid latest_arrival format")
    
    result = travel_predictor.find_optimal_departure_time(
        start, end, earliest, latest, hours_window
    )
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result


@router.get("/travel-time/forecast", tags=["travel-time"])
def get_travel_time_forecast(
    start: str,
    end: str,
    hours: int = 24
):
    """
    Erstellt stündliche Verkehrsprognose für eine Route.
    
    - **start**: Startort
    - **end**: Zielort
    - **hours**: Anzahl Stunden (default: 24, max: 48)
    """
    if not road_network.has_location(start):
        raise HTTPException(status_code=404, detail=f"Start location '{start}' not found")
    if not road_network.has_location(end):
        raise HTTPException(status_code=404, detail=f"End location '{end}' not found")
    
    if hours > 48:
        raise HTTPException(status_code=400, detail="Maximum 48 hours forecast")
    
    forecast = travel_predictor.get_hourly_forecast(start, end, hours)
    
    return {
        "start": start,
        "end": end,
        "forecast_hours": hours,
        "forecast": forecast
    }


