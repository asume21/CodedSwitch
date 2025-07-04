#!/usr/bin/env bash
# 🐧 CodedSwitch AI Code Translator - Python 3.11 / Linux launcher
# Equivalent to run_with_py311.bat for Windows.

set -e

echo "🚀 CodedSwitch AI Code Translator - Python 3.11 (Linux)"

# Resolve script directory to allow execution from anywhere
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ----------------------------------------------------------------------
# 1. Check that the virtual environment exists
# ----------------------------------------------------------------------
if [ ! -d "$SCRIPT_DIR/venv_py311" ]; then
  echo "❌ Python 3.11 virtual environment 'venv_py311' not found!"
  echo "Run setup_py311_env.sh first to create the environment."
  exit 1
fi

# ----------------------------------------------------------------------
# 2. Activate virtual environment
# ----------------------------------------------------------------------
source "$SCRIPT_DIR/venv_py311/bin/activate"

# ----------------------------------------------------------------------
# 3. Load environment variables from .env if present
# ----------------------------------------------------------------------
if [ -f "$SCRIPT_DIR/.env" ]; then
  echo "🔑 Loading environment variables from .env ..."
  set -a  # export all sourced variables
  source "$SCRIPT_DIR/.env"
  set +a
fi

if [ -z "$GEMINI_API_KEY" ]; then
  echo "⚠️  Warning: GEMINI_API_KEY not set. AI features will be limited."
fi

# ----------------------------------------------------------------------
# 4. Launch the application
# ----------------------------------------------------------------------
echo "🎯 Starting CodedSwitch ..."
python "$SCRIPT_DIR/main.py" "$@"
