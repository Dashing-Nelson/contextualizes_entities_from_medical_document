.PHONY: install

install:
	@echo "Checking for Poetry..."
	@if ! command -v poetry >/dev/null 2>&1; then \
	  echo "Poetry not found, installing..."; \
	  curl -sSL https://install.python-poetry.org | python3 -; \
	  echo "Adding Poetry to PATH for this session..."; \
	  export PATH="$${HOME}/.local/bin:$$PATH"; \
	else \
	  echo "Poetry is installed."; \
	fi
	@echo "Installing project dependencies via Poetry..."
	poetry install
	@echo "Checking for .env file..."
	@if [ ! -f .env ]; then \
	  echo ".env file not found. Please create one with the required configuration."; \
	  exit 1; \
	else \
	  echo ".env file found."; \
	fi
	@echo "Running download_model.sh script..."
	bash download_model.sh

.PHONY: format isort lint test check

format:
	@echo "Running Black formatter..."
	poetry run black .

isort:
	@echo "Running isort..."
	poetry run isort .

lint:
	@echo "Running flake8..."
	poetry run flake8 .

test:
	@echo "Running tests..."
	poetry run pytest

# Combined target to check code formatting and linting
check: format isort lint
	@echo "Code formatting and linting completed successfully."

.PHONY: docker-dev-build docker-dev-run docker-prod-build docker-prod-run

# Extract the HUGGING_FACE_MODEL_PATH and HTTP_PORT values from .env
HUGGING_FACE_MODEL_PATH := $(shell grep '^HUGGING_FACE_MODEL_PATH=' .env | cut -d '=' -f2)
HTTP_PORT := $(shell grep '^HTTP_PORT=' .env | cut -d '=' -f2)

# Docker Build & Run for Development Mode

docker-dev-build:
	@echo "Building development image with HUGGING_FACE_MODEL_PATH=$(HUGGING_FACE_MODEL_PATH)..."
	docker build --build-arg HUGGING_FACE_MODEL_PATH=$(HUGGING_FACE_MODEL_PATH) --target development -t fastapi-dev .

docker-dev-run:
	@echo "Running development container on port $(HTTP_PORT)..."
	docker run --env-file .env -d -p $(HTTP_PORT):8000 fastapi-dev

# Docker Build & Run for Production Mode

docker-prod-build:
	@echo "Building production image with HUGGING_FACE_MODEL_PATH=$(HUGGING_FACE_MODEL_PATH)..."
	docker build --build-arg HUGGING_FACE_MODEL_PATH=$(HUGGING_FACE_MODEL_PATH) --target production -t fastapi-prod .

docker-prod-run:
	@echo "Running production container on port $(HTTP_PORT)..."
	docker run --env-file .env -d -p $(HTTP_PORT):8000 fastapi-prod

.PHONY: run-dev

run-dev:
	@echo "Running application in development mode using uvicorn..."
	poetry run uvicorn app.main:app --reload --env-file .env