import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI TestClient fixture"""
    return TestClient(app)

@pytest.fixture
def sample_orders():
    """Sample orders for testing"""
    return [
        {
            "order_id": 1,
            "start_location": "Berlin",
            "end_location": "München",
            "priority": 1
        },
        {
            "order_id": 2,
            "start_location": "Frankfurt",
            "end_location": "Hamburg",
            "priority": 2
        },
        {
            "order_id": 3,
            "start_location": "Köln",
            "end_location": "Stuttgart",
            "priority": 1
        }
    ]

@pytest.fixture
def sample_vehicles():
    """Sample vehicles for testing"""
    return [
        {"vehicle_id": "v1", "capacity": 100},
        {"vehicle_id": "v2", "capacity": 150}
    ]
