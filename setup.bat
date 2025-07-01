@echo off
REM Fitness Studio Agent System - Setup Script for Windows
REM This script sets up the entire development environment

setlocal enabledelayedexpansion

echo 🏋️ Fitness Studio Agent System Setup
echo ====================================

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Desktop first.
    exit /b 1
)

echo [SUCCESS] Docker and Docker Compose are installed

REM Check if .env file exists
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy .env.example .env >nul
    echo [WARNING] Please edit .env file with your OpenAI API key and other settings
    echo [WARNING] Minimal required: OPENAI_API_KEY=your_key_here
) else (
    echo [SUCCESS] .env file already exists
)

REM Handle command line arguments
set "command=%1"
if "%command%"=="" set "command=setup"

if "%command%"=="setup" goto :setup
if "%command%"=="start" goto :start
if "%command%"=="stop" goto :stop
if "%command%"=="reset" goto :reset
if "%command%"=="logs" goto :logs
if "%command%"=="test" goto :test
if "%command%"=="help" goto :help
goto :unknown

:setup
echo [INFO] Starting setup process...
echo.

echo [INFO] Starting Docker services...
docker-compose pull
docker-compose up -d mongodb redis

echo [INFO] Waiting for MongoDB to be ready...
timeout /t 10 /nobreak >nul

docker-compose up -d backend

echo [INFO] Waiting for backend to be ready...
timeout /t 15 /nobreak >nul

echo [INFO] Generating sample data...
timeout /t 5 /nobreak >nul
docker-compose exec -T backend python -m app.utils.sample_data

echo.
echo [SUCCESS] Setup completed! 🎉
echo.
echo 📡 API Endpoints:
echo    • API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo    • Health Check: http://localhost:8000/
echo.
echo 🗄️ Database Management:
echo    • Start MongoDB Express: docker-compose --profile tools up -d mongo-express
echo    • Access: http://localhost:8081 (admin/admin123)
echo.
echo 🧪 Testing Commands:
echo    • Test APIs: setup.bat test
echo.
echo 📊 Logs:
echo    • View backend logs: docker-compose logs -f backend
echo.
echo 🛑 Stop Services:
echo    • Stop: setup.bat stop
echo    • Reset: setup.bat reset
goto :end

:start
echo [INFO] Starting services...
docker-compose up -d
echo [SUCCESS] Services started!
goto :end

:stop
echo [INFO] Stopping services...
docker-compose down
echo [SUCCESS] Services stopped!
goto :end

:reset
echo [WARNING] This will remove all data. Are you sure? (y/N)
set /p response=
if /i "!response!"=="y" (
    echo [INFO] Resetting environment...
    docker-compose down -v
    docker system prune -f
    echo [SUCCESS] Environment reset!
) else (
    echo [INFO] Reset cancelled.
)
goto :end

:logs
docker-compose logs -f backend
goto :end

:test
echo [INFO] Running quick API tests...
echo.

REM Test health endpoint
echo Testing health endpoint...
curl -s http://localhost:8000/ | findstr "Fitness Studio" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] ✓ Health check passed
) else (
    echo [ERROR] ✗ Health check failed
)

REM Test support agent
echo Testing support agent...
curl -s -X POST http://localhost:8000/api/v1/support -H "Content-Type: application/json" -d "{\"query\": \"What is the status of the system?\"}" | findstr "response" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] ✓ Support agent test passed
) else (
    echo [ERROR] ✗ Support agent test failed
)

REM Test dashboard agent
echo Testing dashboard agent...
curl -s -X POST http://localhost:8000/api/v1/dashboard -H "Content-Type: application/json" -d "{\"query\": \"Show system status\"}" | findstr "response" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] ✓ Dashboard agent test passed
) else (
    echo [ERROR] ✗ Dashboard agent test failed
)
goto :end

:help
echo Usage: %0 [command]
echo.
echo Commands:
echo   setup     Complete setup (default)
echo   start     Start services
echo   stop      Stop services
echo   reset     Reset environment (removes all data)
echo   logs      Show backend logs
echo   test      Run API tests
echo   help      Show this help
goto :end

:unknown
echo [ERROR] Unknown command: %command%
echo Use '%0 help' for available commands
exit /b 1

:end
pause
