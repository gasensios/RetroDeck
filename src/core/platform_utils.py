"""
Platform Utilities for RetroDeck.
Cross-platform abstractions for Linux, Windows, and macOS.
Handles folder opening, native file pickers, and dynamic library loading.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = not (IS_WINDOWS or IS_MAC)

def open_folder(path: Path):
    """Opens a folder in the operating system's native file explorer."""
    path = Path(path).resolve()
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    if IS_WINDOWS:
        try:
            os.startfile(str(path))
        except Exception:
            subprocess.Popen(["explorer", str(path)])
    elif IS_MAC:
        subprocess.Popen(["open", str(path)])
    else:
        # Linux (xdg-open)
        try:
            subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            print(f"[PlatformUtils] Error opening folder with xdg-open: {e}")

def pick_image_file(title: str = "Seleccionar Caratula", initial_dir: Optional[Path] = None) -> Optional[str]:
    """
    Opens a native file picker dialog for images (.png, .jpg, .jpeg, .webp, .bmp).
    Works on Linux (zenity / kdialog), Windows (tkinter filedialog / PowerShell), and macOS.
    """
    filters_ext = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.PNG", "*.JPG", "*.JPEG", "*.WEBP", "*.BMP"]
    filters_str = " ".join(filters_ext)
    
    # 1. On Windows, try tkinter filedialog first (built into standard Python on Windows)
    if IS_WINDOWS:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected = filedialog.askopenfilename(
                title=title,
                initialdir=str(initial_dir) if initial_dir else None,
                filetypes=[
                    ("Imagenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.PNG;*.JPG;*.JPEG;*.WEBP;*.BMP"),
                    ("Todos los archivos", "*.*")
                ]
            )
            root.destroy()
            return selected if selected else None
        except Exception:
            pass
            
        # Fallback for Windows using PowerShell Forms
        try:
            ps_cmd = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$f = New-Object System.Windows.Forms.OpenFileDialog; "
                "$f.Filter = 'Imagenes (*.png;*.jpg;*.webp;*.bmp)|*.png;*.jpg;*.jpeg;*.webp;*.bmp'; "
                f"$f.Title = '{title}'; "
                "if($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){ Write-Output $f.FileName }"
            )
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return None

    # 2. On Linux, try zenity then kdialog
    if IS_LINUX:
        try:
            res = subprocess.run([
                "zenity", "--file-selection",
                f"--title={title}",
                f"--file-filter=Imagenes ({filters_str}) | {filters_str}",
                "--file-filter=Todos los archivos | *"
            ], capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

        try:
            res = subprocess.run([
                "kdialog", "--getopenfilename", str(initial_dir) if initial_dir else ".",
                f"{filters_str}|Archivos de Imagen"
            ], capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

    # 3. Fallback for macOS or any platform with tkinter
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        selected = filedialog.askopenfilename(
            title=title,
            initialdir=str(initial_dir) if initial_dir else None
        )
        root.destroy()
        return selected if selected else None
    except Exception:
        pass

    return None

def get_core_library_path(core_dir: Path, core_name: str) -> Path:
    """
    Returns the appropriate path for a native shared library:
    - Windows: core_name.dll or libcore_name.dll
    - Linux: libcore_name.so or core_name.so
    - macOS: libcore_name.dylib
    """
    core_dir = Path(core_dir).resolve()
    
    if IS_WINDOWS:
        candidates = [
            core_dir / f"lib{core_name}.dll",
            core_dir / f"{core_name}.dll"
        ]
    elif IS_MAC:
        candidates = [
            core_dir / f"lib{core_name}.dylib",
            core_dir / f"{core_name}.dylib"
        ]
    else:
        candidates = [
            core_dir / f"lib{core_name}.so",
            core_dir / f"{core_name}.so"
        ]

    for c in candidates:
        if c.exists():
            return c

    # Default to the primary candidate even if not created yet (for error reporting)
    return candidates[0]
