# Local Docker Compose deployment
export COMPOSE_PROJECT_NAME := "legal-ward"
set dotenv-load := true

# Default recipe - show available commands
default:
    @just --list


# Build services
build *args:
    docker compose -f docker-compose.yml build {{args}}

# Start services
up *args:
    docker compose -f docker-compose.yml up -d {{args}}
    @echo "backend: http://localhost:8000"

# Stop services
down *args:
    docker compose -f docker-compose.yml down {{args}}

# Follow logs
logs *args:
    docker compose -f docker-compose.yml logs -f {{args}}
    
# Run Django management commands
manage +args:
    docker compose -f docker-compose.yml exec backend python manage.py {{args}}

# Open Django shell
shell:
    docker compose -f docker-compose.yml exec backend python manage.py shell

# Run migrations
migrate:
    docker compose -f docker-compose.yml exec backend python manage.py migrate

# Create superuser
createsuperuser:
    docker compose -f docker-compose.yml exec backend python manage.py createsuperuser

# Run pytest tests
test:
    docker compose -f docker-compose.yml exec backend pytest --strict-markers --strict-config -x -v

# Clean up volumes and containers
clean:
    docker compose -f docker-compose.yml down -v
    docker system prune -f

