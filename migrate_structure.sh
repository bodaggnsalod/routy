#!/bin/bash

echo "🔄 Starting project restructure..."

# Create new directory structure
mkdir -p backend/app/{api/v1,core,models,services,utils}
mkdir -p backend/tests
mkdir -p backend/scripts
mkdir -p docs

# Move backend files
echo "📦 Moving backend files..."
cp src/backend/main.py backend/app/main.py
cp src/api/endpoints.py backend/app/api/v1/endpoints.py
cp src/models.py backend/app/models/schemas.py
cp src/data_pipeline/loader.py backend/app/services/data_loader.py
cp src/rl_engine/agent.py backend/app/services/rl_agent.py
cp src/rl_engine/environment.py backend/app/services/environment.py
cp src/simulation_env/simulation.py backend/app/services/simulation.py
cp tests/test_api.py backend/tests/test_api.py
cp requirements.txt backend/requirements.txt
cp .env.example backend/.env.example

# Move docs
echo "📚 Moving documentation..."
mv phase1.md docs/

# Clean up old structure
echo "🧹 Cleaning up..."
rm -rf src/
rm -rf tests/
rm -rf config/
rm requirements.txt

echo "✅ Restructure complete!"
echo ""
echo "Next steps:"
echo "1. cd backend && pip install -r requirements.txt"
echo "2. cd frontend && npm install"
echo "3. docker-compose up"