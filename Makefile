init_setup:
	@echo "Performing docker compose down"
	docker compose down
	docker compose -f docker-compose.dev.yml down
	@sleep 5
	@echo "Building the containers and starting them"
	docker compose -f docker-compose.dev.yml  up --build -d
	@sleep 5
	@echo "Creating db models (if the don't already exist)"
	export ENV_MODE=.env.local; export PYTHONPATH=${PWD}; python3 -m src.db.init_migrate
	@sleep 5
	@echo "Creating a super user if there's no superuser"
	export ENV_MODE=.env.local; python3 -m src.db.superuser
	
up:
	docker compose up --build

up_test:
	docker compose -f docker-compose.dev.yml up --build

l_test:
	DB_HOST=localhost pytest tests/functional/src --log-cli-level=INFO

create_models:
	export ENV_MODE=.env.local; python3 -m src.db.model

test_config:
	export ENV_MODE=.env.local; python3 -m src.core.config
	export ENV_MODE=.env; python3 -m src.core.config

migrate:
	export ENV_MODE=.env.local; export PYTHONPATH=${PWD}; alembic revision --autogenerate  -m "Added user_agent field to access history model"

create_superuser:
	docker exec -it auth_service flask --app src.app createsuperuser

create_basic_roles:
	docker exec -it auth_service flask --app src.app create_basic_roles
