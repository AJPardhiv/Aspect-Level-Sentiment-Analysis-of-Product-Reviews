@echo off
REM CaterOps AI - Quick Setup Script for Windows

setlocal enabledelayedexpansion

echo.
echo 🍽️ CaterOps AI - Quick Setup
echo ==============================
echo.

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if errorlevel 1 (
    echo PostgreSQL not found. Please install PostgreSQL first.
    pause
    exit /b 1
)

echo ✓ PostgreSQL found

REM Create database
echo.
echo Creating database...
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'caterops'" | findstr /r "1" >nul 2>&1 || ^
    psql -U postgres -c "CREATE DATABASE caterops;"
echo ✓ Database created

REM Run schema
echo.
echo Running database schema...
psql -U postgres -d caterops -f database\schema.sql
echo ✓ Schema loaded

REM Seed data
echo.
echo Seeding sample data...
psql -U postgres -d caterops -f database\seeds\seed_data.sql
echo ✓ Sample data loaded

REM Setup backend
echo.
echo Setting up backend...
cd backend

if not exist .env (
    copy .env.example .env
    echo ✓ Created .env file
)

call npm install
echo ✓ Backend dependencies installed

cd ..

REM Setup frontend
echo.
echo Setting up frontend...
cd frontend

call npm install
echo ✓ Frontend dependencies installed

cd ..

echo.
echo ==============================
echo ✓ Setup Complete!
echo ==============================
echo.
echo Next steps:
echo 1. Backend:  cd backend ^&^& npm run dev
echo 2. Frontend: cd frontend ^&^& npm run dev
echo 3. Open:     http://localhost:5173
echo.
echo Make sure PostgreSQL is running!
echo.
pause
