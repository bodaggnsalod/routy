from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from src.models import Order
from src.rl_engine.agent import RLAgent
from src.api import endpoints
from src.utils.config_loader import load_config

# Load configuration
config = load_config()

# Initialize FastAPI app
app = FastAPI(
    title="Routy API",
    description="KI-basierte dynamische Tourenplanung",
    version=config.get("api", {}).get("version", "1.0")
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RL Agent
agent = RLAgent()

# Include routers
app.include_router(endpoints.router)

@app.get("/health", tags=["Monitoring"])
def read_health():
    """Health-Check Endpunkt"""
    return {
        "status": "ok",
        "service": "Routy API",
        "version": config.get("api", {}).get("version", "1.0")
    }

@app.post("/api/v1/route/optimize", tags=["Routing"])
def optimize_route(orders: List[Order]):
    """
    Optimiert eine Liste von Aufträgen zu einer effizienten Route.
    
    Args:
        orders: Liste von Order-Objekten
    
    Returns:
        Optimierte Route mit Stopps und geschätzter Dauer
    """
    stops = agent.predict(orders)
    estimated_duration_minutes = max(10, len(stops) * 10)
    
    return {
        "route_id": "mvp_route_001",
        "stops": stops,
        "estimated_duration_minutes": estimated_duration_minutes
    }

@app.on_event("startup")
async def startup_event():
    """Startup-Hooks"""
    print("🚀 Routy API is starting...")
    print(f"📋 Config loaded: {config}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown-Hooks"""
    print("🛑 Routy API is shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)