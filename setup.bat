@echo off
REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
pip install --upgrade pip
pip install -r requirements.txt

echo Virtual environment created and dependencies installed.
echo To activate manually later, run: call venv\Scripts\activate
pause

