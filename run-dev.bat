@echo off
REM Run backend and frontend dev servers in separate windows (Windows)
SET ROOT=%~dp0
SET BACKEND_DIR=%ROOT%backend
SET FRONTEND_DIR=%ROOT%frontend

echo Starting backend in new window...
start "MatiousHire Backend" cmd /k "cd /d %BACKEND_DIR% && if exist .venv\Scripts\activate (call .venv\Scripts\activate) && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting frontend in new window...
start "MatiousHire Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo Dev servers started. Backend: http://127.0.0.1:8000  Frontend: http://127.0.0.1:3000 or fallback ports
pause
