@echo off
REM Activate virtual environment
call venv\Scripts\activate

REM Run tests with pytest and coverage
pytest --cov=src tests/

pause

