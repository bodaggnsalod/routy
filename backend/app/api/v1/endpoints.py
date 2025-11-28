from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.schemas import Order, RouteResponse, StatsResponse
from app.services.rl_agent import RLAgent
from app.services.traffic_api import traffic_client
from app.services.road_network import road_network
from app.services.environment import TourEnvironment
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


@router.get("/traffic/live", tags=["traffic"])
def get_live_traffic():
    """
    Holt aktuelle Live-Verkehrsinformationen von der Autobahn API.
    
    Returns:
        Dict mit Traffic-Status und Delay-Faktor
    """
    try:
        delay_factor = traffic_client.get_live_traffic_delay()
        
        return {
            "delay_factor": delay_factor,
            "status": traffic_client._get_status_label(delay_factor),
            "timestamp": "now",
            "source": "autobahn-api"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Traffic API unavailable: {str(e)}")


@router.get("/traffic/route", tags=["traffic"])
def get_traffic_for_route(start: str, end: str):
    """
    Holt Verkehrsinformationen für eine spezifische Route.
    
    - **start**: Startort
    - **end**: Zielort
    """
    try:
        traffic_info = traffic_client.get_traffic_info_for_route(start, end)
        return traffic_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get traffic info: {str(e)}")


@router.post("/agent/train", tags=["ml"])
def train_agent(episodes: int = 10, learning_rate: float = 0.01):
    """
    Trainiert den RL-Agent mit gegebenen Parametern.
    
    - **episodes**: Anzahl Trainings-Episoden
    - **learning_rate**: Lernrate für DQN
    """
    try:
        # Erstelle Demo-Environment für Training
        demo_orders = [
            Order(order_id=i, start_location="Berlin", end_location="München", priority=1)
            for i in range(5)
        ]
        env = TourEnvironment(orders=demo_orders)
        env.add_vehicle("truck_1")
        
        stats = agent.train(environment=env, episodes=episodes, learning_rate=learning_rate)
        
        return {
            "status": "success",
            "training_stats": stats,
            "model_ready": agent.trained
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/agent/history", tags=["ml"])
def get_training_history():
    """
    Gibt die Trainings-Historie des RL-Agents zurück.
    """
    return {
        "history": agent.get_training_history(),
        "total_trainings": len(agent.get_training_history())
    }


@router.get("/network/locations", tags=["network"])
def get_network_locations():
    """
    Gibt alle verfügbaren Standorte im Straßennetzwerk zurück.
    """
    return {
        "locations": road_network.get_all_locations(),
        "total": len(road_network.get_all_locations())
    }


@router.get("/network/path", tags=["network"])
def get_shortest_path(start: str, end: str):
    """
    Berechnet den kürzesten Pfad zwischen zwei Standorten.
    
    - **start**: Startort
    - **end**: Zielort
    """
    if not road_network.has_location(start):
        raise HTTPException(status_code=404, detail=f"Start location '{start}' not found")
    if not road_network.has_location(end):
        raise HTTPException(status_code=404, detail=f"End location '{end}' not found")
    
    path = road_network.shortest_path(start, end)
    distance = road_network.shortest_path_length(start, end)
    
    if path is None:
        raise HTTPException(status_code=404, detail="No path found between locations")
    
    return {
        "start": start,
        "end": end,
        "path": path,
        "distance_minutes": distance,
        "stops_count": len(path)
    }


@router.get("/network/congested", tags=["network"])
def get_congested_routes(threshold: float = 0.5):
    """
    Gibt alle Routen mit hohem Traffic zurück.
    
    - **threshold**: Minimaler Delay-Faktor (default: 0.5)
    """
    congested = road_network.get_congested_routes(threshold)
    
    return {
        "threshold": threshold,
        "congested_routes": congested,
        "count": len(congested)
    }


@router.post("/network/simulate-traffic", tags=["network"])
def simulate_traffic():
    """
    Simuliert Traffic-Delays auf zufälligen Routen (für Demo-Zwecke).
    """
    import random
    
    # Hole alle Routen
    all_edges = road_network.get_all_edges()
    
    # Wähle 2-3 zufällige Routen und setze hohe Delays
    num_congested = min(3, len(all_edges))
    congested_routes = random.sample(all_edges, num_congested)
    
    updates = []
    for route in congested_routes:
        # Setze Delay zwischen 0.5 und 1.0
        delay = random.uniform(0.5, 1.0)
        road_network.update_traffic(route['start'], route['end'], delay)
        updates.append({
            'route': f"{route['start']} ↔ {route['end']}",
            'delay_factor': delay
        })
    
    return {
        "message": "Traffic simulated",
        "updated_routes": updates,
        "count": len(updates)
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


