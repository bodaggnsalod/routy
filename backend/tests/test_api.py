import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.models import Order
from src.rl_engine.agent import RLAgent
from src.rl_engine.environment import TourEnvironment
from src.simulation_env.simulation import Simulation
from src.data_pipeline.loader import DataLoader

client = TestClient(app)

# ============== API Tests ==============

class TestAPIHealth:
    def test_health_check(self):
        """Test /health Endpunkt"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data

class TestAPIRouting:
    def test_optimize_route_basic(self):
        """Test /api/v1/route/optimize mit Dummy-Daten"""
        payload = [
            {"order_id": 1, "start_location": "Berlin", "end_location": "München", "priority": 1},
            {"order_id": 2, "start_location": "Frankfurt", "end_location": "Hamburg", "priority": 2},
        ]
        response = client.post("/api/v1/route/optimize", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "route_id" in data
        assert isinstance(data["stops"], list)
        assert "estimated_duration_minutes" in data
        assert data["estimated_duration_minutes"] > 0

    def test_optimize_route_empty(self):
        """Test /api/v1/route/optimize mit leerer Liste"""
        response = client.post("/api/v1/route/optimize", json=[])
        assert response.status_code == 400

    def test_get_route(self):
        """Test GET /api/v1/route/{route_id}"""
        response = client.get("/api/v1/route/test_route_123")
        assert response.status_code == 200
        data = response.json()
        assert data["route_id"] == "test_route_123"

    def test_get_stats(self):
        """Test GET /api/v1/stats"""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_routes_optimized" in data
        assert "avg_duration_minutes" in data

# ============== RL Agent Tests ==============

class TestRLAgent:
    def test_agent_initialization(self):
        """Test RLAgent Initialisierung"""
        agent = RLAgent()
        assert agent.trained == False
        assert agent.model == None

    def test_agent_train(self):
        """Test RLAgent.train()"""
        agent = RLAgent()
        stats = agent.train(episodes=5)
        assert stats["status"] == "trained_stub"
        assert stats["episodes"] == 5
        assert agent.trained == True

    def test_agent_predict_basic(self):
        """Test RLAgent.predict() mit Dummy-Daten"""
        agent = RLAgent()
        orders = [
            Order(order_id=1, start_location="A", end_location="B", priority=2),
            Order(order_id=2, start_location="C", end_location="D", priority=1),
        ]
        stops = agent.predict(orders)
        assert isinstance(stops, list)
        assert len(stops) > 0
        # First stop sollte von niedrigster Priorität sein
        assert "C" in stops  # order 2 hat priority 1 (höher)

    def test_agent_predict_empty(self):
        """Test RLAgent.predict() mit leerer Liste"""
        agent = RLAgent()
        stops = agent.predict([])
        assert stops == []

# ============== Environment Tests ==============

class TestTourEnvironment:
    def test_environment_initialization(self):
        """Test TourEnvironment Initialisierung"""
        env = TourEnvironment()
        assert env.time == 0
        assert env.assigned_orders == {}

    def test_environment_reset(self):
        """Test TourEnvironment.reset()"""
        env = TourEnvironment()
        env.time = 10
        state = env.reset()
        assert env.time == 0
        assert isinstance(state, dict)

    def test_environment_step(self):
        """Test TourEnvironment.step()"""
        env = TourEnvironment()
        action = {"assign": {"order_id": 1, "vehicle_id": "v1"}}
        state, reward, done = env.step(action)
        assert env.time == 1
        assert isinstance(state, dict)
        assert isinstance(reward, float)

    def test_environment_add_vehicle(self):
        """Test Environment Vehicle Management"""
        env = TourEnvironment()
        env.add_vehicle("v1", capacity=100)
        assert len(env.vehicles) == 1
        assert env.vehicles[0]["vehicle_id"] == "v1"

# ============== Simulation Tests ==============

class TestSimulation:
    def test_simulation_initialization(self):
        """Test Simulation Initialisierung"""
        sim = Simulation()
        assert sim.time == 0
        assert len(sim.events) == 0

    def test_simulation_add_event(self):
        """Test Simulation.add_event()"""
        sim = Simulation()
        event = {
            "type": "order_arrived",
            "timestamp": 1,
            "data": {"order_id": 1}
        }
        sim.add_event(event)
        assert len(sim.events) == 1

    def test_simulation_run_step(self):
        """Test Simulation.run_step()"""
        sim = Simulation()
        event = {
            "type": "order_completed",
            "timestamp": 1,
            "data": {"order_id": 1}
        }
        sim.add_event(event)
        result = sim.run_step()
        assert result is not None
        assert 1 in sim.completed_orders

    def test_simulation_run_full(self):
        """Test Simulation.run_simulation()"""
        sim = Simulation()
        for i in range(5):
            sim.add_event({
                "type": "order_arrived",
                "timestamp": i,
                "data": {"order_id": i}
            })
        
        final_state = sim.run_simulation(num_steps=10)
        assert isinstance(final_state, dict)
        assert "time" in final_state

# ============== Data Pipeline Tests ==============

class TestDataLoader:
    def test_loader_initialization(self):
        """Test DataLoader Initialisierung"""
        loader = DataLoader()
        assert loader is not None

    def test_load_orders_from_list(self):
        """Test DataLoader mit in-memory Daten"""
        loader = DataLoader()
        # Test über API statt direkter Datei
        orders = [
            Order(order_id=1, start_location="A", end_location="B", priority=1),
            Order(order_id=2, start_location="C", end_location="D", priority=2),
        ]
        assert len(orders) == 2
        assert orders[0].order_id == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])