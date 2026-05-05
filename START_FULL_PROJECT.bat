@echo off
TITLE JEE/NEET Platform - Master Control
echo ===================================================
echo   🚀 Starting JEE/NEET Platform Infrastructure
echo ===================================================

:: 1. Start MinIO Server (Storage)
echo [1/3] Starting MinIO Storage Server...
start "MinIO Storage" cmd /k "E:\minio-data\minio.exe server E:\minio-data\data --console-address :9001"

:: 2. Start Python Backend (API Bridge)
echo [2/3] Starting Python Backend API...
start "Python Backend" cmd /k "cd minIO\server\backend && python main.py"

:: 3. Start React Main Website (Vite)
echo [3/4] Starting React Frontend (Main App)...
start "React Frontend" cmd /k "npm run dev"

:: 4. Start MinIO Custom Dashboard (UI)
echo [4/4] Starting MinIO Dashboard UI...
start "MinIO Dashboard" cmd /k "cd minIO && python -m http.server 3000"

echo.
echo ===================================================
echo   ✅ All systems are launching!
echo.
echo   Main Website:    http://localhost:5173
echo   Custom Dashboard: http://localhost:3000
echo   Backend API:     http://localhost:8000
echo   MinIO Console:   http://localhost:9001
echo ===================================================
echo.
echo NOTE: Keep these terminal windows open while working.
echo.
pause
