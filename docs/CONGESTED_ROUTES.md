# Congested Routes Feature

## 🚦 Übersicht

Dieses Feature zeigt Routen an, die einen hohen Traffic-Delay-Faktor aufweisen (standardmäßig ≥ 0.5).

## 📡 Backend API

### 1. Überlastete Routen abrufen
```http
GET /api/v1/network/congested?threshold=0.5
```

**Response:**
```json
{
  "threshold": 0.5,
  "congested_routes": [
    {
      "start": "Berlin",
      "end": "Hamburg",
      "weight": 324,
      "base_weight": 180,
      "delay_factor": 0.8
    }
  ],
  "count": 1
}
```

### 2. Traffic simulieren (für Demo)
```http
POST /api/v1/network/simulate-traffic
```

Generiert zufällige Delays auf 2-3 Routen für Demo-Zwecke.

**Response:**
```json
{
  "message": "Traffic simulated",
  "updated_routes": [
    {
      "route": "Berlin ↔ Hamburg",
      "delay_factor": 0.73
    }
  ],
  "count": 2
}
```

## 🎨 Frontend Komponente

Die `AutobahnDemo` Komponente zeigt nun einen 5. Test-Block:

**"5️⃣ Routen mit hohem Traffic"**

- Zeigt Anzahl der überlasteten Routen
- Listet jede Route mit:
  - Start ↔ End
  - Normale Reisezeit
  - Reisezeit mit Traffic
  - Delay in Prozent (Badge)
- Grüne Success-Message wenn keine überlasteten Routen

## 🔧 Technische Details

### Backend Services

**`road_network.py`** - Neue Methoden:
- `get_all_edges()` - Gibt alle Kanten mit Delay-Faktoren zurück
- `get_congested_routes(threshold)` - Filtert Routen nach Delay-Faktor

### Berechnung Delay-Faktor

```python
delay_factor = (current_weight / base_weight) - 1
```

Beispiel:
- Base: 180 min
- Mit Traffic: 324 min
- Delay-Faktor: (324 / 180) - 1 = 0.8 = 80% Verzögerung

## 🚀 Verwendung

### Im Frontend
1. Öffne http://localhost:5173
2. Klicke "Autobahn API Demo starten"
3. Klicke "Demo starten"
4. Scrolle zu "5️⃣ Routen mit hohem Traffic"

### Über API (cURL)
```bash
# Traffic simulieren
curl -X POST http://localhost:8000/api/v1/network/simulate-traffic

# Überlastete Routen abrufen
curl http://localhost:8000/api/v1/network/congested?threshold=0.5
```

## 💡 Anwendungsfälle

1. **Echtzeit-Monitoring**: Zeige Fahrern welche Routen zu meiden sind
2. **Route-Optimierung**: Bevorzuge Routen mit niedrigem Delay-Faktor
3. **Alerts**: Benachrichtige bei plötzlichem Traffic-Anstieg
4. **Statistiken**: Analysiere Traffic-Muster über Zeit

## 🔄 Integration mit Live-Traffic

Der Delay-Faktor wird automatisch aktualisiert wenn:
- `traffic_api.get_live_traffic_delay()` aufgerufen wird
- `road_network.update_traffic()` ausgeführt wird
- Routes mit `agent.predict()` optimiert werden

## 📊 Beispiel-Output

```
Überlastete Routen (Delay >= 0.5):

🚗 Berlin ↔ Leipzig
   Normal: 120 min → Mit Traffic: 221 min
   [+84%]

🚗 Köln ↔ Frankfurt  
   Normal: 120 min → Mit Traffic: 186 min
   [+55%]

🚗 München ↔ Stuttgart
   Normal: 150 min → Mit Traffic: 240 min
   [+60%]
```

## ✅ Testing

```python
# Unit Test
from app.services.road_network import road_network

road_network.update_traffic('Berlin', 'Hamburg', 0.7)
congested = road_network.get_congested_routes(0.5)
assert len(congested) > 0
```

```bash
# API Test
pytest tests/test_api.py -k congested -v
```
