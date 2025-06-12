@echo off
echo Starting AI Code Translator - Advanced Final Version
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Run the application
python integrated_gui.py

pause
