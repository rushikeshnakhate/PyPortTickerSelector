#!/bin/bash
set -e  # exit on error

# Detect python executable
if command -v python &>/dev/null && python --version &>/dev/null 2>&1; then
    PYTHON=python
elif command -v py &>/dev/null; then
    PYTHON="py -3"
elif command -v python3 &>/dev/null && python3 --version &>/dev/null 2>&1; then
    PYTHON=python3
else
    echo "Python not found. Please install Python 3."
    exit 1
fi

echo "Using Python: $PYTHON"

# Create virtual environment
$PYTHON -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Git Bash on Windows
    source venv/Scripts/activate
else
    # Unix / Linux / macOS
    source venv/bin/activate
fi

# Upgrade pip (use python -m pip on Windows to avoid lock issues)
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "Virtual environment created and dependencies installed."
echo "To activate manually later:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "  source venv/Scripts/activate"
else
    echo "  source venv/bin/activate"
fi