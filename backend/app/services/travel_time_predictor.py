"""
Travel Time Prediction Service
Vorhersagt optimale Startzeitpunkte basierend auf historischen Verkehrsdaten
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import math

from app.services.traffic_api import traffic_client
from app.services.road_network import road_network


class TravelTimePredictor:
    """
    Vorhersagt Reisezeiten und empfiehlt optimale Startzeitpunkte.
    
    MVP: Nutzt vereinfachte Verkehrsmuster + Live-API Daten
    Production: Würde ML-Modelle (LSTM, Prophet) auf historischen Daten trainieren
    """
    
    def __init__(self):
        # Typische Verkehrsmuster (Rush Hour, etc.)
        self.traffic_patterns = {
            # Wochentag: [(Stunde, Delay-Faktor), ...]
            'weekday': [
                (6, 0.3),   # Früh morgens
                (7, 0.7),   # Morgen-Rush Hour
                (8, 0.9),   # Peak Rush Hour
                (9, 0.6),   # Nach Rush Hour
                (10, 0.2),  # Vormittag
                (12, 0.3),  # Mittagszeit
                (17, 0.8),  # Abend-Rush Hour
                (18, 0.9),  # Peak Abend
                (19, 0.5),  # Nach Rush Hour
                (22, 0.1),  # Abend
            ],
            'weekend': [
                (8, 0.1),
                (10, 0.2),
                (12, 0.3),
                (14, 0.4),
                (16, 0.3),
                (18, 0.2),
                (20, 0.1),
            ]
        }
    
    def _get_day_type(self, dt: datetime) -> str:
        """Bestimmt ob Wochentag oder Wochenende."""
        return 'weekend' if dt.weekday() >= 5 else 'weekday'
    
    def _get_hour_delay_factor(self, dt: datetime) -> float:
        """
        Holt Delay-Faktor für eine bestimmte Stunde basierend auf Mustern.
        
        MVP: Interpoliert zwischen definierten Zeitpunkten
        Production: ML-Modell mit echten historischen Daten
        """
        day_type = self._get_day_type(dt)
        pattern = self.traffic_patterns[day_type]
        
        hour = dt.hour
        
        # Finde nächste definierte Zeitpunkte
        prev_point = None
        next_point = None
        
        for i, (h, factor) in enumerate(pattern):
            if h <= hour:
                prev_point = (h, factor)
            if h > hour and next_point is None:
                next_point = (h, factor)
                break
        
        # Falls keine Punkte gefunden, nutze Standardwerte
        if prev_point is None:
            return 0.1
        if next_point is None:
            return prev_point[1]
        
        # Lineare Interpolation
        h1, f1 = prev_point
        h2, f2 = next_point
        
        if h2 == h1:
            return f1
        
        t = (hour - h1) / (h2 - h1)
        return f1 + t * (f2 - f1)
    
    def _add_randomness(self, delay: float) -> float:
        """Fügt realistische Zufallsvariation hinzu."""
        # ±20% Variation
        variance = delay * 0.2
        return max(0, delay + random.uniform(-variance, variance))
    
    def predict_travel_time(
        self, 
        start: str, 
        end: str, 
        departure_time: datetime
    ) -> Dict[str, Any]:
        """
        Vorhersagt Reisezeit für eine spezifische Abfahrtszeit.
        
        Args:
            start: Startort
            end: Zielort
            departure_time: Geplante Abfahrtszeit
        
        Returns:
            Dict mit Vorhersage-Details
        """
        # Hole Basis-Reisezeit
        base_time = road_network.shortest_path_length(start, end)
        
        if base_time is None:
            return {
                'error': 'Route not found',
                'start': start,
                'end': end
            }
        
        # Hole Verkehrsmuster für Zeitpunkt
        pattern_delay = self._get_hour_delay_factor(departure_time)
        pattern_delay = self._add_randomness(pattern_delay)
        
        # Hole aktuelle Live-Daten (falls Abfahrt in naher Zukunft)
        hours_until = (departure_time - datetime.now()).total_seconds() / 3600
        live_delay = 0.0
        
        if 0 <= hours_until <= 2:
            # Nur für nahe Zukunft Live-Daten nutzen
            live_delay = traffic_client.get_live_traffic_delay()
            # Gewichte: 70% Live, 30% Pattern
            final_delay = 0.7 * live_delay + 0.3 * pattern_delay
        else:
            # Für entfernte Zukunft nur Muster
            final_delay = pattern_delay
        
        predicted_time = base_time * (1 + final_delay)
        
        return {
            'start': start,
            'end': end,
            'departure_time': departure_time.isoformat(),
            'base_time_minutes': base_time,
            'predicted_time_minutes': round(predicted_time, 1),
            'delay_factor': round(final_delay, 2),
            'delay_minutes': round(predicted_time - base_time, 1),
            'traffic_level': self._get_traffic_level(final_delay),
            'confidence': 0.8 if hours_until <= 2 else 0.6
        }
    
    def _get_traffic_level(self, delay_factor: float) -> str:
        """Konvertiert Delay-Faktor in lesbare Traffic-Stufe."""
        if delay_factor < 0.2:
            return 'sehr gering'
        elif delay_factor < 0.4:
            return 'gering'
        elif delay_factor < 0.6:
            return 'mittel'
        elif delay_factor < 0.8:
            return 'hoch'
        else:
            return 'sehr hoch'
    
    def find_optimal_departure_time(
        self,
        start: str,
        end: str,
        earliest_departure: Optional[datetime] = None,
        latest_arrival: Optional[datetime] = None,
        hours_window: int = 12
    ) -> Dict[str, Any]:
        """
        Findet optimalen Startzeitpunkt innerhalb eines Zeitfensters.
        
        Args:
            start: Startort
            end: Zielort
            earliest_departure: Früheste mögliche Abfahrt (default: jetzt)
            latest_arrival: Späteste gewünschte Ankunft (optional)
            hours_window: Zeitfenster in Stunden (default: 12h)
        
        Returns:
            Dict mit Empfehlung und Alternativen
        """
        if earliest_departure is None:
            earliest_departure = datetime.now()
        
        # Teste jede Stunde im Zeitfenster
        predictions = []
        
        for hour_offset in range(hours_window):
            test_time = earliest_departure + timedelta(hours=hour_offset)
            
            prediction = self.predict_travel_time(start, end, test_time)
            
            if 'error' not in prediction:
                arrival_time = test_time + timedelta(minutes=prediction['predicted_time_minutes'])
                
                # Prüfe ob Ankunft rechtzeitig
                valid = True
                if latest_arrival and arrival_time > latest_arrival:
                    valid = False
                
                predictions.append({
                    **prediction,
                    'arrival_time': arrival_time.isoformat(),
                    'valid': valid,
                    'hour_offset': hour_offset
                })
        
        if not predictions:
            return {'error': 'No valid predictions found'}
        
        # Finde optimale Zeit (minimale Reisezeit)
        valid_predictions = [p for p in predictions if p.get('valid', True)]
        
        if not valid_predictions:
            valid_predictions = predictions  # Fallback
        
        optimal = min(valid_predictions, key=lambda p: p['predicted_time_minutes'])
        
        # Top 3 Alternativen
        alternatives = sorted(
            valid_predictions, 
            key=lambda p: p['predicted_time_minutes']
        )[1:4]
        
        return {
            'recommendation': optimal,
            'alternatives': alternatives,
            'total_options_analyzed': len(predictions),
            'search_window_hours': hours_window
        }
    
    def get_hourly_forecast(
        self,
        start: str,
        end: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Erstellt stündliche Verkehrsprognose.
        
        Args:
            start: Startort
            end: Zielort
            hours: Anzahl Stunden (default: 24)
        
        Returns:
            Liste von stündlichen Vorhersagen
        """
        now = datetime.now()
        forecast = []
        
        for hour_offset in range(hours):
            time = now + timedelta(hours=hour_offset)
            prediction = self.predict_travel_time(start, end, time)
            
            if 'error' not in prediction:
                forecast.append(prediction)
        
        return forecast


# Global instance
travel_predictor = TravelTimePredictor()
