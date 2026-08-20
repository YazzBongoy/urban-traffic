#!/bin/bash
# Setup script for Urban Traffic Management System

set -e

echo "🚗 Urban Traffic Management System - Setup"
echo "============================================"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose exec backend alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend:    http://localhost:3000"
echo "  - MinIO:       http://localhost:9001"
echo ""
echo "API Documentation: http://localhost:8000/docs"
