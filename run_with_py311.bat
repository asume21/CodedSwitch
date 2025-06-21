@echo off
echo 🚀 CodedSwitch AI Code Translator - Python 3.11 GPU Accelerated
echo =============================================================

REM Check if Python 3.11 virtual environment exists
if not exist "venv_py311" (
    echo ❌ Python 3.11 virtual environment not found!
    echo Please run setup_py311_env.bat first to create the environment
    pause
    exit /b 1
)

REM Activate Python 3.11 virtual environment
echo 🔌 Activating Python 3.11 virtual environment...
call venv_py311\Scripts\activate.bat

REM Set API key from .env file if it exists
if exist ".env" (
    echo 🔑 Loading environment variables from .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="GEMINI_API_KEY" set GEMINI_API_KEY=%%b
        if "%%a"=="OPENAI_API_KEY" set OPENAI_API_KEY=%%b
        if "%%a"=="HF_TOKEN" set HF_TOKEN=%%b
    )
)

REM Check for API key
if "%GEMINI_API_KEY%"=="" (
    echo ⚠️  Warning: GEMINI_API_KEY not found in environment
    echo You can still use demo mode, but AI features will be limited
)

REM Run the application
echo 🎯 Starting CodedSwitch with Python 3.11 and GPU acceleration...
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ❌ Application encountered an error
    pause
)

echo 👋 CodedSwitch session ended
pause
