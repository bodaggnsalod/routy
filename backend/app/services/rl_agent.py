from typing import List, Dict, Any, Optional
import numpy as np
import random
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[RL Agent] PyTorch not available, using fallback mode")

from app.models.schemas import Order
from app.services.road_network import road_network
from app.services.traffic_api import traffic_client
from app.core.config import settings


class DQN(nn.Module if TORCH_AVAILABLE else object):
    """
    Deep Q-Network für Route-Optimierung.
    """
    
    def __init__(self, input_dim: int, output_dim: int):
        if not TORCH_AVAILABLE:
            return
        super(DQN, self).__init__()
        hidden_dim = settings.GRAPH_HIDDEN_DIM
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available")
        return self.net(x)


class RLAgent:
    """
    Reinforcement Learning Agent mit DQN und Live-Traffic Integration.
    
    Funktionalität:
    - train(): DQN-Training mit Traffic-Daten
    - predict(): Optimierte Route mit Verkehrsberücksichtigung
    - Fallback auf naive Sortierung wenn PyTorch nicht verfügbar
    """
    
    def __init__(self):
        """Initialisiere den RL-Agent"""
        self.trained = False
        self.model = None
        self.training_history: List[Dict[str, Any]] = []
        self.use_dqn = TORCH_AVAILABLE
        
        if self.use_dqn:
            self._init_dqn_model()
    
    def _init_dqn_model(self):
        """Initialisiere DQN Modell falls PyTorch verfügbar."""
        if not TORCH_AVAILABLE:
            return
        
        # Modell-Dimensionen werden bei Bedarf dynamisch gesetzt
        self.input_dim = None
        self.output_dim = None
        self.optimizer = None
        self.loss_fn = nn.MSELoss() if TORCH_AVAILABLE else None

    def train(self, environment=None, episodes: int = None, learning_rate: float = None) -> Dict[str, Any]:
        """
        Trainiere den RL-Agent.
        
        Wenn PyTorch verfügbar: DQN Training
        Sonst: Stub-Training
        
        Args:
            environment: TourEnvironment-Instanz (optional)
            episodes: Anzahl Trainings-Episoden
            learning_rate: Lernrate
        
        Returns:
            Dict mit Training-Statistiken
        """
        episodes = episodes or settings.RL_EPISODES
        learning_rate = learning_rate or settings.RL_LEARNING_RATE
        
        if not self.use_dqn or environment is None:
            return self._train_stub(episodes, learning_rate)
        
        return self._train_dqn(environment, episodes, learning_rate)
    
    def _train_stub(self, episodes: int, learning_rate: float) -> Dict[str, Any]:
        """Stub-Training ohne DQN."""
        self.trained = True
        
        training_stats = {
            "episodes": episodes,
            "learning_rate": learning_rate,
            "status": "trained_stub",
            "avg_reward": 0.0,
            "total_steps": episodes * 100,
            "mode": "fallback"
        }
        
        self.training_history.append(training_stats)
        return training_stats
    
    def _train_dqn(self, environment, episodes: int, learning_rate: float) -> Dict[str, Any]:
        """
        DQN Training Loop mit Live-Traffic Integration.
        """
        if not TORCH_AVAILABLE:
            return self._train_stub(episodes, learning_rate)
        
        # Initialisiere Modell basierend auf Environment-State
        state = environment.reset()
        state_array = self._state_to_array(state)
        
        if self.input_dim is None:
            self.input_dim = len(state_array)
            self.output_dim = len(environment.get_possible_actions())
            self.model = DQN(self.input_dim, self.output_dim)
            self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        gamma = settings.RL_GAMMA
        epsilon = settings.RL_EPSILON
        
        total_rewards = []
        
        for ep in range(episodes):
            state = environment.reset()
            episode_reward = 0.0
            
            for step in range(settings.GRAPH_MAX_STEPS):
                state_tensor = torch.tensor(
                    self._state_to_array(state), 
                    dtype=torch.float32
                )
                
                # ε-greedy Policy
                if random.random() < epsilon:
                    action = random.randint(0, self.output_dim - 1)
                else:
                    with torch.no_grad():
                        action = self.model(state_tensor).argmax().item()
                
                # Führe Action aus (mit Live-Traffic)
                next_state, reward, done = environment.step(action)
                episode_reward += reward
                
                # Q-Learning Update
                q_values = self.model(state_tensor)
                next_state_tensor = torch.tensor(
                    self._state_to_array(next_state),
                    dtype=torch.float32
                )
                next_q_values = self.model(next_state_tensor)
                
                target = q_values.clone()
                target[action] = reward + gamma * next_q_values.max().item()
                
                loss = self.loss_fn(q_values, target.detach())
                
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                state = next_state
                
                if done:
                    break
            
            total_rewards.append(episode_reward)
        
        self.trained = True
        
        training_stats = {
            "episodes": episodes,
            "learning_rate": learning_rate,
            "status": "trained_dqn",
            "avg_reward": float(np.mean(total_rewards)),
            "total_steps": sum(range(settings.GRAPH_MAX_STEPS)) * episodes,
            "mode": "dqn",
            "epsilon": epsilon,
            "gamma": gamma
        }
        
        self.training_history.append(training_stats)
        return training_stats
    
    def _state_to_array(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Konvertiert Environment-State in NumPy Array.
        """
        # Einfache State-Repräsentation
        return np.array([
            state.get("time", 0),
            state.get("orders_left", 0),
            state.get("assigned_orders_count", 0),
            state.get("total_reward", 0.0)
        ])

    def predict(self, orders: List[Order]) -> List[str]:
        """
        Vorhersage einer Route basierend auf Aufträgen.
        
        Wenn DQN trainiert: Nutze Netzwerk-basierte Optimierung
        Sonst: Naive Sortierung nach Priorität
        
        Args:
            orders: Liste von Order-Objekten
        
        Returns:
            Liste von Stopps (Locations) in optimierter Reihenfolge
        """
        if not orders:
            return []
        
        # Sammle alle Locations
        locations = set()
        for order in orders:
            locations.add(order.start_location)
            locations.add(order.end_location)
        
        # Aktualisiere Straßennetz mit Traffic-Daten
        self._update_network_with_traffic(locations)
        
        if self.use_dqn and self.trained and self.model:
            return self._predict_with_dqn(orders)
        else:
            return self._predict_naive(orders)
    
    def _update_network_with_traffic(self, locations: set):
        """
        Aktualisiere Straßennetzwerk mit aktuellen Verkehrsdaten.
        """
        # Hole Live-Traffic-Delay
        delay_factor = traffic_client.get_live_traffic_delay()
        
        # Update alle relevanten Kanten
        locations_list = list(locations)
        for i, loc1 in enumerate(locations_list):
            for loc2 in locations_list[i+1:]:
                if road_network.has_location(loc1) and road_network.has_location(loc2):
                    road_network.update_traffic(loc1, loc2, delay_factor)
    
    def _predict_with_dqn(self, orders: List[Order]) -> List[str]:
        """
        DQN-basierte Route-Optimierung mit Netzwerk-Routing.
        """
        if not TORCH_AVAILABLE or not self.model:
            return self._predict_naive(orders)
        
        # Sortiere zunächst nach Priorität
        sorted_orders = sorted(orders, key=lambda o: (o.priority, o.order_id))
        
        # Baue Route mit kürzesten Pfaden
        route = []
        current_location = None
        
        for order in sorted_orders:
            start = order.start_location
            end = order.end_location
            
            # Füge Standorte zum Netzwerk hinzu falls nötig
            if not road_network.has_location(start):
                road_network.add_location(start)
            if not road_network.has_location(end):
                road_network.add_location(end)
            
            if current_location is None:
                # Erste Station
                route.append(start)
                current_location = start
            else:
                # Finde kürzesten Pfad zum nächsten Start
                path = road_network.shortest_path(current_location, start)
                if path and len(path) > 1:
                    route.extend(path[1:])  # Ohne aktuellen Standort
                elif current_location != start:
                    route.append(start)
                current_location = start
            
            # Füge Ziel hinzu
            if end != current_location:
                path = road_network.shortest_path(current_location, end)
                if path and len(path) > 1:
                    route.extend(path[1:])
                else:
                    route.append(end)
                current_location = end
        
        # Entferne Duplikate unter Beibehaltung der Reihenfolge
        seen = set()
        unique_route = []
        for stop in route:
            if stop not in seen:
                unique_route.append(stop)
                seen.add(stop)
        
        return unique_route
    
    def _predict_naive(self, orders: List[Order]) -> List[str]:
        """
        Naive Sortierung nach Priorität (Fallback ohne DQN).
        
        MVP-Logik:
        1. Sortiere Aufträge nach Priorität (ascending) dann nach order_id
        2. Sammle alle Start- und End-Locations
        3. Entferne Duplikate (preserving order)
        """
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
    
    def save_model(self, path: str = "dqn_traffic_model.pth"):
        """
        Speichert das trainierte DQN-Modell.
        """
        if self.model and TORCH_AVAILABLE:
            torch.save(self.model.state_dict(), path)
            print(f"[RL Agent] Model saved to {path}")
        else:
            print("[RL Agent] No model to save or PyTorch not available")
    
    def load_model(self, path: str = "dqn_traffic_model.pth"):
        """
        Lädt ein gespeichertes DQN-Modell.
        """
        if not TORCH_AVAILABLE:
            print("[RL Agent] PyTorch not available, cannot load model")
            return
        
        try:
            if self.model:
                self.model.load_state_dict(torch.load(path))
                self.trained = True
                print(f"[RL Agent] Model loaded from {path}")
            else:
                print("[RL Agent] Model not initialized, cannot load weights")
        except FileNotFoundError:
            print(f"[RL Agent] Model file not found: {path}")
        except Exception as e:
            print(f"[RL Agent] Error loading model: {e}")
