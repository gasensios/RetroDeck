# 🪟 Guía Oficial de RetroDeck para Windows

Esta carpeta contiene las herramientas y documentación específicas para ejecutar y compilar **RetroDeck** en sistemas operativos **Windows (10 y 11 de 64 bits)**.

---

## 🚀 Cómo Jugar en Windows (Paso a Paso)

### 1. Requisitos Previos
* **Python 3.10 o superior:** Descárgalo gratis desde [python.org](https://www.python.org/downloads/).
  > ⚠️ **Muy importante durante la instalación:** Marca la casilla **`[X] Add python.exe to PATH`** en la primera pantalla del instalador de Python.

---

### 2. Formas de Ejecutar el Emulador

Tienes tres métodos para jugar en Windows:

#### Método A: Lanzador Automático por Lotes (Recomendado)
Haz doble clic en el archivo raíz:
👉 **`RetroDeck.bat`**
* Creará automáticamente un entorno virtual aislado (`.venv`).
* Instalará las librerías necesarias (`pygame`).
* Iniciará RetroDeck en pantalla completa o ventana a 60 FPS.

#### Método B: Ejecución Silenciosa sin Consola
Si no deseas ver la ventana negra de la consola CMD detrás del juego, haz doble clic en:
👉 **`RetroDeck.vbs`**
* Arrancará la estación de juegos directamente con fondo transparente y sin ventanas de consola secundarias.

#### Método C: Crear un `.exe` Independiente (Portátil)
Si quieres llevarte RetroDeck en un pendrive o compartirlo sin requerir Python en otras máquinas Windows:
1. Haz doble clic en el script: **`windows\build_exe.bat`**
2. Se generará una carpeta lista para distribuir en: **`dist\RetroDeck\RetroDeck.exe`**

---

## 🎮 Compatibilidad con Mandos en Windows

RetroDeck utiliza el subsistema SDL2/Pygame con compatibilidad nativa para:
* **Mandos de Xbox (360, One, Series X/S):** Compatibilidad plug-and-play instantánea vía XInput.
* **Mandos de PlayStation (PS4 DualShock y PS5 DualSense):** Detección directa por USB o Bluetooth (compatible con Steam o DS4Windows).
* **Mandos 8BitDo y mandos retro USB:** Detección de cruceta analógica y digital.

Para personalizar cualquier botón o remapear los controles para SNES o Mega Drive, pulsa **`[C]`** dentro del emulador y navega con el diagrama interactivo de botones.

---

## 🛠️ Compilación de Núcleos Nativos C en Windows (Opcional)

Si deseas modificar el código C de los motores de emulación (`snes/` o `megadrive_bridge.c`) y recompilar las librerías dinámicas `.dll` en Windows:

1. Instala un entorno GCC para Windows como **[MSYS2](https://www.msys2.org/)** o **[WinLibs MinGW-w64](https://winlibs.com/)**.
2. Asegúrate de que `gcc` esté en tu variable de entorno PATH.
3. Ejecuta con doble clic el script:
   👉 **`windows\compile_cores.bat`**
4. Se generarán automáticamente `libretrosnes.dll` y `libmegadrive_bridge.dll` en la carpeta `src\emulator_core\`.
