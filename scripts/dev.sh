#!/bin/bash
# Development helper scripts

case "$1" in
    start)
        echo "Starting development environment..."
        docker-compose up -d
        ;;
    stop)
        echo "Stopping development environment..."
        docker-compose down
        ;;
    restart)
        echo "Restarting development environment..."
        docker-compose down
        docker-compose up -d
        ;;
    logs)
        docker-compose logs -f
        ;;
    migrate)
        echo "Running migrations..."
        docker-compose exec backend alembic upgrade head
        ;;
    makemigration)
        echo "Creating migration..."
        docker-compose exec backend alembic revision --autogenerate -m "$2"
        ;;
    test)
        echo "Running tests..."
        docker-compose exec backend pytest
        ;;
    shell)
        docker-compose exec backend bash
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|migrate|makemigration|test|shell}"
        exit 1
        ;;
esac
