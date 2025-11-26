# Phase 1: Projektfundament und Prototyp-Setup

## 1. Zielsetzung

**Ziel:** Ein Code-Agent soll die vollständige Projektbasis für "Routy" erstellen.
**Ergebnis:** Eine lauffähige, testbare Codebasis mit allen Kernmodulen als Skelett-Implementierungen.

---

## 2. Aufgaben für den Code-Agenten

Führe die folgenden Schritte sequenziell aus. Jeder Schritt enthält eine Aufgabe und eine Verifizierung.

### **Schritt 1: Projektstruktur und Umgebung initialisieren**

**Aufgabe:**
1.  Erstelle das folgende Verzeichnis- und Dateilayout:
    ```
    /
    ├── .venv/
    ├── config/
    │   └── settings.yaml
    ├── src/
    │   ├── __init__.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── endpoints.py
    │   ├── backend/
    │   │   ├── __init__.py
    │   │   └── main.py
    │   ├── data_pipeline/
    │   │   ├── __init__.py
    │   │   └── loader.py
    │   ├── rl_engine/
    │   │   ├── __init__.py
    │   │   ├── agent.py
    │   │   └── environment.py
    │   ├── simulation_env/
    │   │   ├── __init__.py
    │   │   └── simulation.py
    │   └── utils/
    │       ├── __init__.py
    │       └── config_loader.py
    ├── tests/
    │   ├── __init__.py
    │   └── test_api.py
    ├── .env.example
    ├── README.md
    └── requirements.txt
    ```
2.  Initialisiere ein Python Virtual Environment im `.venv`-Ordner.
3.  Erstelle die `requirements.txt` mit folgendem Inhalt:
    ```
    fastapi
    uvicorn[standard]
    pydantic
    python-dotenv
    pyyaml
    pytest
    httpx
    ```

**Verifizierung:**
- Die Verzeichnisstruktur existiert wie oben definiert.
- Die Datei `requirements.txt` enthält die spezifizierten Pakete.

---

### **Schritt 2: Konfigurationssystem einrichten**

**Aufgabe:**
1.  Fülle die `config/settings.yaml` mit folgendem Inhalt:
    ```yaml
    api:
      host: "0.0.0.0"
      port: 8000
      version: "1.0"

    logging:
      level: "INFO"

    data:
      default_path: "/data/routes.csv"
    ```
2.  Erstelle eine `.env.example`-Datei mit dem Inhalt `API_KEY="YOUR_API_KEY_HERE"`.
3.  Implementiere in `src/utils/config_loader.py` eine Funktion zum Laden der YAML-Konfiguration.

**Verifizierung:**
- Die Konfigurationsdateien sind erstellt und enthalten die oben genannten Inhalte.

---

### **Schritt 3: Backend und API-Grundgerüst erstellen**

**Aufgabe:**
1.  Implementiere in `src/backend/main.py` eine FastAPI-Anwendung.
2.  Die Anwendung soll einen `/health`-Endpunkt haben, der `{"status": "ok"}` zurückgibt.
3.  Füge einen Dummy-Endpunkt `/api/v1/route/optimize` hinzu, der eine Beispiel-Route als JSON zurückgibt.

**Beispiel für `src/backend/main.py`:**
```python
from fastapi import FastAPI

app = FastAPI(title="Routy API")

@app.get("/health", tags=["Monitoring"])
def read_health():
    return {"status": "ok"}

@app.post("/api/v1/route/optimize", tags=["Routing"])
def optimize_route():
    # Dummy implementation
    return {
        "route_id": "dummy_route_123",
        "stops": ["Standort A", "Standort B", "Standort C"],
        "estimated_duration_minutes": 45
    }
```

**Verifizierung:**
- Die FastAPI-Anwendung kann mit `uvicorn src.backend.main:app --reload` gestartet werden.
- Ein GET-Request an `http://127.0.0.1:8000/health` gibt `{"status": "ok"}` zurück.

---

### **Schritt 4: RL-Engine und Simulation als Skelett implementieren**

**Aufgabe:**
1.  Erstelle in `src/rl_engine/agent.py` eine Klasse `RLAgent` mit Methoden wie `train()` und `predict()`.
2.  Erstelle in `src/rl_engine/environment.py` eine Klasse `TourEnvironment` mit Methoden wie `reset()` und `step()`.
3.  Erstelle in `src/simulation_env/simulation.py` eine Klasse `Simulation` mit Methoden wie `run_step()` und `add_event()`.
4.  Alle Methoden können vorerst `pass` oder eine Log-Ausgabe enthalten.

**Verifizierung:**
- Die Klassen und Methoden sind in den entsprechenden Dateien definiert und importierbar.

---

### **Schritt 5: Testsystem aufsetzen**

**Aufgabe:**
1.  Implementiere in `tests/test_api.py` einen Test für den `/health`-Endpunkt.

**Beispiel für `tests/test_api.py`:**
```python
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Verifizierung:**
- Das Kommando `pytest` im Hauptverzeichnis läuft erfolgreich durch.

---

## 3. Akzeptanzkriterien für Phase 1

- Das Projekt kann mit `uvicorn` gestartet werden und die API ist erreichbar.
- Alle Modul-Skelette sind vorhanden und importierbar.
- Das Test-Setup ist konfiguriert und die Basis-Tests laufen erfolgreich durch.
- Die Konfiguration kann aus der YAML-Datei geladen werden.