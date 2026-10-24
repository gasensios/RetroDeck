@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

title RetroDeck - Estacion de Juegos Retro [SNES y Sega Mega Drive]
echo ======================================================================
echo    RETRODECK - Estacion de Juegos Retro de 16 Bits [Windows]
echo ======================================================================
echo.

rem 1. Check Python installation - testing execution to avoid Windows Store stubs
set "PYTHON_BIN="

python --version >nul 2>nul
if %ERRORLEVEL% equ 0 set "PYTHON_BIN=python"
if defined PYTHON_BIN goto :python_found

py -3 --version >nul 2>nul
if %ERRORLEVEL% equ 0 set "PYTHON_BIN=py -3"
if defined PYTHON_BIN goto :python_found

py --version >nul 2>nul
if %ERRORLEVEL% equ 0 set "PYTHON_BIN=py"
if defined PYTHON_BIN goto :python_found

python3 --version >nul 2>nul
if %ERRORLEVEL% equ 0 set "PYTHON_BIN=python3"
if defined PYTHON_BIN goto :python_found

:python_found
if not defined PYTHON_BIN goto :no_python

rem 2. Check and configure Virtual Environment
if exist ".venv\Scripts\python.exe" goto :venv_ready

echo [INFO] Creando entorno virtual aislado .venv...
%PYTHON_BIN% -m venv .venv
if %ERRORLEVEL% neq 0 goto :venv_error

echo [INFO] Actualizando pip e instalando dependencias pygame...
.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>nul
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 goto :pip_error

echo [OK] Entorno configurado correctamente.
echo.

:venv_ready

rem 3. Check for native emulator DLLs
if exist "src\emulator_core\libretrosnes.dll" goto :launch
if exist "src\emulator_core\retrosnes.dll" goto :launch

echo [AVISO] Las librerias nativas de Windows DLL aun no se han compilado.
where gcc >nul 2>nul
if %ERRORLEVEL% neq 0 goto :no_gcc

echo [INFO] Compilador GCC detectado. Compilando nucleos nativos para Windows...
call windows\compile_cores.bat
goto :launch

:no_gcc
echo [NOTA] Puedes compilar los nucleos nativos instalando MinGW/GCC o MSYS2
echo y ejecutando el script: windows\compile_cores.bat
echo.

:launch
rem 4. Launch RetroDeck
echo [INFO] Iniciando RetroDeck en Windows...
.venv\Scripts\python.exe src\main.py
if %ERRORLEVEL% neq 0 goto :app_error

exit /b 0

:no_python
echo [ERROR] No se ha encontrado Python instalado en el sistema.
echo Por favor, instala Python 3.10 o superior desde https://www.python.org/
echo Recuerda marcar la casilla: [X] "Add python.exe to PATH" durante la instalacion.
echo.
pause
exit /b 1

:venv_error
echo.
echo [ERROR] Fallo al crear el entorno virtual.
pause
exit /b 1

:pip_error
echo.
echo [ERROR] Error instalando dependencias en requirements.txt.
pause
exit /b 1

:app_error
echo.
echo [AVISO] La aplicacion finalizo con codigo de error %ERRORLEVEL%.
pause
exit /b %ERRORLEVEL%
