@echo off
echo Starting CloudX Infrastructure (Testing Mode)...

:: Start Backend on Port 8000
start cmd /k "cd server\backend && C:\Python314\python.exe main.py"

:: Start Frontend Server on Port 3000
start cmd /k "C:\Python314\python.exe -m http.server 3000"

echo System initialized.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000/index.html
echo MinIO Console: http://192.168.1.13:9001
