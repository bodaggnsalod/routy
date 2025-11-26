from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting...")
    print(f"📍 API Prefix: {settings.API_V1_PREFIX}")
    print(f"🌐 CORS Origins: {settings.ALLOWED_ORIGINS}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="KI-basierte dynamische Tourenplanung für Logistikunternehmen",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health check
@app.get("/health", tags=["monitoring"])
def health_check():
    """
    Health-Check Endpunkt.
    
    Returns:
        Status, Service-Name und Version
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Include API routers
app.include_router(
    endpoints.router,
    prefix=settings.API_V1_PREFIX,
    tags=["api-v1"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )