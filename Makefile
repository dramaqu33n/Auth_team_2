init_setup:
	@echo "Performing docker compose down"
	docker compose down
	docker compose -f docker-compose.dev.yml down
	@sleep 5
	@echo "Building the containers and starting them"
	docker compose -f docker-compose.dev.yml  up --build -d
	@sleep 5
	@echo "Creating db models (if the don't already exist)"
	export ENV_MODE=.env.local; python3 -m src.db.init_migrate
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