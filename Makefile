up:
	@echo "Performing docker compose down"
	docker compose down
	@sleep 5
	@echo "Building the containers and starting them"
	docker compose up --build -d
	@sleep 5
	@echo "Creating db models (if the don't already exist)"
	python3 -m src.db.init_migrate
	@sleep 5
	@echo "Creating a super user if there's no"
	python3 -m src.db.superuser