@echo off
echo 🚀 CodedSwitch AI Code Translator - Setup Script
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo 📦 Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📥 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📋 Installing dependencies...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    echo ⚠️ requirements.txt not found, installing core dependencies...
    python -m pip install ttkbootstrap>=1.10.1
    python -m pip install google-generativeai>=0.3.0
    python -m pip install grpcio>=1.66.0
    python -m pip install requests>=2.31.0
    python -m pip install python-dotenv>=1.0.0
    python -m pip install typing_extensions>=4.0.0
    python -m pip install pywin32>=306
)

REM Test installation
echo 🧪 Testing installation...
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import tkinter
    print('✅ tkinter: OK')
except ImportError as e:
    print(f'❌ tkinter: {e}')

try:
    import ttkbootstrap
    print('✅ ttkbootstrap: OK')
except ImportError as e:
    print(f'❌ ttkbootstrap: {e}')

try:
    import google.generativeai as genai
    print('✅ google-generativeai: OK')
except ImportError as e:
    print(f'❌ google-generativeai: {e}')

try:
    import requests
    print('✅ requests: OK')
except ImportError as e:
    print(f'❌ requests: {e}')

try:
    import dotenv
    print('✅ python-dotenv: OK')
except ImportError as e:
    print(f'❌ python-dotenv: {e}')

print('🎯 Core dependency test complete!')
"

echo.
echo ✅ Setup completed successfully!
echo.
echo To run the application:
echo   1. Activate the virtual environment: .venv\Scripts\activate.bat
echo   2. Run the application: python main.py
echo.
echo Or use: test_api.bat
echo.
echo 📝 Make sure your API key is set in the .env file!
echo.
pause
