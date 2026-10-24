# 📘 Manual de Usuario y Funcionamiento Interno de RetroDeck

¡Bienvenido a **RetroDeck**! Esta estación de emulación retro soporta de forma nativa **Super Nintendo (SNES)**, **Sega Mega Drive / Genesis** y **SNK Neo Geo (MVS / AES)** mediante motores propios en C, una interfaz gráfica interactiva en Python/Pygame y una versión web ligera para navegadores.

---

## 📑 Índice de Contenidos

1. [¿Qué es RetroDeck?](#1-qué-es-retrodeck)
2. [Sistemas Soportados (SNES, Sega Mega Drive y SNK Neo Geo)](#2-sistemas-soportados-snes-sega-mega-drive-y-snk-neo-geo)
3. [Estructura de Carpetas y Diferenciación](#3-estructura-de-carpetas-y-diferenciación)
4. [Cómo Añadir y Gestionar Juegos (y Requisitos de BIOS Neo Geo)](#4-cómo-añadir-y-gestionar-juegos)
5. [Guía Multi-Plataforma: Cómo Jugar en Linux, Windows y Web](#5-guía-multi-plataforma-cómo-jugar-en-linux-windows-y-web)
6. [Menú Propio del Juego y Gestión de Carátulas](#6-menú-propio-del-juego-y-gestión-de-carátulas)
7. [Controles y Configuración de Mandos Multi-Consola](#7-controles-y-configuración-de-mandos-multi-consola)
8. [Durante la Partida: Menú de Pausa y Savestates](#8-durante-la-partida-menú-de-pausa-y-savestates)
9. [Arquitectura Interna y Abstracción de Plataformas](#9-arquitectura-interna-y-abstracción-de-plataformas)
10. [Preguntas Frecuentes y Cumplimiento Legal en GitHub](#10-preguntas-frecuentes)
11. [Versión WebAssembly en GitHub Pages](#11-versión-webassembly-en-github-pages)

---

## 1. ¿Qué es RetroDeck?

**RetroDeck** es una plataforma de juegos retro disponible para **Linux, Windows y Web** que reúne tres sistemas legendarios en una sola aplicación con motores nativos propios y una interfaz artística retro inspirada en los salones recreativos y consolas de los años 80 y 90:
* **Super Nintendo**: Núcleo C nativo (`libretrosnes.so` en Linux, `libretrosnes.dll` en Windows).
* **Sega Mega Drive / Genesis**: Núcleo C nativo (`libmegadrive_bridge.so` en Linux, `libmegadrive_bridge.dll` en Windows).
* **SNK Neo Geo (MVS / AES)**: Núcleo C nativo arcade (`libneogeo_bridge.so` en Linux, `libneogeo_bridge.dll` en Windows con FBAlpha 2012 Neo Geo).
* **Estética de los 80/90**: Cuadrícula neón en perspectiva 3D (estilo Mode 7 / synthwave) adaptada a cada sistema, cielo estrellado centelleante, chasis de máquinas arcade con tornillos remachados, distintivos originales (diamante de 4 colores de Super Famicom, sello ovalado dorado de 16-BIT de Mega Drive y placa dorada/roja Arcade de Neo Geo), LEDs luminosos, bahía iluminada para cartuchos 3D y simulación de pantalla CRT con cristal curvado.

---

## 2. Sistemas Soportados (SNES, Sega Mega Drive y SNK Neo Geo)

| Sistema | Fabricante | Extensiones de ROMs | Directorio de ROMs | BIOS Requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Super Nintendo** | Nintendo | `.smc`, `.sfc`, `.fig`, `.zip` | `roms/snes/` | No requerida |
| **Mega Drive / Genesis** | Sega | `.bin`, `.gen`, `.md`, `.smd`, `.zip` | `roms/megadrive/` | No requerida |
| **Neo Geo (MVS / AES)** | SNK | `.zip`, `.7z`, `.neo` | `roms/neogeo/` | `neogeo.zip` (Usuario) |

---

## 3. Estructura de Carpetas y Diferenciación

El repositorio está claramente separado para permitir jugar tanto en Linux, en Windows o en la web:

```text
Retro_Games/
│
├── RetroDeck.sh               # 🐧 Lanzador ejecutable para Linux
├── RetroDeck.desktop          # 🖥️ Lanzador para el escritorio Linux
├── RetroDeck.bat              # 🪟 Lanzador automático para Windows (doble clic)
├── RetroDeck.vbs              # 🪟 Lanzador silencioso sin consola para Windows
├── TUTORIAL.md                # 📘 Este manual de instrucciones
├── README.md                  # 📄 Resumen rápido y aviso legal del proyecto
├── .gitignore                 # 🛡️ Protección para Git (ignora ROMs, BIOS propietaria y saves)
│
├── windows/                   # 🪟 Utilidades exclusivas para Windows
│   ├── README.md              # 📖 Guía oficial de uso en Windows
│   ├── compile_cores.bat      # ⚙️ Script de compilación de DLLs con MinGW/GCC
│   └── build_exe.bat          # 📦 Generador de ejecutable portátil RetroDeck.exe
│
├── docs/                      # 🌐 Versión WebAssembly para GitHub Pages
│   ├── index.html             # 🕹️ Interfaz web del emulador arcade
│   ├── style.css              # 🎨 Estética synthwave y CRT web
│   ├── retrodeck-web.js       # ⚡ Motor WebAssembly y Gamepad API
│   └── assets/                # 📦 Demos homebrew y fuentes web
│
├── roms/
│   ├── snes/                  # 📂 ROMs de Super Nintendo (.smc, .sfc)
│   ├── megadrive/             # 📂 ROMs de Sega Mega Drive (.bin, .md, .gen)
│   └── neogeo/                # 📂 ROMs de SNK Neo Geo (.zip, .neo) + LEEME_BIOS.txt
│
├── boxart/
│   ├── snes/                  # 🖼️ Carátulas SNES (.png, .jpg, .webp)
│   ├── megadrive/             # 🖼️ Carátulas Mega Drive (.png, .jpg, .webp)
│   └── neogeo/                # 🖼️ Carátulas Neo Geo (.png, .jpg, .webp)
│
├── saves/
│   ├── snes/                  # 💾 Partidas de batería SNES (.srm)
│   ├── megadrive/             # 💾 Partidas de batería Mega Drive (.srm)
│   └── neogeo/                # 💾 Memoria SRAM Neo Geo
│
├── states/
│   ├── snes/                  # ⚡ Savestates rápidos SNES
│   ├── megadrive/             # ⚡ Savestates rápidos Mega Drive
│   └── neogeo/                # ⚡ Savestates rápidos Neo Geo
│
├── config/
│   ├── settings.json          # ⚙️ Mapeo de teclas, volumen, pantalla y preferencias
│   └── gamelist_cache.json    # 🗃️ Registro de favoritos y estadísticas
│
├── src/                       # 💻 Código fuente multiplataforma
│   ├── emulator_core/         # 🧠 Núcleos nativos C (SNES, Mega Drive y Neo Geo)
│   ├── ui/                    # 🎨 Menús, visor de cartuchos, controles y juego
│   └── core/                  # 🎛️ Gestores de entrada, plataformas, ROMs y sonido
│
└── assets/                    # 📦 Tipografía pixel, sonidos, iconos y capturas
    └── screenshots/           # 📸 Capturas de pantalla oficiales
```

---

## 4. Cómo Añadir y Gestionar Juegos

1. Copia tus juegos a la carpeta correspondiente de tu sistema:
   * Para SNES: `roms/snes/`
   * Para Mega Drive: `roms/megadrive/`
   * Para Neo Geo: `roms/neogeo/`
2. **Requisito de BIOS para SNK Neo Geo (MVS / AES):**
   * Debido a los derechos de autor de SNK Corporation y las políticas de GitHub, los archivos comerciales de BIOS (`neogeo.zip`) **no pueden alojarse en un repositorio público**.
   * Debes suministrar tu propio archivo `neogeo.zip` legal y colocarlo directamente en `roms/neogeo/neogeo.zip`.
   * El archivo `.gitignore` protege tu instalación para que nunca subas este archivo por accidente a GitHub.
   * Puedes consultar las especificaciones completas en [`roms/neogeo/LEEME_BIOS.txt`](file:///home/gasensio/Documentos/Retro_Games/roms/neogeo/LEEME_BIOS.txt).
   * Se incluye una demo homebrew de dominio público en `roms/neogeo/neogeo_demo.zip` para verificar el correcto funcionamiento del sistema.
3. Si tienes carátulas, colócalas en `boxart/<sistema>/` con el mismo nombre que la ROM (por ejemplo, `mslug.zip` -> `mslug.png`), o asígnalas interactivamente desde el **Menú del Juego (`[X]` o `[M]`)**.
4. **Reescanear en caliente:** Si copias nuevos juegos con el emulador ya en ejecución, puedes reescanear la biblioteca al instante desde el menú de Ajustes (**`[S]`** -> Opción *"Reescanear catálogo de ROMs"*).

---

## 5. Guía Multi-Plataforma: Cómo Jugar en Linux, Windows y Web

### 🐧 5.1. Cómo Jugar en Linux (Nativo)

1. Abre la terminal en el directorio del proyecto y dale permisos de ejecución:
   ```bash
   chmod +x RetroDeck.sh
   ```
2. Ejecuta el emulador:
   ```bash
   ./RetroDeck.sh
   ```
   *El script se encarga de crear el entorno virtual aislado `.venv` e instalar las dependencias (`pygame`) automáticamente.*
3. Para integrar un acceso directo en tu escritorio o menú de aplicaciones:
   ```bash
   cp RetroDeck.desktop ~/.local/share/applications/
   ```

---

### 🪟 5.2. Cómo Jugar en Windows (Nativo)

1. **Instalar Python:** Instala [Python 3.10 o superior](https://www.python.org/downloads/) asegurándote de marcar la casilla **`[X] Add python.exe to PATH`** en el instalador.
2. **Ejecución con doble clic:**
   * **`RetroDeck.bat`**: Haz doble clic para arrancar. Si es la primera vez, preparará automáticamente el entorno virtual `.venv` y descargará las librerías necesarias.
   * **`RetroDeck.vbs`**: Haz doble clic para iniciar la aplicación en segundo plano de forma silenciosa (sin que quede la ventana negra de CMD abierta).
3. **Mandos en Windows:** Conecta cualquier mando USB o Bluetooth de **Xbox** (XInput) o **PlayStation** (DirectInput con DS4Windows/Steam); se detecta automáticamente al iniciar.
4. **Empaquetar como `.exe`:** Haz doble clic en `windows\build_exe.bat` para compilar un ejecutable independiente `dist\RetroDeck\RetroDeck.exe` que puedes llevar en un pendrive sin necesitar Python.

---

### 🌐 5.3. Cómo Jugar en la Web (GitHub Pages / WebAssembly)

No requiere ninguna instalación en tu equipo:

1. Entra a: **`https://gasensios.github.io/RetroDeck/`**
2. **Jugar al instante:**
   * Haz clic sobre las demos integradas (**Astrohawk** o **BombX**) para jugar de inmediato.
   * O **arrastra cualquier ROM** (`.smc`, `.sfc`, `.bin`, `.gen`, `.md`) desde tu ordenador a la ventana del navegador. La ROM se carga en memoria y nunca se transmite a internet.
3. Puedes conectar tu mando USB o Bluetooth al ordenador y el navegador lo detectará mediante la *Web Gamepad API*.

---

### 🔄 Alternar entre Consolas en los Menús (SNES, Mega Drive y Neo Geo)
- Pulsa la tecla **`[TAB]`** o pulsa los botones superiores **`[L]` / `[R]`** en tu mando.
- También puedes hacer clic sobre las pestañas **`[★ SNES]`**, **`[★ MEGADRIVE]`** y **`[★ NEOGEO]`** en la parte superior derecha.
- Toda la interfaz cambiará de forma instantánea de colores temáticos, cartucho 3D (gris clásico SNES, negro curvo Mega Drive o masivo arcade MVS/AES Neo Geo) y lista de juegos.

---

## 6. Menú Propio del Juego y Gestión de Carátulas

Cada juego dispone de un **Menú Propio de Configuración** con estética de máquina arcade de los años 80-90. En este menú puedes personalizar la carátula, gestionar partidas de batería (.srm) y consultar estadísticas.

### 🕹️ Cómo acceder al Menú del Juego:
* **Mando**: Selecciona el juego en el catálogo y pulsa el botón **`[X]`** (o el botón asignado a acción secundaria).
* **Teclado**: Pulsa **`[M]`** o **`[O]`** sobre el juego seleccionado.
* **Ratón**: Haz clic directo sobre el panel lateral de detalles o sobre el cartucho 3D.

### 🎨 Opciones disponibles en el Menú:
1. **`>> INICIAR JUEGO <<`**: Lanza la ROM de inmediato.
2. **`Favorito: [★ SI / No]`**: Marca el juego para que aparezca con estrella dorada y al inicio del catálogo.
3. **`Asignar Carátula (Selector de Archivos)`**: Abre un explorador de archivos nativo del sistema operativo (Zenity/KDialog en Linux, diálogo nativo de Windows o macOS) para elegir cualquier imagen de tu disco duro.
   * **Formatos soportados:** `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`.
   * La carátula se vincula automáticamente al juego y se renderiza en tiempo real sobre la pegatina del cartucho 3D.
4. **`Abrir Carpeta de Carátulas (boxart/)`**: Abre la carpeta `boxart/<sistema>/` en tu gestor de archivos para arrastrar imágenes por lotes.
5. **`Quitar Carátula Personalizada`**: Restaura el cartucho a su diseño original con tipografía serigrafiada retro.
6. **`Crear Copia de Seguridad (Backup Partida)`**: Crea un duplicado con fecha y hora de la pila de guardado (`.srm`), ideal antes de un combate difícil o para conservar partidas históricas.
7. **`Borrar Partida de Batería (Reiniciar Save)`**: Elimina el `.srm` si deseas comenzar una partida completamente desde cero.
8. **`Abrir Carpeta de la ROM (roms/)`**: Abre la ubicación física de la ROM en el explorador de archivos del sistema.
9. **`Resetear Estadísticas de Juego`**: Restablece el contador de partidas jugadas de este título.

---

## 7. Controles y Configuración de Mandos Multi-Consola

RetroDeck permite personalizar los controles **de forma independiente para cada consola** (Super Nintendo, Sega Mega Drive y SNK Neo Geo), tanto para teclado como para mandos USB / Gamepads:

### ⚙️ Cómo configurar controles:
1. Pulsa **`[C]`** desde el explorador de juegos (se abrirá automáticamente con la consola que estés explorando).
2. **Selecciona la consola a configurar**: Pulsa **`[TAB]`** (o los gatillos **`[L]` / `[R]`**) o haz clic en las pestañas superiores **`[★ SNES]`**, **`[★ MEGA DRIVE]`** y **`[★ NEO GEO]`**.
3. **Selecciona el dispositivo**: Pulsa **`[◄]`** o **`[►]`** para alternar entre **`⌨ TECLADO`** y **`🎮 MANDO / GAMEPAD`**.
4. **Elige el botón a mapear**: Navega con **`[Arriba]`** y **`[Abajo]`**. A la derecha verás el diagrama de la consola activa (**mando SNES**, **pad 6 botones Mega Drive** o **Arcade Stick 4 botones de Neo Geo**) iluminando en dorado el botón seleccionado.
5. **Reasignar**: Pulsa **`[Enter]`** o **`[A]`** y luego pulsa la nueva tecla o botón físico.
6. **Restaurar valores de fábrica**: Pulsa **`[X]`** o **`[S]`** para restablecer la configuración de la consola y dispositivo actuales.
7. **Guardar y volver**: Pulsa **`[Escape]`** o **`[B]`**.

---

### 🕹️ Mapeo por Defecto para Super Nintendo (SNES)
* **Cruceta (D-PAD)**: Flechas de dirección (`▲`, `▼`, `◄`, `►`)
* **Botones frontales en rombo**:
  * `B` (Inferior): `Z` (en teclado) / `Botón 0` (A en Xbox / Cruz en PS)
  * `A` (Derecha): `X` (en teclado) / `Botón 1` (B en Xbox / Círculo en PS)
  * `Y` (Izquierda): `A` (en teclado) / `Botón 2` (X en Xbox / Cuadrado en PS)
  * `X` (Superior): `S` (en teclado) / `Botón 3` (Y en Xbox / Triángulo en PS)
* **Gatillos**: `L` = `Q` (Botón 4) / `R` = `W` (Botón 5)
* **Control**: `Start` = `Enter` (Botón 7) / `Select` = `Shift Derecho` (Botón 6)

---

### 🕹️ Mapeo por Defecto para Sega Mega Drive / Genesis
* **Cruceta (D-PAD)**: Flechas de dirección (`▲`, `▼`, `◄`, `►`)
* **Fila inferior (3 botones clásicos)**:
  * `A` (Acción 1 / Especial): `A` (en teclado) / `Botón 2` (X en Xbox / Cuadrado en PS)
  * `B` (Acción 2 / Ataque): `S` (en teclado) / `Botón 0` (A en Xbox / Cruz en PS)
  * `C` (Acción 3 / Salto): `D` (en teclado) / `Botón 1` (B en Xbox / Círculo en PS)
  *(Disposición natural y ergonómica de tres dedos correlativos: A, S, D)*
* **Fila superior (Mando de 6 botones)**:
  * `X`: `Q` (en teclado) / `Botón 3` (Y en Xbox / Triángulo en PS)
  * `Y`: `W` (en teclado) / `Botón 4` (Gatillo L1)
  * `Z`: `E` (en teclado) / `Botón 5` (Gatillo R1)
* **Control**: `Start` = `Enter` (Botón 7) / `Mode` = `Shift Derecho` (Botón 6)

---

### 🕹️ Mapeo por Defecto para SNK Neo Geo (Arcade Stick)
* **Palanca Arcade (8 direcciones)**: Flechas de dirección (`▲`, `▼`, `◄`, `►`)
* **Disposición en arco arcade de 4 botones**:
  * `A` (Rojo / Golpe débil): `A` (en teclado) / `Botón 0` (A en Xbox / Cruz en PS)
  * `B` (Amarillo / Patada débil): `S` (en teclado) / `Botón 1` (B en Xbox / Círculo en PS)
  * `C` (Verde / Golpe fuerte): `D` (en teclado) / `Botón 2` (X en Xbox / Cuadrado en PS)
  * `D` (Azul / Patada fuerte): `F` (en teclado) / `Botón 3` (Y en Xbox / Triángulo en PS)
* **Control**: `1P Start` = `Enter` (Botón 7) / `Coin / Select` = `Shift Derecho` (Botón 6)

---

### Atajos Globales en los Menús
* **`[TAB]` o `[L / R]`**: Cambiar consola activa (**SNES <-> MEGA DRIVE <-> NEO GEO**).
* **`[C]`**: Abrir configuración de controles con diagramas interactivos específicos.
* **`[A]`, `[Enter]` o `[Espacio]`**: Iniciar la ROM seleccionada.
* **`[F3]`**: Activar / desactivar contador de FPS en tiempo real con monitor de estabilidad.
* **`[X]` o `[M]`**: Abrir el Menú Propio del Juego (Gestión de carátulas, backups SRAM, estadísticas).
* **`[Y]`**: Marcar o desmarcar juego como Favorito (estrella dorada).
* **`[S]`**: Ajustes generales (Tamaño de fuente para portátiles, tipografía HD / Pixel Retro, contador FPS, filtro CRT scanlines, scanlines en menús, intensidad, volumen).
* **`[H]` o `[F1]`**: Ayuda interactiva integrada.
* **`[F11]` o `[Alt + Enter]`**: Alternar Pantalla Completa / Modo Ventana (a resolución nativa de monitor).

---

## 8. Durante la Partida: Menú de Pausa y Savestates

En los tres sistemas soportados (SNES, Mega Drive y Neo Geo):
* **`[F3]`**: Alternar el visor de FPS en tiempo real en la esquina superior (verde = 60 FPS fijos, amarillo/rojo = caídas).
* **`[F5]`**: Guardar Estado Rápido (*Savestate* instantáneo).
* **`[F7]`**: Cargar Estado Rápido (*Load State* instantáneo).
* **`[F11]` o `[Alt + Enter]`**: Alternar entre pantalla completa y ventana en mitad de la partida.
* **`[ESC]`**: Abre el **Menú de Pausa retro** con opciones de continuar, guardar, cargar, contador FPS, alternar pantalla completa, reiniciar consola o salir de forma segura.
* Las partidas con pila interna (batería SRAM) se guardan en sus respectivas carpetas `saves/snes/`, `saves/megadrive/` y `saves/neogeo/`.

---

## 9. Arquitectura Interna y Abstracción de Plataformas

RetroDeck está construido para maximizar el rendimiento y la fidelidad mediante un diseño desacoplado:
* **Núcleo SNES (`libretrosnes.so` / `libretrosnes.dll`)**: Compilado en C nativo. Emula la CPU 65816, la PPU con todos los modos gráficos (incluido Mode 7 con rotación y zoom) y el procesador de sonido SPC700 con DSP de 8 canales. Proporciona una superficie de 512x480 a 60 FPS.
* **Núcleo Mega Drive (`libmegadrive_bridge.so` / `libmegadrive_bridge.dll`)**: Compilado en C nativo con Genesis Plus GX. Emula la CPU Motorola 68000 a 7.6 MHz, el chip de audio dual Yamaha YM2612 (FM) + TI SN76489 (PSG) y el procesador VDP con planos de scroll A y B.
* **Núcleo Neo Geo (`libneogeo_bridge.so` / `libneogeo_bridge.dll`)**: Compilado en C nativo con FBAlpha 2012 Neo Geo. Emula la CPU dual Motorola 68000 (12 MHz) + Zilog Z80 (4 MHz), chip de sonido Yamaha YM2610 stereo (FM + ADPCM), paleta de 65.536 colores y sprites ilimitados sin parpadeo a 60 FPS reales.
* **Módulo de Abstracción Multiplataforma (`src/core/platform_utils.py`)**: Detecta automáticamente el sistema operativo (Windows, Linux, macOS) para resolver diálogos nativos de archivos, apertura de carpetas en el explorador del sistema y resolución de nombres de librerías dinámicas (`.dll` vs `.so`).
* **Integración Pygame con Ctypes**: Puente de datos de alta velocidad en memoria compartida, streaming directo de audio PCM estéreo y post-procesado CRT y scanlines en tiempo real.

---

## 10. Preguntas Frecuentes y Cumplimiento Legal en GitHub

**¿Por qué no viene incluida la BIOS de Neo Geo (`neogeo.zip`)?**  
Las ROMs de la BIOS de SNK Neo Geo son propiedad intelectual registrada de SNK CORPORATION. Alojar o distribuir estos archivos en un repositorio público de GitHub violaría la DMCA y los Términos de Servicio de GitHub. Por este motivo, el repositorio incluye un `.gitignore` estricto y un manual de instrucciones (`roms/neogeo/LEEME_BIOS.txt`) para que cada usuario pueda suministrar su propia copia obtenida legalmente.

**¿Puedo usar imágenes `.webp` o `.jpg` para las carátulas?**  
Sí, el menú de cada juego soporta `.png`, `.jpg`, `.jpeg`, `.webp` y `.bmp`. Además puedes asignarlas seleccionándolas con el diálogo nativo de archivos del sistema operativo o colocándolas en `boxart/<sistema>/`.

**¿Cómo restauro los controles originales si me equivoco al mapear?**  
Entra a Controles con **`[C]`**, elige la consola y el dispositivo (Teclado o Mando) y pulsa **`[X]`** o **`[S]`** para restaurar los valores por defecto.

**¿Se pierden mis partidas si reinstalo o cambio carátulas?**  
No. Todas las partidas en pila (`.srm`) están a salvo en la carpeta `saves/`. Además, desde el menú del juego puedes crear copias de seguridad de tus partidas en cualquier momento.

**¿Es seguro subir este proyecto a GitHub?**  
Sí, es 100% legal. Los núcleos de emulación son de código abierto (GPL-2.0) y el repositorio está blindado mediante `.gitignore` para excluir cualquier archivo protegido por derechos de autor (ROMs comerciales, BIOS propietarias y volcados de memoria).

---

## 11. Versión WebAssembly en GitHub Pages

RetroDeck incluye una versión web completa optimizada para navegadores web mediante **WebAssembly (WASM)**.

### 🌐 Características de la versión Web:
* **Enlace público:** `https://gasensios.github.io/RetroDeck/`
* **Arrastrar y soltar ROMs (Drag & Drop):** Puedes arrastrar cualquier archivo `.smc`, `.sfc`, `.bin`, `.gen`, `.md` directamente a la pantalla del emulador. La ROM se carga en la memoria del navegador y nunca se transmite a ningún servidor.
* **Demos integradas:** Incluye los juegos homebrew *Astrohawk* (SNES) y *BombX* (Mega Drive) listos para jugar sin archivos externos.
* **Mandos USB y Bluetooth:** Reconoce automáticamente mandos de Xbox, PlayStation o mandos retro mediante la *Web Gamepad API*.
* **Filtro CRT:** Botón en la barra arcade inferior para activar/desactivar el filtro de líneas de escaneado en tiempo real.

### 🚀 Despliegue en GitHub Pages:
1. Sube tu código a `https://github.com/gasensios/RetroDeck`.
2. En GitHub, ve a **Settings** > **Pages**.
3. En **Build and deployment > Source**, selecciona **Deploy from a branch** con rama `main` y carpeta `/docs` -> Pulsa **Save**.
