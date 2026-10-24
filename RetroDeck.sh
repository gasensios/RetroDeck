#!/usr/bin/env bash
# ==============================================================================
# RetroDeck - Multi-System Retro Gaming Station (SNES, Mega Drive & Neo Geo)
# High-Performance Launcher with Auto-Tuning for PC & Raspberry Pi (ARM)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Hardware & Architecture Detection
ARCH="$(uname -m)"
IS_RPI=0

if [ -f /proc/device-tree/model ] && grep -qi "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    IS_RPI=1
    RPI_MODEL="$(tr -d '\0' < /proc/device-tree/model)"
    echo "=========================================================="
    echo " [RetroDeck] Hardware detectado: $RPI_MODEL ($ARCH)"
    echo " [RetroDeck] Aplicando optimizaciones de bajo consumo y latencia"
    echo "=========================================================="
elif [[ "$ARCH" =~ ^(arm|aarch64) ]]; then
    IS_RPI=1
    echo "[RetroDeck] Arquitectura ARM detectada ($ARCH). Optimizando buffers..."
fi

# Performance & Display Environment Variables
export SDL_RENDER_VSYNC=1
export PULSE_LATENCY_MSEC=30

# Standalone KMS/DRM Console Mode Detection for Raspberry Pi OS Lite
if [ "$IS_RPI" -eq 1 ] && [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    if [ -e /dev/dri/card0 ]; then
        echo "[RetroDeck] Sin servidor X11/Wayland detectado. Activando KMS/DRM puro..."
        export SDL_VIDEODRIVER=kmsdrm
    fi
fi

# Virtual Environment Detection
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 no está instalado en este sistema."
    exit 1
fi

# Verify / Auto-build native cores if missing and gcc is present
CORE_DIR="$SCRIPT_DIR/src/emulator_core"
if [ ! -f "$CORE_DIR/libretrosnes.so" ] || [ ! -f "$CORE_DIR/libmegadrive_bridge.so" ] || [ ! -f "$CORE_DIR/libneogeo_bridge.so" ]; then
    if command -v make &>/dev/null && command -v gcc &>/dev/null; then
        echo "[RetroDeck] Compilando núcleos nativos optimizados para $ARCH..."
        make -C "$CORE_DIR" -j"$(nproc 2>/dev/null || echo 2)"
    fi
fi

# Launch application
exec python3 "$SCRIPT_DIR/src/main.py" "$@"
