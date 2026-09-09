@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 is not installed.
  echo Download it from: https://www.python.org/downloads/
  echo During setup, select "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup: creating the demo environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

if not exist ".venv\.demo_requirements_ready" (
  echo First-time setup: installing required packages...
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :error
  type nul > ".venv\.demo_requirements_ready"
)

set FRESH_DATABASE=0
if not exist "db.sqlite3" set FRESH_DATABASE=1

set USE_SQLITE=1
set DEBUG=1

echo Preparing the local demo database...
.venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto :error
if "%FRESH_DATABASE%"=="1" (
  echo Adding sample products...
  .venv\Scripts\python.exe seed_products.py
  if errorlevel 1 goto :error
)
.venv\Scripts\python.exe manage.py create_staff --reset
if errorlevel 1 goto :error
set ADMIN_PASSWORD=AdminMatcha2026!
.venv\Scripts\python.exe manage.py create_admin --reset
if errorlevel 1 goto :error

echo.
echo ======================================================
echo  MATCHA SHOP DEMO IS STARTING
echo  Store: http://127.0.0.1:8000/
echo  Staff: staff / StaffMatcha2026!
echo  Admin: admin / AdminMatcha2026!
echo  Stop:  press Control + C
echo ======================================================
echo.

start "" "http://127.0.0.1:8000/"
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
exit /b 0

:error
echo.
echo Demo could not start. Read the error above.
pause
exit /b 1
