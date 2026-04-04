@echo off
REM LaborGuard - Windows Startup Script

echo.
echo ===============================================
echo   🛡️  LaborGuard
echo   Windows Startup Script
echo ===============================================
echo.

REM Check if Docker is running
echo Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker Desktop is not running!
    echo.
    echo Please start Docker Desktop and wait for it to be ready, then run this script again.
    echo.
    echo Steps:
    echo   1. Open Docker Desktop
    echo   2. Wait for "Docker Desktop is running" status
    echo   3. Run this script again: .\start.bat
    echo.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Check if .env exists
if not exist ".env" (
    echo [INFO] .env file not found. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] .env file created from .env.example
    ) else (
        echo Creating default .env file...
        (
            echo # LaborGuard Environment Variables
            echo SECRET_KEY=dev-secret-key-change-in-production
            echo JWT_SECRET=dev-jwt-secret-change-in-production
            echo JWT_ALGORITHM=HS256
            echo JWT_EXPIRY_HOURS=24
            echo DATABASE_URL=sqlite+aiosqlite:///./laborguard.db
            echo USE_MOCK_APIS=true
            echo DEBUG=true
            echo CORS_ORIGINS=http://localhost:5173,http://localhost:3000
            echo VITE_API_BASE_URL=http://localhost:8000
        ) > .env
        echo [OK] .env file created
    )
)
echo.

echo Step 1/5: Stopping any existing containers...
docker-compose down 2>nul
echo.

echo Step 2/5: Ensuring Docker volume exists...
docker volume inspect laborguard_backend_data >nul 2>&1
if errorlevel 1 (
    docker volume create laborguard_backend_data >nul
    echo [OK] Created volume: laborguard_backend_data
) else (
    echo [OK] Volume exists: laborguard_backend_data
)
echo.

echo Step 3/5: Building Docker images...
echo Building backend and frontend...
docker-compose build backend frontend
if errorlevel 1 (
    echo [ERROR] Failed to build Docker images!
    pause
    exit /b 1
)
echo [OK] Docker images built successfully
echo.

echo Step 4/5: Starting backend...
docker-compose up -d backend
echo Waiting for backend to be ready (10 seconds)...
timeout /t 10 /nobreak >nul
echo.

echo Step 5/5: Starting frontend...
docker-compose up -d frontend
echo.

REM Verify services are running
echo Verifying services...
docker-compose ps
echo.

echo ===============================================
echo   ✅ All services started successfully!
echo ===============================================
echo.
echo Service URLs:
echo    Frontend:     http://localhost:5173
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/docs
echo    Health Check: http://localhost:8000/health
echo.
echo To view logs:
echo    All services:  docker-compose logs -f
echo    Backend only:  docker-compose logs -f backend
echo    Frontend only: docker-compose logs -f frontend
echo.
echo To stop all services:
echo    docker-compose down
echo.
echo To restart:
echo    docker-compose restart
echo.
pause
