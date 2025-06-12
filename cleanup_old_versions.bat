@echo off
echo This script will remove all old versions of the AI Code Translator
pause

echo Removing old versions...
del /S /Q "..\AI_Code_Translator_Organized\Advanced_Version\*"
del /S /Q "..\AI_Code_Translator_Organized\Chatbot_Version\*"
del /S /Q "..\AI_Code_Translator_Organized\Gemini_Version\*"
del /S /Q "..\AI_Code_Translator_Organized\Standalone_Version\*"
del /S /Q "..\AI_Code_Translator_Organized\Ultimate_Version\*"

echo Cleaning up empty directories...
rmdir /S /Q "..\AI_Code_Translator_Organized\Advanced_Version"
rmdir /S /Q "..\AI_Code_Translator_Organized\Chatbot_Version"
rmdir /S /Q "..\AI_Code_Translator_Organized\Gemini_Version"
rmdir /S /Q "..\AI_Code_Translator_Organized\Standalone_Version"
rmdir /S /Q "..\AI_Code_Translator_Organized\Ultimate_Version"

pause
