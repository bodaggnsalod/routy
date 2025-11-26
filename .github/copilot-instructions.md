# Routy AI Agent Instructions

## Project Overview
Routy is an AI-powered tour planning system for logistics companies. This is an **MVP/Phase 1** project with a strict separation between backend (FastAPI + Python) and frontend (React + Vite + Tailwind).

## Critical Architecture Decisions

### 1. Project Structure (MIGRATED ✅)
The project uses a **clean monorepo structure**:
- **Backend:** `backend/app/` with imports like `from app.main import app`
- **Frontend:** `frontend/` (React + Vite)
- **Legacy `src/` folder:** May still exist but should NOT be used

⚠️ **When editing code:**
- Backend files MUST use `from app.*` imports (e.g., `from app.models.schemas import Order`)
- If you see `from src.*` imports, these are outdated and should be updated
- All new code goes into `backend/app/` structure

### 2. Monorepo Layout
```
routy/
├── backend/          # Python FastAPI (port 8000)
│   ├── app/         # New structure (preferred)
│   └── tests/       # pytest tests
├── frontend/         # React + Vite (port 5173)
│   ├── src/
│   └── tests/       # Vitest tests
└── docs/            # Project documentation
```

## Development Workflows

### Backend
```bash
cd backend
source .venv/bin/activate  # or .venv/bin/activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload  # OR src.backend.main:app (legacy)
pytest -v
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Vite dev server with proxy to backend
npm run test         # Vitest
```

### Full Stack (Docker)
```bash
docker-compose up    # Backend:8000, Frontend:5173
```

## Key Conventions

### Backend Patterns
1. **API Versioning:** All routes under `/api/v1/` (see `backend/app/api/v1/endpoints.py`)
2. **Config:** Uses Pydantic Settings in `backend/app/core/config.py` (NOT YAML!)
3. **Models:** Pydantic models in `backend/app/models/schemas.py` (Order, Vehicle, RouteResponse, StatsResponse)
4. **RL Agent:** Stub implementation in `backend/app/services/rl_agent.py` - uses naive priority sorting, not real ML
5. **CORS:** Configurable via `settings.ALLOWED_ORIGINS` (default: localhost:5173, localhost:3000)

### Frontend Patterns
1. **Proxy Setup:** Vite proxies `/health` and `/api` to `localhost:8000` (see `vite.config.js`)
2. **Landing Page:** Polls `/health` every 5s and shows status with colored indicator
3. **Logo Path:** Expects `/@logo.jpg` in `public/` (note the `@` prefix)
4. **Tailwind:** Utility-first, no custom component classes

### Testing Patterns
1. **Backend:** Uses `TestClient` from FastAPI, organized in classes (e.g., `TestAPIHealth`)
2. **Frontend:** Vitest with Testing Library, mocks `fetch` in `beforeEach`
3. **Coverage:** Backend aims for >70% (`pytest --cov=app`)

## Common Pitfalls

1. **Wrong Imports:** Using `from src.*` instead of `from app.*` breaks everything
2. **Missing pydantic-settings:** Backend requires `pydantic-settings` package for Settings class
3. **Port Conflicts:** Backend on 8000, frontend on 5173 - check if already in use
4. **Proxy Failures:** Frontend won't fetch backend if backend not running on 8000
5. **Logo 404:** Frontend Landing component expects `/@logo.jpg` - file must exist in `frontend/public/`
6. **PYTHONPATH:** When running backend, ensure you're in `backend/` directory or set PYTHONPATH correctly

## External Dependencies & Integration

### Backend
- **FastAPI:** ASGI framework, auto-generates OpenAPI docs at `/docs`
- **Pydantic:** For request/response validation AND settings (via pydantic-settings)
- **Settings:** Environment-based config via `.env` file (see `backend/.env.example`)
- **RLAgent:** Currently stub - Phase 2 will add TensorFlow/PyTorch

### Frontend
- **Vite:** Dev server + bundler, uses `@vitejs/plugin-react`
- **Tailwind CSS:** JIT compilation, config in `tailwind.config.cjs`
- **React 18:** Function components with hooks only

## Data Flow Example
```
Frontend (Landing.jsx)
  → fetch('/health')                    [Vite proxy]
    → http://localhost:8000/health      [FastAPI]
      → app.main.read_health()
        → returns {"status": "ok"}
```

## When Adding New Features

### New API Endpoint
1. Add route to `backend/app/api/v1/endpoints.py` (or create in `backend/app/api/v1/`)
2. Define Pydantic models in `backend/app/models/schemas.py`
3. Add test in `backend/tests/test_api.py` (use `TestClient(app)`)
4. Check OpenAPI docs at `http://localhost:8000/docs`

### New Frontend Component
1. Create in `frontend/src/components/`
2. Import in `App.jsx` or `Landing.jsx`
3. Use Tailwind classes (no custom CSS)
4. Add test in `frontend/tests/` with Vitest

### Service/Business Logic
1. Add to `backend/app/services/` (e.g., `new_service.py`)
2. Import with `from app.services.new_service import ...`
3. Test in `backend/tests/test_services.py`
4. Use type hints and docstrings (Google style)

## Phase 2 Plans (Context for Future Work)
- Real RL training (currently stubbed)
- PostgreSQL + Alembic migrations
- Live traffic API integration (HERE/TomTom)
- WebSocket for real-time updates
- Frontend dashboard with route visualization

## Quick Reference Commands
```bash
# Backend
uvicorn app.main:app --reload          # Dev server
pytest -v                               # Run tests
pytest --cov=app --cov-report=html     # Coverage

# Frontend  
npm run dev                             # Dev server
npm run test                            # Run tests
npm run build                           # Production build

# Docker
docker-compose up                       # Full stack
docker-compose down                     # Stop all
```
