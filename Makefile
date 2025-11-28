.PHONY: help install test lint run docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make run          - Run application locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make clean        - Clean temporary files"

install:
	cd app && pip install -r requirements.txt

test:
	cd app && pytest test_main.py -v

lint:
	cd app && pylint app/*.py --disable=C0114,C0115,C0116 --max-line-length=120

run:
	cd app && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	cd app && docker build -t banking-devops-api .

docker-run:
	docker run -d -p 8000:8000 --name banking-api banking-devops-api

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
