.PHONY: help build up down logs migrate shell test lint clean

# Default target
help:
	@echo "Available targets:"
	@echo "  build      - Build all Docker images"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  logs       - View logs"
	@echo "  migrate    - Run database migrations"
	@echo "  shell      - Open shell in API container"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters"
	@echo "  clean      - Remove all containers and volumes"

# Build
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Database migrations
migrate:
	docker-compose exec api alembic upgrade head

makemigrations:
	docker-compose exec api alembic revision --autogenerate -m "$(msg)"

# Shell access
shell-api:
	docker-compose exec api /bin/sh

shell-bot:
	docker-compose exec bot /bin/sh

shell-db:
	docker-compose exec postgres psql -U tamagotchi -d tamagotchi_db

# Testing
test-backend:
	docker-compose exec api pytest

test-frontend:
	docker-compose exec frontend npm test

# Linting
lint-backend:
	docker-compose exec api flake8 .
	docker-compose exec api black --check .

lint-frontend:
	docker-compose exec frontend npm run lint

format-backend:
	docker-compose exec api black .

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

# Development
dev-backend:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dev-bot:
	cd backend && python -m bot.main

dev-frontend:
	cd frontend && npm start

dev-celery:
	cd backend && celery -A tasks.worker worker --loglevel=info

dev-beat:
	cd backend && celery -A tasks.scheduler beat --loglevel=info

# Production
deploy:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

backup:
	docker-compose exec postgres pg_dump -U tamagotchi tamagotchi_db > backup_$$(date +%Y%m%d_%H%M%S).sql

restore:
	cat $(file) | docker-compose exec -T postgres psql -U tamagotchi -d tamagotchi_db
