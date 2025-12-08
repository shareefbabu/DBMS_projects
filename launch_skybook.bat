@echo off
echo ============================================================
echo        SkyBook Complete Launcher
echo ============================================================
echo.

REM Kill any existing Python processes
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start API server in new window
echo [*] Starting API server...
start "SkyBook API Server" /MIN python api_server.py
timeout /t 5 /nobreak >nul

REM Start HTTP server for frontend in new window
echo [*] Starting HTTP server for frontend...
start "SkyBook HTTP Server" /MIN python -m http.server 8000
timeout /t 3 /nobreak >nul

REM Open browser
echo [*] Opening SkyBook in browser...
start http://localhost:8000/index.html

echo.
echo ============================================================
echo        SkyBook is now running!
echo ============================================================
echo.
echo   Frontend:  http://localhost:8000/index.html
echo   API:       http://localhost:5000
echo.
echo   IMPORTANT: Do NOT close the API Server or HTTP Server windows!
echo              Close this window when done to stop all servers.
echo ============================================================
echo.
echo Press any key to STOP all servers and exit...
pause >nul

REM Cleanup: kill all Python processes
taskkill /F /IM python.exe >nul 2>&1
echo.
echo [*] All servers stopped. Goodbye!
timeout /t 2 /nobreak >nul
