@echo off
REM Activate virtual environment
call venv\Scripts\activate

REM Run tests using test_runner.py with coverage
python tests\test_runner.py -c -v

echo.
echo Coverage report generated in htmlcov\index.html
echo.
echo To run with different options:
echo   python tests\test_runner.py -c -v          # Coverage + verbose
echo   python tests\test_runner.py --quick        # Skip slow tests
echo   python tests\test_runner.py -f factory     # Only factory tests
echo   python tests\test_runner.py -p             # Run in parallel
echo.

pause