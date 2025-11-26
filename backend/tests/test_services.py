import pytest
from app.services.rl_agent import RLAgent
from app.services.environment import TourEnvironment
from app.services.simulation import Simulation
from app.services.data_loader import DataLoader
from app.models.schemas import Order

class TestRLAgent:
    def test_agent_initialization(self):
        """Test RLAgent initialization"""
        agent = RLAgent()
        assert agent.trained == False
        assert agent.model == None
        assert len(agent.training_history) == 0

    def test_agent_train(self):
        """Test RLAgent training"""
        agent = RLAgent()
        stats = agent.train(episodes=5, learning_rate=0.01)
        assert stats["status"] == "trained_stub"
        assert stats["episodes"] == 5
        assert agent.trained == True
        assert len(agent.training_history) == 1

    def test_agent_predict_basic(self):
        """Test RLAgent prediction with orders"""
        agent = RLAgent()
        orders = [
            Order(order_id=1, start_location="A", end_location="B", priority=2),
            Order(order_id=2, start_location="C", end_location="D", priority=1),
        ]
        stops = agent.predict(orders)
        assert isinstance(stops, list)
        assert len(stops) > 0
        # Priority 1 sollte zuerst kommen
        assert "C" in stops

    def test_agent_predict_empty(self):
        """Test RLAgent prediction with empty list"""
        agent = RLAgent()
        stops = agent.predict([])
        assert stops == []

class TestTourEnvironment:
    def test_environment_initialization(self):
        """Test TourEnvironment initialization"""
        env = TourEnvironment()
        assert env.time == 0
        assert len(env.assigned_orders) == 0
        assert len(env.vehicles) == 0

    def test_environment_reset(self):
        """Test environment reset"""
        env = TourEnvironment()
        env.time = 10
        env.total_reward = 50.0
        state = env.reset()
        assert env.time == 0
        assert env.total_reward == 0.0
        assert isinstance(state, dict)

    def test_environment_step(self):
        """Test environment step"""
        env = TourEnvironment()
        action = {"assign": {"order_id": 1, "vehicle_id": "v1"}}
        state, reward, done = env.step(action)
        assert env.time == 1
        assert isinstance(state, dict)
        assert isinstance(reward, float)
        assert isinstance(done, bool)

    def test_environment_add_vehicle(self):
        """Test adding vehicle to environment"""
        env = TourEnvironment()
        env.add_vehicle("v1", capacity=100)
        assert len(env.vehicles) == 1
        assert env.vehicles[0]["vehicle_id"] == "v1"
        assert env.vehicles[0]["capacity"] == 100

class TestSimulation:
    def test_simulation_initialization(self):
        """Test Simulation initialization"""
        sim = Simulation()
        assert sim.time == 0
        assert len(sim.events) == 0

    def test_simulation_add_event(self):
        """Test adding event to simulation"""
        sim = Simulation()
        event = {
            "type": "order_arrived",
            "timestamp": 1,
            "data": {"order_id": 1}
        }
        sim.add_event(event)
        assert len(sim.events) == 1

    def test_simulation_run_step(self):
        """Test running simulation step"""
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
        """Test running full simulation"""
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

    def test_simulation_reset(self):
        """Test simulation reset"""
        sim = Simulation()
        sim.time = 50
        sim.add_event({"type": "test", "timestamp": 1})
        sim.reset()
        assert sim.time == 0
        assert len(sim.events) == 0

class TestDataLoader:
    def test_loader_initialization(self):
        """Test DataLoader initialization"""
        loader = DataLoader()
        assert loader is not None

    def test_unsupported_format(self):
        """Test loading with unsupported format"""
        loader = DataLoader()
        with pytest.raises(ValueError):
            loader.load_orders("test.xml")
