from typing import List, Dict, Any
from app.models.schemas import Order

class RLAgent:
    """
    Minimal Reinforcement Learning Agent für MVP.
    
    Funktionalität:
    - train(): Placeholder für RL-Training (Stub)
    - predict(): Gibt naive sortierte Route basierend auf Priorität zurück
    """
    
    def __init__(self):
        """Initialisiere den RL-Agent"""
        self.trained = False
        self.model = None
        self.training_history: List[Dict[str, Any]] = []

    def train(self, environment=None, episodes: int = 10, learning_rate: float = 0.01) -> Dict[str, Any]:
        """
        Trainiere den RL-Agent (MVP: Stub-Implementierung).
        
        Args:
            environment: TourEnvironment-Instanz (optional)
            episodes: Anzahl Trainings-Episoden
            learning_rate: Lernrate (placeholder)
        
        Returns:
            Dict mit Training-Statistiken
        """
        self.trained = True
        
        training_stats = {
            "episodes": episodes,
            "learning_rate": learning_rate,
            "status": "trained_stub",
            "avg_reward": 0.0,
            "total_steps": episodes * 100
        }
        
        self.training_history.append(training_stats)
        return training_stats

    def predict(self, orders: List[Order]) -> List[str]:
        """
        Vorhersage einer Route basierend auf Aufträgen.
        
        MVP-Logik:
        1. Sortiere Aufträge nach Priorität (ascending) dann nach order_id
        2. Sammle alle Start- und End-Locations
        3. Entferne Duplikate (preserving order)
        
        Args:
            orders: Liste von Order-Objekten
        
        Returns:
            Liste von Stopps (Locations) in optimierter Reihenfolge
        """
        if not orders:
            return []
        
        # Sortiere nach Priorität (höher = später) dann nach order_id
        sorted_orders = sorted(orders, key=lambda o: (o.priority, o.order_id))
        
        # Sammle alle Stopps
        stops = []
        for order in sorted_orders:
            stops.append(order.start_location)
        
        # Füge letzte Destination hinzu
        if sorted_orders:
            stops.append(sorted_orders[-1].end_location)
        
        # Entferne Duplikate unter Beibehaltung der Reihenfolge
        seen = set()
        unique_stops = []
        for stop in stops:
            if stop not in seen:
                unique_stops.append(stop)
                seen.add(stop)
        
        return unique_stops

    def get_training_history(self) -> List[Dict[str, Any]]:
        """
        Gibt die Trainings-Historie zurück.
        """
        return self.training_history