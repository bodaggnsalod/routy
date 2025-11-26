# Routy: KI-Tourenplanung MVP

Ein KI-gestütztes System zur dynamischen Tourenplanung für Logistikunternehmen.

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

- `GET /health` - Health Check
- `POST /api/v1/route/optimize` - Route optimieren
- `GET /api/v1/stats` - Statistiken

Vollständige Docs: http://localhost:8000/docs

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