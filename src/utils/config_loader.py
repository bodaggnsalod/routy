import yaml
from pathlib import Path
from typing import Any, Dict, Optional

def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Lade YAML-Konfiguration.
    
    Args:
        path: Optionaler Pfad zur config.yaml. 
              Wenn nicht angegeben, suche nach config/settings.yaml
    
    Returns:
        Dict mit Konfigurationsdaten
    """
    
    if path:
        config_path = Path(path)
    else:
        # Standardpfade durchsuchen
        possible_paths = [
            Path(__file__).parent.parent.parent / "config" / "settings.yaml",
            Path.cwd() / "config" / "settings.yaml",
            Path.cwd() / "routy" / "config" / "settings.yaml",
        ]
        
        config_path = None
        for p in possible_paths:
            if p.exists():
                config_path = p
                break
        
        if not config_path:
            # Fallback zu default config
            return _get_default_config()
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config or _get_default_config()
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load config from {config_path}: {e}")
        return _get_default_config()

def _get_default_config() -> Dict[str, Any]:
    """
    Gebe default Konfiguration zurück.
    """
    return {
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "version": "1.0"
        },
        "logging": {
            "level": "INFO"
        },
        "data": {
            "default_path": "/data/routes.csv"
        }
    }