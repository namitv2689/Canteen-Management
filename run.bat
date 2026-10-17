@echo off
REM One-click setup + run for Canteen Coupon Management (Windows)
cd /d "%~dp0"

REM Find a real Python (the Microsoft Store placeholder does not count)
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"
if not defined PY (
  echo.
  echo  Python is not installed on this PC.
  echo  1. Download it from https://www.python.org/downloads/
  echo  2. In the installer, tick "Add python.exe to PATH", then Install.
  echo  3. Double-click run.bat again.
  echo.
  pause
  exit /b 1
)

if not exist venv\Scripts\python.exe (
  echo Creating virtual environment...
  %PY% -m venv venv || (echo Could not create the virtual environment. & pause & exit /b 1)
)

echo Installing dependencies...
venv\Scripts\python.exe -m pip install -q -r requirements.txt || (echo Dependency install failed. & pause & exit /b 1)

REM Open the project in VS Code (if installed)
where code >nul 2>nul && call code .

REM Open the browser shortly after the server starts
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:5000/"

echo.
echo Starting server at http://127.0.0.1:5000/  (press Ctrl+C to stop)
venv\Scripts\python.exe app.py
pause
