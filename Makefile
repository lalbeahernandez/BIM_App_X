.PHONY: bootstrap dev down logs ps clean lint format typecheck test smoke verify all db-shell seed codex-tasks

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
	python scripts/dev.py lint

typecheck:
	python scripts/dev.py typecheck

format:
	docker compose run --rm api ruff format app tests
	docker compose run --rm web npm run format

test:
	python scripts/dev.py test

smoke:
	python scripts/dev.py smoke

verify:
	python scripts/dev.py verify

all:
	python scripts/dev.py all

db-shell:
	docker compose exec db psql -U bim -d bim

seed:
	docker compose exec -T db psql -U bim -d bim < db/seed.sql


codex-tasks:
	python scripts/dev.py codex-tasks
