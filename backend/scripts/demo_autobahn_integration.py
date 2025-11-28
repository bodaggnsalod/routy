"""
Beispiel-Script: Verwendung des integrierten RL-Agents mit Autobahn API

Dieses Script zeigt wie:
1. Live-Traffic-Daten von der Autobahn API geholt werden
2. Das Straßennetzwerk mit Traffic-Delays aktualisiert wird
3. Der DQN-Agent trainiert wird (wenn PyTorch verfügbar)
4. Routen mit Traffic-Berücksichtigung optimiert werden
"""

from app.models.schemas import Order
from app.services.rl_agent import RLAgent
from app.services.environment import TourEnvironment
from app.services.traffic_api import traffic_client
from app.services.road_network import road_network


def demo_traffic_api():
    """Demonstriere Live-Traffic-Abfrage"""
    print("\n=== Traffic API Demo ===")
    
    # Hole Live-Traffic-Delay
    delay_factor = traffic_client.get_live_traffic_delay()
    print(f"Aktueller Traffic Delay Factor: {delay_factor:.2f}")
    
    # Hole spezifische Route-Info
    route_info = traffic_client.get_traffic_info_for_route("Berlin", "München")
    print(f"\nRoute Berlin -> München:")
    print(f"  Status: {route_info['traffic_status']}")
    print(f"  Geschätzte Verzögerung: {route_info['estimated_delay_minutes']} Minuten")


def demo_road_network():
    """Demonstriere Straßennetzwerk-Routing"""
    print("\n=== Road Network Demo ===")
    
    # Zeige verfügbare Standorte
    locations = road_network.get_all_locations()
    print(f"Verfügbare Standorte: {locations}")
    
    # Berechne kürzesten Pfad
    start = "Berlin"
    end = "München"
    
    if road_network.has_location(start) and road_network.has_location(end):
        path = road_network.shortest_path(start, end)
        distance = road_network.shortest_path_length(start, end)
        
        print(f"\nKürzester Pfad {start} -> {end}:")
        print(f"  Route: {' -> '.join(path) if path else 'Nicht gefunden'}")
        print(f"  Distanz: {distance:.0f} Minuten" if distance else "N/A")
        
        # Aktualisiere mit Traffic
        delay = traffic_client.get_live_traffic_delay()
        road_network.update_traffic(start, path[1] if path and len(path) > 1 else end, delay)
        
        new_distance = road_network.shortest_path_length(start, end)
        print(f"  Mit Traffic: {new_distance:.0f} Minuten" if new_distance else "N/A")


def demo_rl_agent():
    """Demonstriere RL-Agent Nutzung"""
    print("\n=== RL Agent Demo ===")
    
    # Erstelle Test-Orders
    orders = [
        Order(
            order_id=1,
            start_location="Berlin",
            end_location="Hamburg",
            priority=1
        ),
        Order(
            order_id=2,
            start_location="Hamburg",
            end_location="München",
            priority=2
        ),
        Order(
            order_id=3,
            start_location="München",
            end_location="Frankfurt",
            priority=1
        )
    ]
    
    # Initialisiere Agent
    agent = RLAgent()
    print(f"Agent Modus: {'DQN' if agent.use_dqn else 'Fallback'}")
    
    # Training (optional, nur wenn Environment bereitgestellt wird)
    env = TourEnvironment(orders=orders, max_time_steps=100)
    env.add_vehicle("truck_1", capacity=200)
    
    training_stats = agent.train(environment=env, episodes=10)
    print(f"\nTraining abgeschlossen:")
    print(f"  Status: {training_stats['status']}")
    print(f"  Durchschnittlicher Reward: {training_stats['avg_reward']:.2f}")
    
    # Vorhersage mit Traffic-Integration
    optimized_route = agent.predict(orders)
    print(f"\nOptimierte Route (mit Live-Traffic):")
    print(f"  Stopps: {' -> '.join(optimized_route)}")
    print(f"  Anzahl Stopps: {len(optimized_route)}")


def demo_full_integration():
    """Vollständige Integration aller Komponenten"""
    print("\n=== Vollständige Integration ===")
    
    # 1. Erstelle Orders
    orders = [
        Order(order_id=1, start_location="Berlin", end_location="Leipzig", priority=1),
        Order(order_id=2, start_location="Leipzig", end_location="Frankfurt", priority=2),
        Order(order_id=3, start_location="Frankfurt", end_location="Stuttgart", priority=1),
    ]
    
    # 2. Hole Live-Traffic
    print("\n1. Hole Live-Traffic-Daten...")
    traffic_info = traffic_client.get_traffic_info_for_route("Berlin", "Stuttgart")
    print(f"   Traffic Status: {traffic_info['traffic_status']}")
    
    # 3. Erstelle Environment
    print("\n2. Erstelle Simulationsumgebung...")
    env = TourEnvironment(orders=orders)
    env.add_vehicle("truck_1")
    env.add_vehicle("truck_2")
    
    # 4. Trainiere Agent
    print("\n3. Trainiere RL-Agent...")
    agent = RLAgent()
    stats = agent.train(environment=env, episodes=5)
    print(f"   Training {stats['status']}")
    
    # 5. Optimiere Route mit Traffic
    print("\n4. Optimiere Route mit Live-Traffic...")
    route = agent.predict(orders)
    print(f"   Optimierte Route: {' -> '.join(route)}")
    
    # 6. Berechne finale Distanz
    if len(route) > 1:
        total_time = 0
        for i in range(len(route) - 1):
            distance = road_network.shortest_path_length(route[i], route[i+1])
            if distance:
                total_time += distance
        print(f"   Geschätzte Gesamtzeit: {total_time:.0f} Minuten")


if __name__ == "__main__":
    print("=" * 60)
    print("Routy: Autobahn API Integration Demo")
    print("=" * 60)
    
    # Führe alle Demos aus
    demo_traffic_api()
    demo_road_network()
    demo_rl_agent()
    demo_full_integration()
    
    print("\n" + "=" * 60)
    print("Demo abgeschlossen!")
    print("=" * 60)
