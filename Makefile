.PHONY: help setup start stop restart logs test lint migrate clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@./scripts/setup.sh

start: ## Start development environment
	@docker-compose up -d

stop: ## Stop development environment
	@docker-compose down

restart: ## Restart development environment
	@docker-compose down
	@docker-compose up -d

logs: ## View logs
	@docker-compose logs -f

test: ## Run all tests
	@docker-compose exec backend pytest
	@cd frontend && npm test

test-backend: ## Run backend tests
	@docker-compose exec backend pytest

test-frontend: ## Run frontend tests
	@cd frontend && npm test

lint: ## Lint code
	@docker-compose exec backend ruff check .
	@cd frontend && npm run lint

migrate: ## Run database migrations
	@docker-compose exec backend alembic upgrade head

makemigration: ## Create new migration (usage: make makemigration msg="description")
	@docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

clean: ## Clean up
	@docker-compose down -v
	@docker system prune -f

shell: ## Open backend shell
	@docker-compose exec backend bash

db-shell: ## Open database shell
	@docker-compose exec db psql -U postgres urban_traffic

redis-shell: ## Open Redis shell
	@docker-compose exec redis redis-cli

build: ## Build Docker images
	@docker-compose build

push: ## Push images to registry
	@docker-compose push

status: ## Show service status
	@docker-compose ps
