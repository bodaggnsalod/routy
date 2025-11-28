# Routy: KI-Tourenplanung

Ein KI-gestütztes System zur dynamischen Tourenplanung für Logistikunternehmen.

## 🔧 Use-case
Ein Disponent im Logistikunternehmen soll den optimalen Startzeitpunkt für eine zu planende Route durch die Anwendung vorgeschlagen bekommen. Der Vorschlag soll durch historische Verkehrsdaten (Baustellen, Stau, !Unfäll, Verkehrsdichte) der zu fahrenden Routen erstellt werden.

Ziel: Vorhersage der zu erwartenden Fahrzeit/Verkehrslage für jeden Zeitpunkt in der Zukunft.

Lösung: Travel-Time Prediction:
-   Time-Series Forecasting (Vorhersage künftiger Verkehrsbedingungen)
-   Predictive Routing / Travel Time Prediction
-   Optimization/Recommendation (Startzeitpunkt optimieren)



## 📁 Projektstruktur

```
routy/
├── backend/           # FastAPI Backend
│   ├── app/          # Python Package
│   │   ├── api/      # API Endpoints (versioned)
│   │   ├── core/     # Config & Core
│   │   ├── models/   # Pydantic Schemas
│   │   └── services/ # Business Logic
│   └── tests/        # Backend Tests
├── frontend/         # React + Vite Frontend
└── docs/            # Dokumentation
```

## 🚀 Schnellstart

### Mit Docker Compose (empfohlen)

```bash
docker-compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### Manuell

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Tests

**Backend:**
```bash
cd backend
pytest -v
```

**Frontend:**
```bash
cd frontend
npm run test
```

## 📊 API Endpunkte

### Core Features
- `GET /health` - Health Check
- `POST /api/v1/route/optimize` - Route optimieren
- `GET /api/v1/stats` - Statistiken

### Travel Time Prediction (Haupt-Use-Case)
- `GET /api/v1/travel-time/predict` - Vorhersage Reisezeit für bestimmten Zeitpunkt
- `GET /api/v1/travel-time/optimal-departure` - Findet optimalen Startzeitpunkt
- `GET /api/v1/travel-time/forecast` - Stündliche Verkehrsprognose

Vollständige API-Dokumentation: http://localhost:8000/docs

Detaillierte Feature-Docs: [docs/TRAVEL_TIME_PREDICTION.md](docs/TRAVEL_TIME_PREDICTION.md)

## 🔧 Konfiguration

Backend-Config in `backend/app/core/config.py` oder via `.env`:

```env
DEBUG=True
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
```

## 📝 Entwicklung

- Code Style: Black + isort
- Tests: pytest (Backend), Vitest (Frontend)
- API: OpenAPI 3.0

## 🚀 Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

**Version:** 1.0.0  
**Status:** 🟢 Active Development