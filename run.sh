#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Git Bash on Windows
    source venv/Scripts/activate
else
    # Unix / Linux / macOS
    source venv/bin/activate
fi

# Run the main application
python -m src.main "$@"
