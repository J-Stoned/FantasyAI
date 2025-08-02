@echo off
echo Starting MLB League Import Test...
echo ================================

echo.
echo Step 1: Starting the FastAPI server...
start cmd /k "python scripts/start.py"

echo.
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo.
echo Step 2: Running MLB import test...
python test_mlb_league_import.py

echo.
echo Test complete! Check the results above.
pause