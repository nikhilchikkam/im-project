@echo off
setlocal enabledelayedexpansion

echo 🚀 Nutrigence Local Development Setup
echo =====================================

REM Check prerequisites
echo [INFO] Checking prerequisites...

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 20+ from https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1,2,3 delims=." %%a in ('node --version') do set NODE_VERSION=%%a
set NODE_VERSION=%NODE_VERSION:~1%
if %NODE_VERSION% lss 20 (
    echo [ERROR] Node.js version 20+ required. Found: %NODE_VERSION%
    pause
    exit /b 1
)
echo [SUCCESS] Node.js found

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%a in ('python --version') do set PYTHON_VERSION=%%a
for /f "tokens=2 delims=." %%a in ("%PYTHON_VERSION%") do set PYTHON_MINOR=%%a
if %PYTHON_MINOR% lss 9 (
    echo [ERROR] Python 3.9+ required. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git not found. Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)
echo [SUCCESS] Git found

REM Check if we're in the right directory
if not exist "README.md" (
    echo [ERROR] Please run this script from the project root directory (where README.md is located)
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] Frontend directory not found
    pause
    exit /b 1
)

if not exist "backend" (
    echo [ERROR] Backend directory not found
    pause
    exit /b 1
)

echo [SUCCESS] All prerequisites met!

REM Create environment files
echo [INFO] Setting up environment files...

REM Backend environment
if not exist "backend\.env" (
    (
        echo # Database Configuration
        echo DATABASE_URL=postgresql://nutrigence_user:password@localhost:5432/nutrigence_db
        echo.
        echo # Authentication
        echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
        echo JWT_ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo REFRESH_TOKEN_EXPIRE_DAYS=7
        echo.
        echo # Environment
        echo ENVIRONMENT=development
        echo FRONTEND_URL=http://localhost:5173
    ) > backend\.env
    echo [SUCCESS] Created backend\.env
) else (
    echo [WARNING] backend\.env already exists, skipping...
)

REM Frontend environment
if not exist "frontend\.env" (
    (
        echo # API Configuration
        echo VITE_API_URL=http://localhost:8000
        echo.
        echo # Environment
        echo VITE_ENVIRONMENT=development
    ) > frontend\.env
    echo [SUCCESS] Created frontend\.env
) else (
    echo [WARNING] frontend\.env already exists, skipping...
)

REM Setup backend
echo [INFO] Setting up backend...

cd backend

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo [INFO] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo [SUCCESS] Backend dependencies installed

cd ..

REM Setup frontend
echo [INFO] Setting up frontend...

cd frontend

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm install
echo [SUCCESS] Frontend dependencies installed

cd ..

REM Database setup
echo [INFO] Setting up database...

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Docker found. Setting up PostgreSQL with Docker...
    
    REM Check if container already exists
    docker ps -a --format "table {{.Names}}" | findstr "nutrigence-postgres" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [WARNING] PostgreSQL container already exists
        set /p choice="Do you want to remove the existing container and create a new one? (y/N): "
        if /i "!choice!"=="y" (
            docker stop nutrigence-postgres >nul 2>&1
            docker rm nutrigence-postgres >nul 2>&1
        )
    )
    
    REM Create PostgreSQL container
    docker run --name nutrigence-postgres -e POSTGRES_DB=nutrigence_db -e POSTGRES_USER=nutrigence_user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
    
    echo [SUCCESS] PostgreSQL container started
    echo [INFO] Waiting for database to be ready...
    timeout /t 5 /nobreak >nul
    
) else (
    echo [WARNING] Docker not found. Please install PostgreSQL manually:
    echo   - Download from https://www.postgresql.org/download/windows/
    echo.
    echo Then create the database:
    echo   psql -U postgres
    echo   CREATE DATABASE nutrigence_db;
    echo   CREATE USER nutrigence_user WITH PASSWORD 'password';
    echo   GRANT ALL PRIVILEGES ON DATABASE nutrigence_db TO nutrigence_user;
    echo   \q
)

echo [SUCCESS] Setup completed successfully!
echo.
echo 🎉 Your Nutrigence development environment is ready!
echo.
echo Next steps:
echo 1. Start the backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python api.py
echo.
echo 2. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Visit http://localhost:5173 in your browser
echo.
echo 📚 For more information, see LOCAL_DEVELOPMENT_SETUP.md

pause
