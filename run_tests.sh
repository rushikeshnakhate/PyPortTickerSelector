#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Git Bash on Windows
    source venv/Scripts/activate
else
    # Unix / Linux / macOS
    source venv/bin/activate
fi

# Run tests using test_runner.py with coverage
python tests/test_runner.py -c -v

echo ""
echo "To run with different options:"
echo "  python tests/test_runner.py -c -v          # Coverage + verbose"
echo "  python tests/test_runner.py --quick        # Skip slow tests"
echo "  python tests/test_runner.py -f factory     # Only factory tests"
echo "  python tests/test_runner.py -p             # Run in parallel"