.PHONY: help up down logs migrate shell

help:
	@echo "Available commands:"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - View all logs"
	@echo "  make migrate   - Run migrations"
	@echo "  make shell     - Enter backend shell"

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend python manage.py makemigrations
	docker-compose exec backend python manage.py migrate

shell:
	docker-compose exec backend bash