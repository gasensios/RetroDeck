@echo off
setlocal

cd /d "%~dp0\.."

echo ======================================================================
echo    Generador de Ejecutable Portatil para Windows [RetroDeck.exe]
echo ======================================================================
echo.

if not exist ".venv\Scripts\python.exe" goto :no_venv

echo [INFO] Verificando instalacion de PyInstaller...
.venv\Scripts\python.exe -m pip install pyinstaller >nul 2>nul

echo [INFO] Empaquetando RetroDeck en un ejecutable de Windows...
.venv\Scripts\pyinstaller.exe --noconfirm --onedir --windowed --name "RetroDeck" --add-data "assets;assets" --add-data "src\emulator_core;src\emulator_core" --add-data "config;config" src\main.py

if %ERRORLEVEL% neq 0 goto :build_error

echo.
echo ======================================================================
echo [EXITO] Compilacion completada con exito.
echo La aplicacion independiente portatil se encuentra en:
echo   dist\RetroDeck\RetroDeck.exe
echo ======================================================================
pause
exit /b 0

:no_venv
echo [ERROR] No se encontro el entorno virtual .venv. Ejecuta primero RetroDeck.bat.
pause
exit /b 1

:build_error
echo.
echo [ERROR] Ocurrio un fallo durante la generacion del ejecutable.
pause
exit /b 1
