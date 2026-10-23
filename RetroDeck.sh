#!/usr/bin/env bash
# ==============================================================================
# RetroDeck - Multi-System Linux Retro Gaming Station (SNES & Mega Drive)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Activate virtualenv if present
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Check Python3
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 no está instalado en este sistema."
    exit 1
fi

# Run application
exec python3 "$SCRIPT_DIR/src/main.py" "$@"
