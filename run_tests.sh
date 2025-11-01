#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Git Bash on Windows
    source venv/Scripts/activate
else
    # Unix / Linux / macOS
    source venv/bin/activate
fi

# Run tests with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "Coverage report generated in htmlcov/index.html"