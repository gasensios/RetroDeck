@echo off
setlocal

echo ======================================================================
echo    Generador de Ejecutable Portatil para Windows (RetroDeck.exe)
echo ======================================================================
echo.

cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual .venv. Ejecuta primero RetroDeck.bat.
    pause
    exit /b 1
)

echo [INFO] Verificando instalacion de PyInstaller...
.venv\Scripts\python -m pip install pyinstaller >nul 2>nul

echo [INFO] Empaquetando RetroDeck en un ejecutable de Windows...
.venv\Scripts\pyinstaller --noconfirm --onedir --windowed ^
    --name "RetroDeck" ^
    --add-data "assets;assets" ^
    --add-data "src\emulator_core;src\emulator_core" ^
    --add-data "config;config" ^
    src\main.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo [EXITO] Compilacion completada con exito.
    echo La aplicacion independiente portatil se encuentra en:
    echo   dist\RetroDeck\RetroDeck.exe
    echo ======================================================================
) else (
    echo [ERROR] Ocurrio un fallo durante la generacion del ejecutable.
)

pause
