up:
	@echo "Performing docker compose down"
	docker compose down
	@sleep 5
	@echo "Building the containers and starting them"
	docker compose up --build -d
	@sleep 5
	@echo "Creating db models (if the don't already exist)"
	python3 -m src.db.model
	@sleep 5
	@echo "Creating a super user, Arnold Shortman"
	python3 -m src.db.superuser


# init_migrate:
# 	@echo "Do initial migration"
# 	alembic revision --autogenerate -m "Initial migration"
# 	@sleep 5
# 	alembic upgrade head