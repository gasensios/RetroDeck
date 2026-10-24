@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

title RetroDeck - Estacion de Juegos Retro (SNES y Sega Mega Drive)
echo ======================================================================
echo    RETRODECK - Estacion de Juegos Retro de 16 Bits (Windows)
echo ======================================================================
echo.

rem 1. Check Python installation (check 'python' first, then 'py' launcher)
set "PYTHON_BIN="
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PYTHON_BIN=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_BIN=py"
    )
)

if not defined PYTHON_BIN (
    echo [ERROR] No se ha encontrado Python instalado en el sistema.
    echo Por favor, instala Python 3.10 o superior desde https://www.python.org/
    echo Recuerda marcar la casilla: [X] "Add python.exe to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

rem 2. Check and configure Virtual Environment
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual aislado (.venv)...
    !PYTHON_BIN! -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Fallo al crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [INFO] Instalando dependencias necesarias (pygame)...
    .venv\Scripts\python -m pip install --upgrade pip >nul 2>nul
    .venv\Scripts\python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Error instalando dependencias.
        pause
        exit /b 1
    )
    echo [OK] Entorno configurado correctamente.
    echo.
)

rem 3. Check for native emulator DLLs
if not exist "src\emulator_core\libretrosnes.dll" (
    if not exist "src\emulator_core\retrosnes.dll" (
        echo [AVISO] Las librerias nativas de Windows (.dll) aun no se han compilado.
        where gcc >nul 2>nul
        if %ERRORLEVEL% equ 0 (
            echo [INFO] Compilador GCC detectado. Compilando nucleos nativos para Windows...
            call windows\compile_cores.bat
        ) else (
            echo [NOTA] Puedes compilar los nucleos nativos instalando MinGW/GCC o MSYS2
            echo y ejecutando el script: windows\compile_cores.bat
        )
        echo.
    )
)

rem 4. Launch RetroDeck
echo [INFO] Iniciando RetroDeck en Windows...
.venv\Scripts\python src\main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [AVISO] La aplicacion finalizo con codigo de error %ERRORLEVEL%.
    pause
)
