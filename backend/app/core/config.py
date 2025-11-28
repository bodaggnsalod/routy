import os
from pathlib import Path
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Routy API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # RL Config
    RL_LEARNING_RATE: float = 0.01
    RL_EPISODES: int = 100
    RL_EPSILON: float = 0.1
    RL_GAMMA: float = 0.9
    
    # Autobahn API
    AUTOBAHN_API_URL: str = "https://verkehr.autobahn.de/o/autobahn/"
    AUTOBAHN_TIMEOUT: int = 5
    
    # Graph Network Config
    GRAPH_HIDDEN_DIM: int = 32
    GRAPH_MAX_STEPS: int = 20

settings = Settings()
