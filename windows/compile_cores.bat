@echo off
setlocal

cd /d "%~dp0\..\src\emulator_core"

echo ======================================================================
echo    Compilacion de Nucleos C para Windows [MinGW-w64 / GCC]
echo ======================================================================
echo.

where gcc >nul 2>nul
if %ERRORLEVEL% neq 0 goto :no_gcc

echo [1/3] Compilando nucleo Super Nintendo libretrosnes.dll...
gcc -O3 -shared -fPIC -Wall -Wextra -I snes snes/apu.c snes/cart.c snes/cpu.c snes/dma.c snes/dsp.c snes/input.c snes/ppu.c snes/snes.c snes/snes_other.c snes/spc.c snes/statehandler.c -o libretrosnes.dll -lm
if %ERRORLEVEL% equ 0 echo [OK] libretrosnes.dll generado correctamente.
if %ERRORLEVEL% neq 0 echo [ERROR] Fallo al compilar libretrosnes.dll.

echo.
echo [2/3] Compilando puente Sega Mega Drive libmegadrive_bridge.dll...
if exist "genesis_plus_gx_libretro.dll" goto :compile_md
if exist "libmegadrive.dll" goto :compile_md
goto :no_libmd

:compile_md
if exist "genesis_plus_gx_libretro.dll" gcc -O3 -shared -fPIC -Wall -Wextra megadrive_bridge.c genesis_plus_gx_libretro.dll -o libmegadrive_bridge.dll -lm
if not exist "genesis_plus_gx_libretro.dll" gcc -O3 -shared -fPIC -Wall -Wextra megadrive_bridge.c -L. -lmegadrive -o libmegadrive_bridge.dll -lm
if %ERRORLEVEL% equ 0 echo [OK] libmegadrive_bridge.dll generado correctamente.
if %ERRORLEVEL% neq 0 echo [ERROR] Fallo al compilar libmegadrive_bridge.dll.
goto :check_ng

:no_libmd
echo [AVISO] genesis_plus_gx_libretro.dll no esta presente. Omitiendo puente de Mega Drive.

:check_ng
echo.
echo [3/3] Compilando puente SNK Neo Geo libneogeo_bridge.dll...
if exist "fbalpha2012_neogeo_libretro.dll" goto :compile_ng
goto :no_libng

:compile_ng
gcc -O3 -shared -fPIC -Wall -Wextra neogeo_bridge.c fbalpha2012_neogeo_libretro.dll -o libneogeo_bridge.dll -lm
if %ERRORLEVEL% equ 0 echo [OK] libneogeo_bridge.dll generado correctamente.
if %ERRORLEVEL% neq 0 echo [ERROR] Fallo al compilar libneogeo_bridge.dll.
goto :done

:no_libng
echo [AVISO] fbalpha2012_neogeo_libretro.dll no esta presente. Omitiendo puente de Neo Geo.
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
