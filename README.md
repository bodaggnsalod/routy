# Routy: KI-Tourenplanung MVP

Dieses Dokument beschreibt das Projekt "Routy", das ein KI-basiertes System zur dynamischen Tourenplanung für Logistikunternehmen entwickelt.

## 📌 Projektidee
**Dynamische KI-Tourenplanung für Logistikunternehmen**

## 🎯 Projektziel
Ziel ist es, ein KI-gestütztes System zu entwickeln, das Transport- und Lieferfahrzeuge automatisch und effizient plant. Das System reagiert in Echtzeit auf Verkehr, neue Aufträge und Verzögerungen, um die bestmögliche Route für jeden Auftrag zu generieren.

## 🚀 MVP-Funktionen

### Aktive Features
- ✅ Basis-API mit FastAPI
- ✅ Route-Optimierung (naive Sortierung nach Priorität)
- ✅ RL-Agent Skeleton
- ✅ Simulations-Umgebung
- ✅ Data-Loader (CSV/JSON)
- ✅ Unit Tests
- ✅ Docker-ready

### Kommende Features (Phase 2+)
- 🔄 Echtes RL-Training
- 🔄 Live-Traffic-Integration
- 🔄 Dashboard/Frontend
- 🔄 Datenbank-Integration
- 🔄 WebSocket-Support

## 📦 Technische KOmponenten (TechStack)

| Component     | Technology                    |
|-------------  |-------------------------------|
| **Backend**   | FastAPI, Python 3.10+         |
| **API**       | REST + OpenAPI                |
| **RL-Engine** | NumPy, Scikit-Learn (Phase 2) |
| **Database**  | SQLite / PostgreSQL (Phase 2) |
| **Testing**   | Pytest                        |
| **DevOps**    | Docker, Docker Compose        |

## 🔧 Installation & Setup

### Voraussetzungen
- Python 3.10+
- pip / venv

### Schritt 1: Repository clonen
```bash
cd /home/<user>/ITM-Gruppe1
git clone <repo-url> routy
cd routy
```

### Schritt 2: Virtual Environment erstellen
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder: .venv\Scripts\activate  # Windows
```

### Schritt 3: Dependencies installieren
```bash
pip install -r requirements.txt
```

## 🚀 Schnellstart
Die Schritte von **🔧 Installation & Setup** müssen erfolgreich vorher abgeschlossen werden.

### 1. Backend starten
```bash
uvicorn src.backend.main:app --reload
```

Server läuft unter: `http://127.0.0.1:8000`

### 2. API testen

**Health-Check:**
```bash
curl http://127.0.0.1:8000/health
```

**Route optimieren:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/route/optimize \
  -H "Content-Type: application/json" \
  -d '[
    {"order_id": 1, "start_location": "Berlin", "end_location": "München", "priority": 1},
    {"order_id": 2, "start_location": "Frankfurt", "end_location": "Hamburg", "priority": 2}
  ]'
```

### 3. Tests ausführen
```bash
pytest -v
```

### 4. API-Docs öffnen
- **OpenAPI (Swagger):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## 📋 API-Endpunkte

### Monitoring
- `GET /health` — Health-Check

### Routing
- `POST /api/v1/route/optimize` — Route optimieren
- `GET /api/v1/route/{route_id}` — Route-Details
- `GET /api/v1/stats` — Statistiken
- `POST /api/v1/data/upload` — Daten hochladen

## 📁 Projektstruktur

```
routy/
├── config/              # Konfigurationsdateien
│   └── settings.yaml   # API & Logging Config
├── src/
│   ├── api/            # FastAPI Endpunkte
│   ├── backend/        # Main App Entry Point
│   ├── models.py       # Pydantic Models
│   ├── data_pipeline/  # CSV/JSON Loader
│   ├── rl_engine/      # RL-Agent & Environment
│   ├── simulation_env/ # Simulations-Umgebung
│   └── utils/          # Utilities (Config Loading)
├── tests/              # Unit & Integration Tests
├── requirements.txt    # Python Dependencies
├── README.md          # Diese Datei
└── .env.example       # Environment Variable Template
```

## 🧠 Komponenten-Übersicht

### RLAgent
- **Funktion:** Optimiert Routen basierend auf Aufträgen
- **MVP-Logik:** Sortiert Aufträge nach Priorität
- **Erweiterung (Phase 2):** Echtes RL-Modell mit Q-Learning

### TourEnvironment
- **Funktion:** Simulations-Umgebung für RL-Training
- **MVP:** State-Tracking und Reward-Berechnung
- **Erweiterung:** Verkehrs-Simulation, Multi-Vehicle-Szenen

### Simulation
- **Funktion:** Event-basierte Simulation
- **MVP:** Event-Processing und State Management
- **Erweiterung:** Realistische Verkehr- und Verzögerungs-Szenarien

### DataLoader
- **Funktion:** Lädt Aufträge und Fahrzeuge aus CSV/JSON
- **MVP:** Basis CSV- und JSON-Support
- **Erweiterung:** Datenbank-Integration, Streaming

## 🧪 Tests ausführen

### Alle Tests
```bash
pytest
```

### Mit Verbose Output
```bash
pytest -v
```

### Nur spezifische Test-Klasse
```bash
pytest tests/test_api.py::TestAPIHealth -v
```

### Mit Coverage
```bash
pytest --cov=src tests/
```

## 🐳 Docker Setup

### Image bauen
```bash
docker build -t routy:latest .
```

### Container starten
```bash
docker run -p 8000:8000 routy:latest
```

## 📊 Monitoring & Debugging

### Logs anschauen
```bash
# Lokale Logs
journalctl -u routy -f

# Docker Logs
docker logs -f <container_id>
```

### Debug-Mode aktivieren
```bash
export DEBUG=True
uvicorn src.backend.main:app --reload --log-level debug
```

## 🔐 Sicherheit

- `.env.example` kopieren zu `.env` vor Production
- `API_KEY` in `.env` setzen
- CORS ist aktuell offen (anpassen für Production)
- Rate Limiting (Phase 2)
- Authentication/Authorization (Phase 2)

## 🚀 Next Steps (Phase 2)

1. **Echtes RL-Training**
   - Integration von TensorFlow/PyTorch
   - Q-Learning Implementation
   - Multi-Agent Coordination

2. **Live-Traffic-Integration**
   - HERE Maps API
   - TomTom Traffic API
   - Real-Time ETA Calculation

3. **Frontend Dashboard**
   - React/Next.js
   - Real-Time Route Visualization
   - Dispatcher Interface

4. **Database Integration**
   - PostgreSQL Setup
   - SQLAlchemy ORM
   - Data Persistence

5. **Advanced Features**
   - Multi-Vehicle Optimization
   - Vehicle Type Constraints
   - Time Window Constraints
   - Eco-Mode (CO₂ Optimierung)

## 📝 Entwickler-Guide

### Neue API-Endpunkte hinzufügen
1. Modell in `src/models.py` definieren
2. Endpunkt in `src/api/endpoints.py` implementieren
3. Test in `tests/test_api.py` schreiben
4. In `src/backend/main.py` registrieren

### Code Style
- PEP 8 + Black Formatter
- Type Hints verwenden
- Docstrings für alle Funktionen

### Commit-Messages
```
feat: Add new route optimization algorithm
fix: Correct priority sorting bug
docs: Update API documentation
test: Add integration tests for route endpoint
```

## 📞 Support & Kontakt

Für Fragen oder Probleme:
- 📧 Email: dev@routy.io
- 🐛 Issues: GitHub Issues
- 💬 Discussion: GitHub Discussions

## 📄 Lizenz

MIT License — siehe LICENSE file

---

**Version:** 1.0 MVP  
**Letztes Update:** 2025-11-21  
**Status:** 🟢 In Development