@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 app.py
) else (
  python app.py
)
if errorlevel 1 (
  echo.
  echo Nao foi possivel abrir. Verifique Python e Tkinter.
  pause
)
