"""
Graph-basiertes Routing-Netzwerk für RL-Agent
"""
import networkx as nx
from typing import Dict, List, Tuple, Optional


class RoadNetwork:
    """
    Straßennetzwerk-Repräsentation mit NetworkX.
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self._build_default_network()
    
    def _build_default_network(self):
        """
        Erstellt ein Standard-Netzwerk (MVP: synthetisches Beispiel).
        
        In Production würde dies aus echten Kartendaten geladen.
        """
        # Beispiel-Knoten (Städte/Orte)
        nodes = ['Berlin', 'Hamburg', 'München', 'Köln', 'Frankfurt', 
                 'Stuttgart', 'Düsseldorf', 'Dortmund', 'Leipzig']
        
        for node in nodes:
            self.graph.add_node(node)
        
        # Beispiel-Kanten mit Basis-Reisezeiten in Minuten
        edges = [
            ('Berlin', 'Hamburg', 180),
            ('Berlin', 'Leipzig', 120),
            ('Hamburg', 'Düsseldorf', 240),
            ('München', 'Stuttgart', 150),
            ('München', 'Frankfurt', 240),
            ('Köln', 'Düsseldorf', 30),
            ('Köln', 'Frankfurt', 120),
            ('Frankfurt', 'Stuttgart', 90),
            ('Frankfurt', 'Leipzig', 240),
            ('Dortmund', 'Düsseldorf', 45),
            ('Dortmund', 'Köln', 60),
            ('Leipzig', 'Dresden', 90),
        ]
        
        for u, v, weight in edges:
            if u in nodes and v in nodes:
                self.graph.add_edge(u, v, weight=weight, base_weight=weight)
    
    def add_location(self, location: str):
        """Füge einen neuen Standort hinzu."""
        if not self.graph.has_node(location):
            self.graph.add_node(location)
    
    def add_route(self, start: str, end: str, travel_time: int):
        """
        Füge eine Route zwischen zwei Standorten hinzu.
        
        Args:
            start: Startort
            end: Zielort
            travel_time: Reisezeit in Minuten
        """
        self.add_location(start)
        self.add_location(end)
        self.graph.add_edge(start, end, weight=travel_time, base_weight=travel_time)
    
    def update_traffic(self, start: str, end: str, delay_factor: float):
        """
        Aktualisiere Kantengewicht basierend auf Verkehrslage.
        
        Args:
            start: Startort
            end: Zielort
            delay_factor: Verzögerungsfaktor (0.0 - 1.0)
        """
        if self.graph.has_edge(start, end):
            base = self.graph[start][end]['base_weight']
            new_weight = base * (1 + delay_factor)
            self.graph[start][end]['weight'] = new_weight
    
    def shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        Berechne kürzesten Pfad zwischen zwei Orten.
        
        Returns:
            Liste von Orten auf dem kürzesten Pfad oder None
        """
        try:
            return nx.shortest_path(self.graph, start, end, weight='weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def shortest_path_length(self, start: str, end: str) -> Optional[float]:
        """
        Berechne Länge des kürzesten Pfads.
        
        Returns:
            Gesamte Reisezeit in Minuten oder None
        """
        try:
            return nx.shortest_path_length(self.graph, start, end, weight='weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def get_neighbors(self, location: str) -> List[str]:
        """
        Gibt alle direkt erreichbaren Nachbarn zurück.
        """
        if self.graph.has_node(location):
            return list(self.graph.neighbors(location))
        return []
    
    def get_all_locations(self) -> List[str]:
        """Gibt alle Standorte im Netzwerk zurück."""
        return list(self.graph.nodes())
    
    def has_location(self, location: str) -> bool:
        """Prüft ob ein Standort existiert."""
        return self.graph.has_node(location)
    
    def get_edge_weight(self, start: str, end: str) -> Optional[float]:
        """
        Gibt das Gewicht (Reisezeit) einer Kante zurück.
        """
        if self.graph.has_edge(start, end):
            return self.graph[start][end]['weight']
        return None
    
    def get_all_edges(self) -> List[Dict[str, any]]:
        """
        Gibt alle Kanten im Netzwerk zurück.
        
        Returns:
            Liste von Dicts mit start, end, weight, base_weight
        """
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                'start': u,
                'end': v,
                'weight': data.get('weight', 0),
                'base_weight': data.get('base_weight', 0),
                'delay_factor': (data.get('weight', 0) / data.get('base_weight', 1)) - 1 if data.get('base_weight', 1) > 0 else 0
            })
        return edges
    
    def get_congested_routes(self, threshold: float = 0.5) -> List[Dict[str, any]]:
        """
        Gibt alle Routen zurück, deren Delay-Faktor über dem Threshold liegt.
        
        Args:
            threshold: Minimaler Delay-Faktor (default: 0.5)
        
        Returns:
            Liste von Routen mit hohem Traffic
        """
        congested = []
        for edge in self.get_all_edges():
            if edge['delay_factor'] >= threshold:
                congested.append(edge)
        return congested


# Global instance
road_network = RoadNetwork()
