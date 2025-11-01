@echo off
REM Activate virtual environment
call venv\Scripts\activate

REM Run the main application
python -m src.main %*

pause
