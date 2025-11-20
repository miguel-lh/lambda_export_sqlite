.PHONY: help install install-dev test lint format build deploy clean run-local

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependencias de producción
	pip install -r requirements.txt

install-dev: ## Instala dependencias de desarrollo
	pip install -r requirements-dev.txt

test: ## Ejecuta tests con coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit: ## Ejecuta solo tests unitarios
	pytest tests/unit/ -v

test-integration: ## Ejecuta solo tests de integración
	pytest tests/integration/ -v

lint: ## Ejecuta linters (flake8, pylint, mypy)
	flake8 src/ --max-line-length=100
	pylint src/ --max-line-length=100
	mypy src/

format: ## Formatea código con black e isort
	black src/ tests/
	isort src/ tests/

format-check: ## Verifica formateo sin modificar
	black --check src/ tests/
	isort --check-only src/ tests/

build: ## Construye la aplicación con SAM
	sam build

validate: ## Valida el template de SAM
	sam validate

run-local: build ## Ejecuta la función localmente
	sam local invoke ExportToSQLiteFunction -e events/event.json --env-vars events/env-vars.json

start-api: build ## Inicia API Gateway local
	sam local start-api --env-vars events/env-vars.json

deploy-dev: build ## Despliega a desarrollo
	sam deploy --config-env dev

deploy-prod: build ## Despliega a producción
	sam deploy --config-env prod

logs-dev: ## Muestra logs de desarrollo
	sam logs -n ExportToSQLiteFunction --stack-name export-sqlite-dev-stack --tail

logs-prod: ## Muestra logs de producción
	sam logs -n ExportToSQLiteFunction --stack-name export-sqlite-prod-stack --tail

clean: ## Limpia archivos generados
	rm -rf .aws-sam
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.sqlite" -delete

all: format lint test build ## Ejecuta format, lint, test y build
