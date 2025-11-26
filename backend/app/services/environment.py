from typing import Any, Dict, List, Tuple
from app.models.schemas import Order

class TourEnvironment:
    """
    Simulationsumgebung für RL-Training.
    
    Simuliert eine Tourenplanungs-Szene mit:
    - Aufträgen (Orders)
    - Fahrzeugen
    - Zeitpunkt-tracking
    - Reward-Berechnung
    """
    
    def __init__(self, orders: List[Order] | None = None, max_time_steps: int = 1000):
        """
        Initialisiere die Tour-Umgebung.
        
        Args:
            orders: Liste von Order-Objekten
            max_time_steps: Maximale Anzahl von Zeitschritten
        """
        self.orders = orders or []
        self.max_time_steps = max_time_steps
        self.time = 0
        self.vehicles: List[Dict[str, Any]] = []
        self.assigned_orders: Dict[int, int] = {}  # order_id -> vehicle_id mapping
        self.total_reward = 0.0

    def reset(self) -> Dict[str, Any]:
        """
        Setze die Umgebung zurück auf Initial-State.
        
        Returns:
            Initial state representation
        """
        self.time = 0
        self.assigned_orders = {}
        self.total_reward = 0.0
        return self.get_state()

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool]:
        """
        Führe einen Schritt in der Umgebung aus.
        
        Args:
            action: Action-Dict z.B. {'assign': {'order_id': 1, 'vehicle_id': 'v1'}}
        
        Returns:
            (state, reward, done)
        """
        self.time += 1
        
        # Berechne Reward basierend auf Action
        reward = self._compute_reward(action)
        self.total_reward += reward
        
        # Prüfe ob Episode beendet
        done = self.time >= self.max_time_steps or len(self.orders) == 0
        
        return self.get_state(), reward, done

    def _compute_reward(self, action: Dict[str, Any]) -> float:
        """
        Berechne Reward für eine Action.
        
        MVP-Logik: Einfache Heuristik
        - +1 für valide Assignment
        - -0.5 für ungültige Assignment
        """
        if action.get("assign"):
            return 1.0
        return -0.5

    def get_state(self) -> Dict[str, Any]:
        """
        Holt den aktuellen Zustand der Umgebung.
        
        Returns:
            State representation als Dict
        """
        return {
            "time": self.time,
            "orders_left": len(self.orders),
            "vehicles": self.vehicles,
            "assigned_orders_count": len(self.assigned_orders),
            "total_reward": self.total_reward
        }

    def add_vehicle(self, vehicle_id: str, capacity: int = 100):
        """
        Füge ein Fahrzeug zur Umgebung hinzu.
        """
        self.vehicles.append({
            "vehicle_id": vehicle_id,
            "capacity": capacity,
            "current_load": 0
        })

    def assign_order_to_vehicle(self, order_id: int, vehicle_id: str):
        """
        Weise einen Auftrag einem Fahrzeug zu.
        """
        self.assigned_orders[order_id] = vehicle_id