@echo off
echo Please enter your Gemini API key (from Google Cloud Console):
set /p API_KEY="API Key: "

:: Set as environment variable
echo Setting GEMINI_API_KEY environment variable...
setx GEMINI_API_KEY "%API_KEY%"

:: Update credentials.json
echo Updating credentials.json...
python -c "import json; import os; credentials = {'api_key': '%API_KEY%'}; with open('credentials.json', 'w') as f: json.dump(credentials, f, indent=2)"

echo Credentials setup complete! You can now run the AI Code Translator.
pause
