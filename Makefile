.PHONY: install test coverage lint security run clean help

help:
	@echo "SAMS2 - Available Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make unit       - Run unit tests only"
	@echo "  make integration - Run integration tests only"
	@echo "  make coverage   - Run tests with coverage"
	@echo "  make lint       - Run code quality checks"
	@echo "  make security   - Run security scans"
	@echo "  make run        - Run application"
	@echo "  make clean      - Clean generated files"

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock pylint flake8 bandit safety

test:
	pytest tests/ -v

unit:
	pytest tests/unit/ -v

integration:
	pytest tests/integration/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src/ --max-line-length=120 --extend-ignore=E203,W503
	pylint src/ --exit-zero

security:
	bandit -r src/ -ll
	safety check

run:
	streamlit run app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage .pytest_cache/
	rm -f *.xml *.txt *.json
