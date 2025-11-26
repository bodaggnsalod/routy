# Routy AI Agent Instructions

## Project Overview
Routy is an AI-powered tour planning system for logistics companies. This is an **MVP/Phase 1** project with a strict separation between backend (FastAPI + Python) and frontend (React + Vite + Tailwind).

## Critical Architecture Decisions

### 1. Dual Structure Issue (IMPORTANT!)
The project currently has **two conflicting structures**:
- **Legacy:** `src/` with imports like `from src.backend.main import app`
- **Target:** `backend/app/` with imports like `from app.main import app`

⚠️ **When editing code:**
- Backend files in `backend/app/` should use `from app.*` imports
- Legacy `src/` files use `from src.*` imports
- `backend/app/main.py` exists but still imports from `src/` (inconsistent!)
- Check which structure you're in before adding imports

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
2. **Config Loading:** Uses `src.utils.config_loader.load_config()` to read `config/settings.yaml` (not Pydantic Settings!)
3. **Models:** Pydantic models in `backend/app/models/schemas.py` (Order, Vehicle, Stop)
4. **RL Agent:** Stub implementation in `backend/app/services/rl_agent.py` - uses naive priority sorting, not real ML
5. **CORS:** Wide open (`allow_origins=["*"]`) for MVP - tighten in production

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

1. **Import Confusion:** Mixing `from src.*` and `from app.*` breaks tests/runtime
2. **Missing Config:** Backend expects `config/settings.yaml` - will crash if missing
3. **Port Conflicts:** Backend on 8000, frontend on 5173 - check if already in use
4. **Proxy Failures:** Frontend won't fetch backend if backend not running on 8000
5. **Logo 404:** Frontend Landing component hardcodes `/@logo.jpg` - file must exist in `public/`

## External Dependencies & Integration

### Backend
- **FastAPI:** ASGI framework, auto-generates OpenAPI docs at `/docs`
- **Pydantic:** For request/response validation (NOT for settings!)
- **YAML Config:** Runtime config from `config/settings.yaml`
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
2. Import with `from app.services.new_service import ...` (or `from src.services...` if legacy)
3. Test in `backend/tests/test_services.py`

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
