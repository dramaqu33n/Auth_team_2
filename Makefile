init_setup:
	@echo $(DB_HOST)
	@echo "Performing docker compose down"
	docker compose down
	@sleep 5
	@echo "Building the containers and starting them"
	DB_HOST=localhost docker compose up --build -d
	@sleep 5
	@echo "Creating db models (if the don't already exist)"
	DB_HOST=localhost python3 -m src.db.init_migrate
	@sleep 5
	@echo "Creating a super user if there's no superuser"
	DB_HOST=localhost python3 -m src.db.superuser
	
up:
	docker compose up --build

local_test:
	export ENV_MODE=.env.local; export PYTHONPATH=${PWD};\
	docker compose up --build
	pytest tests/functional/src --log-cli-level=INFO
