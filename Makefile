.PHONY: run db install check migrate

run:
	@bash scripts/dev_run.sh

db:
	docker compose up -d db

install:
	@test -d .venv || python3 -m venv .venv
	@. .venv/bin/activate && pip install -r requirements.txt

migrate:
	@. .venv/bin/activate && python manage.py migrate

check:
	@. .venv/bin/activate && python manage.py check
