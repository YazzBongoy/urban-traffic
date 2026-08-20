# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

## Getting Started

1. Clone the repository
2. Run `./scripts/setup.sh`
3. Access the application at http://localhost:3000

## Development Workflow

### Backend

```bash
# Enter the backend container
./scripts/dev.sh shell

# Run tests
./scripts/dev.sh test

# Create a migration
./scripts/dev.sh makemigration "description"

# Apply migrations
./scripts/dev.sh migrate
```

### Frontend

```bash
cd frontend
npm run dev    # Start development server
npm run build  # Build for production
npm test       # Run tests
npm run lint   # Lint code
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Use ruff for linting
- Use black for formatting

### TypeScript (Frontend)
- Follow ESLint rules
- Use functional components with hooks
- Use TypeScript strict mode

## Testing

### Backend
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=app         # With coverage
```

### Frontend
```bash
npm test                  # Run tests
npm run test:coverage    # With coverage
```

## Database

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available configuration options.

## Troubleshooting

### Port conflicts
If ports are already in use, modify `docker-compose.yml` or stop conflicting services.

### Database connection issues
Ensure PostgreSQL is running and accessible:
```bash
docker-compose exec db psql -U postgres
```

### Redis connection issues
```bash
docker-compose exec redis redis-cli ping
```
