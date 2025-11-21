import csv
import json
from typing import List, Union
from pathlib import Path
from src.models import Order, Vehicle

class DataLoader:
    """
    Lädt Daten aus CSV und JSON Dateien.
    
    Unterstützt:
    - Order-Daten (CSV/JSON)
    - Vehicle-Daten (CSV/JSON)
    """
    
    def __init__(self):
        pass

    def load_orders(self, file_path: str) -> List[Order]:
        """
        Lade Aufträge aus CSV oder JSON.
        
        Args:
            file_path: Pfad zur Datei (CSV oder JSON)
        
        Returns:
            Liste von Order-Objekten
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == ".csv":
            return self._load_orders_csv(file_path)
        elif file_path.suffix.lower() == ".json":
            return self._load_orders_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _load_orders_csv(self, file_path: Path) -> List[Order]:
        """
        Lade Orders aus CSV-Datei.
        """
        orders: List[Order] = []
        
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        order = Order(
                            order_id=int(row.get("order_id", 0) or row.get("id", 0)),
                            start_location=row.get("start_location") or row.get("start", ""),
                            end_location=row.get("end_location") or row.get("end", ""),
                            priority=int(row.get("priority", 1))
                        )
                        orders.append(order)
                    except (ValueError, KeyError):
                        # Skip malformed rows
                        continue
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return orders

    def _load_orders_json(self, file_path: Path) -> List[Order]:
        """
        Lade Orders aus JSON-Datei.
        """
        orders: List[Order] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                
                # Handle both array and object with 'orders' key
                orders_data = data if isinstance(data, list) else data.get("orders", [])
                
                for item in orders_data:
                    try:
                        order = Order(
                            order_id=int(item.get("order_id", 0) or item.get("id", 0)),
                            start_location=item.get("start_location") or item.get("start", ""),
                            end_location=item.get("end_location") or item.get("end", ""),
                            priority=int(item.get("priority", 1))
                        )
                        orders.append(order)
                    except (ValueError, KeyError):
                        continue
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return orders

    def load_vehicles(self, file_path: str) -> List[Vehicle]:
        """
        Lade Fahrzeuge aus CSV oder JSON.
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            Liste von Vehicle-Objekten
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == ".csv":
            return self._load_vehicles_csv(file_path)
        elif file_path.suffix.lower() == ".json":
            return self._load_vehicles_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _load_vehicles_csv(self, file_path: Path) -> List[Vehicle]:
        """Lade Fahrzeuge aus CSV."""
        vehicles: List[Vehicle] = []
        
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        vehicle = Vehicle(
                            vehicle_id=row.get("vehicle_id", ""),
                            capacity=int(row.get("capacity", 100))
                        )
                        vehicles.append(vehicle)
                    except ValueError:
                        continue
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return vehicles

    def _load_vehicles_json(self, file_path: Path) -> List[Vehicle]:
        """Lade Fahrzeuge aus JSON."""
        vehicles: List[Vehicle] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                
                vehicles_data = data if isinstance(data, list) else data.get("vehicles", [])
                
                for item in vehicles_data:
                    try:
                        vehicle = Vehicle(
                            vehicle_id=item.get("vehicle_id", ""),
                            capacity=int(item.get("capacity", 100))
                        )
                        vehicles.append(vehicle)
                    except ValueError:
                        continue
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return vehicles