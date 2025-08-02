@echo off
echo === Starting Yahoo OAuth Setup ===
echo.

echo Step 1: Starting FastAPI server...
start /B python scripts\start.py

echo Step 2: Waiting for server to start...
timeout /t 5 /nobreak > nul

echo Step 3: Starting ngrok tunnel...
echo.
echo IMPORTANT: Copy the HTTPS URL shown by ngrok!
echo.
ngrok.exe http 8000