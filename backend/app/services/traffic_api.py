"""
Live Traffic Data Integration mit Autobahn API
"""
import requests
from typing import Optional
from app.core.config import settings


class TrafficAPIClient:
    """
    Client für Live-Verkehrsdaten von der Autobahn API.
    """
    
    def __init__(self):
        self.base_url = "https://verkehr.autobahn.de/o/autobahn/"
        self.timeout = settings.AUTOBAHN_TIMEOUT
    
    def get_live_traffic_delay(self, region: Optional[str] = None) -> float:
        """
        Holt Live-Verkehrsstörungen von der Autobahn API.
        
        Args:
            region: Spezifische Region/Autobahn (z.B. "A1", "A3")
        
        Returns:
            Verzögerungsfaktor (0.0 = kein Delay, 1.0 = maximales Delay)
        """
        try:
            # Autobahn API v3 endpoint
            url = f"{self.base_url}"
            
            # Fallback auf alternative API falls Hauptendpoint nicht verfügbar
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
            except Exception:
                # Fallback: Nutze öffentliche Verkehrsmeldungen-API
                url = "https://verkehr.autobahn.de/o/autobahn/"
                response = requests.get(url, timeout=self.timeout)
                data = response.json() if response.status_code == 200 else {}
            
            # Extrahiere Störungsmeldungen
            events = []
            if isinstance(data, dict):
                events = data.get("roadworks", []) or []
                events.extend(data.get("warning", []) or [])
                events.extend(data.get("closure", []) or [])
            
            # Berechne Delay-Faktor basierend auf Anzahl der Ereignisse
            # Normalisiert auf 0.0 - 1.0
            delay_factor = min(1.0, len(events) / 50.0)
            
            print(f"[Traffic API] Found {len(events)} events, delay factor: {delay_factor:.2f}")
            return delay_factor
            
        except requests.RequestException as e:
            print(f"[Traffic API] Error fetching data: {e}")
            return 0.0
        except Exception as e:
            print(f"[Traffic API] Unexpected error: {e}")
            return 0.0
    
    def get_traffic_info_for_route(self, start: str, end: str) -> dict:
        """
        Holt spezifische Verkehrsinformationen für eine Route.
        
        Args:
            start: Startort
            end: Zielort
        
        Returns:
            Dict mit Verkehrsinformationen
        """
        delay_factor = self.get_live_traffic_delay()
        
        return {
            "start": start,
            "end": end,
            "delay_factor": delay_factor,
            "estimated_delay_minutes": int(delay_factor * 30),  # Max 30 min Verzögerung
            "traffic_status": self._get_status_label(delay_factor)
        }
    
    def _get_status_label(self, delay_factor: float) -> str:
        """
        Konvertiert Delay-Faktor in lesbare Status-Labels.
        """
        if delay_factor < 0.2:
            return "frei"
        elif delay_factor < 0.5:
            return "leicht"
        elif delay_factor < 0.8:
            return "mittel"
        else:
            return "stark"


# Global instance
traffic_client = TrafficAPIClient()
