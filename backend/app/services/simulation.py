from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import Order

class Simulation:
    """
    Simulationsumgebung für MVP-Tests.
    
    Simuliert:
    - Zeitschritte (ticks)
    - Events (Auftrag angekommen, Fahrzeug angekommen, etc.)
    - Fahrzeug-Positionen
    """
    
    def __init__(self, start_time: int = 0):
        """
        Initialisiere Simulation.
        
        Args:
            start_time: Startzeitpunkt
        """
        self.time = start_time
        self.events: List[Dict[str, Any]] = []
        self.vehicles_positions: Dict[str, str] = {}
        self.completed_orders: List[int] = []
        self.active_orders: List[Order] = []

    def add_event(self, event: Dict[str, Any]):
        """
        Füge ein Event zur Simulation hinzu.
        
        Args:
            event: Event-Dict mit 'type', 'timestamp', 'data'
        """
        self.events.append(event)
        # Sortiere Events nach Timestamp
        self.events.sort(key=lambda e: e.get("timestamp", float('inf')))

    def run_step(self) -> Optional[Dict[str, Any]]:
        """
        Führe einen Simulationsschritt aus.
        
        Returns:
            Nächstes verarbeitetes Event oder None
        """
        self.time += 1
        
        if self.events:
            event = self.events.pop(0)
            self._process_event(event)
            return event
        
        return None

    def _process_event(self, event: Dict[str, Any]):
        """
        Verarbeite ein Event.
        
        MVP: Logging und State-Update
        """
        event_type = event.get("type")
        
        if event_type == "order_arrived":
            self.active_orders.append(event.get("data", {}))
        elif event_type == "order_completed":
            order_id = event.get("data", {}).get("order_id")
            if order_id:
                self.completed_orders.append(order_id)
        elif event_type == "vehicle_moved":
            vehicle_id = event.get("data", {}).get("vehicle_id")
            location = event.get("data", {}).get("location")
            if vehicle_id and location:
                self.vehicles_positions[vehicle_id] = location

    def run_simulation(self, num_steps: int = 100) -> Dict[str, Any]:
        """
        Führe mehrere Simulationsschritte hintereinander aus.
        
        Args:
            num_steps: Anzahl der Steps zu simulieren
        
        Returns:
            Finales Simulations-State
        """
        for _ in range(num_steps):
            if not self.run_step():
                break
        
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """
        Holt den aktuellen Zustand der Simulation.
        
        Returns:
            State representation
        """
        return {
            "time": self.time,
            "events_remaining": len(self.events),
            "vehicles_positions": self.vehicles_positions,
            "active_orders": len(self.active_orders),
            "completed_orders": len(self.completed_orders),
            "timestamp": datetime.now().isoformat()
        }

    def reset(self):
        """Setze Simulation zurück."""
        self.time = 0
        self.events = []
        self.vehicles_positions = {}
        self.completed_orders = []
        self.active_orders = []