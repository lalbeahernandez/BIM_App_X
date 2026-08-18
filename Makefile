SHELL := /bin/bash

.PHONY: bootstrap dev down logs ps clean lint format typecheck test smoke verify db-shell seed

bootstrap:
	@test -f .env || cp .env.example .env
	@echo "Environment ready."

dev: bootstrap
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans
	rm -rf .data apps/web/.next apps/web/node_modules

lint:
	docker compose run --rm api ruff check app tests
	docker compose run --rm web npm run lint

typecheck:
	docker compose run --rm api mypy app
	docker compose run --rm web npm run typecheck

format:
	docker compose run --rm api ruff format app tests
	docker compose run --rm web npm run format

test:
	docker compose run --rm api pytest -q

smoke:
	python scripts/smoke_http.py

verify:
	python scripts/verify_harness.py

db-shell:
	docker compose exec db psql -U bim -d bim

seed:
	docker compose exec -T db psql -U bim -d bim < db/seed.sql


codex-tasks:
	python scripts/validate_codex_tasks.py
