.PHONY: dev dev-api dev-web test test-api lint lint-api lint-web build migrate

dev:
	docker compose up --build

dev-api:
	cd apps/api && uvicorn app.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

migrate:
	cd apps/api && alembic upgrade head

test: test-api

test-api:
	cd apps/api && python3 -m pytest tests/ -v

lint: lint-api lint-web

lint-api:
	cd apps/api && python3 -m pytest --collect-only -q

lint-web:
	cd apps/web && npm run lint

build:
	docker compose build

format:
	cd apps/web && npx prettier --write .
