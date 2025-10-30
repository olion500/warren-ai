.PHONY: help install test lint format analyze run-agent

# Default target - show help
help:
	@echo "Warren AI - Buffett-style Investment Analysis Framework"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make analyze      - Analyze a stock (use: make analyze TICKER=AAPL)"
	@echo "  make help         - Show this help message"

# Install dependencies
install:
	pip install -e .

# Run tests
test:
	pytest tests/ -v

# Lint code
lint:
	ruff check .
	mypy warren_core/

# Format code
format:
	black warren_core/ tests/
	isort warren_core/ tests/

# Run stock analysis
analyze:
	@if [ -z "$(TICKER)" ]; then \
		echo "Usage: make analyze TICKER=<symbol>"; \
		echo "Example: make analyze TICKER=AAPL"; \
		exit 1; \
	fi
	python -m warren_core.orchestrator --ticker $(TICKER)
