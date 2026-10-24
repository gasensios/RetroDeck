@echo off
setlocal

cd /d "%~dp0\..\src\emulator_core"

echo ======================================================================
echo    Compilacion de Nucleos C para Windows [MinGW-w64 / GCC]
echo ======================================================================
echo.

where gcc >nul 2>nul
if %ERRORLEVEL% neq 0 goto :no_gcc

echo [1/2] Compilando nucleo Super Nintendo libretrosnes.dll...
gcc -O3 -shared -fPIC -Wall -Wextra -I snes snes/apu.c snes/cart.c snes/cpu.c snes/dma.c snes/dsp.c snes/input.c snes/ppu.c snes/snes.c snes/snes_other.c snes/spc.c snes/statehandler.c -o libretrosnes.dll -lm
if %ERRORLEVEL% equ 0 echo [OK] libretrosnes.dll generado correctamente.
if %ERRORLEVEL% neq 0 echo [ERROR] Fallo al compilar libretrosnes.dll.

echo.
echo [2/2] Compilando puente Sega Mega Drive libmegadrive_bridge.dll...
if not exist "libmegadrive.dll" goto :no_libmd

gcc -O3 -shared -fPIC -Wall -Wextra megadrive_bridge.c -L. -lmegadrive -o libmegadrive_bridge.dll -lm
if %ERRORLEVEL% equ 0 echo [OK] libmegadrive_bridge.dll generado correctamente.
if %ERRORLEVEL% neq 0 echo [ERROR] Fallo al compilar libmegadrive_bridge.dll.
goto :done

:no_libmd
echo [AVISO] libmegadrive.dll no esta presente. Omitiendo puente de Mega Drive.
goto :done

:no_gcc
echo [ERROR] No se ha encontrado gcc en el PATH.
echo Para compilar en Windows necesitas instalar MinGW-w64 o MSYS2:
echo  - Descarga MinGW: https://www.msys2.org/ o https://winlibs.com/
echo  - Asegurate de que la carpeta bin de MinGW este en la variable PATH.
echo.
pause
exit /b 1

:done
echo.
echo ======================================================================
echo    Proceso de compilacion finalizado.
echo ======================================================================
cd /d "%~dp0\.."
