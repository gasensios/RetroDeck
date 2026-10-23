# 📘 Manual de Usuario y Funcionamiento Interno de RetroDeck

¡Bienvenido a **RetroDeck**! Esta estación de emulación retro soporta de forma nativa **Super Nintendo (SNES)** y **Sega Mega Drive / Genesis** mediante motores propios en C y un frontend interactivo en Python/Pygame.

---

## 📑 Índice de Contenidos

1. [¿Qué es RetroDeck?](#1-qué-es-retrodeck)
2. [Sistemas Soportados (SNES y Sega Mega Drive)](#2-sistemas-soportados-snes-y-sega-mega-drive)
3. [Estructura de Carpetas Multi-Sistema](#3-estructura-de-carpetas-multi-sistema)
4. [Cómo Añadir y Gestionar Juegos](#4-cómo-añadir-y-gestionar-juegos)
5. [Cómo Ejecutar y Cambiar de Sistema](#5-cómo-ejecutar-y-cambiar-de-sistema)
6. [Menú Propio del Juego y Gestión de Carátulas](#6-menú-propio-del-juego-y-gestión-de-carátulas)
7. [Controles y Configuración de Mandos](#7-controles-y-configuración-de-mandos)
8. [Durante la Partida: Menú de Pausa y Savestates](#8-durante-la-partida-menú-de-pausa-y-savestates)
9. [Arquitectura Interna de los Núcleos C](#9-arquitectura-interna-de-los-núcleos-c)
10. [Preguntas Frecuentes](#10-preguntas-frecuentes)
11. [Versión WebAssembly en GitHub Pages](#11-versión-webassembly-en-github-pages)

---

## 1. ¿Qué es RetroDeck?

**RetroDeck** es una plataforma de juegos retro para **Linux** que reúne dos consolas históricas de 16 bits en una sola aplicación con motores nativos propios y una interfaz artística retro inspirada en los salones recreativos y consolas de los años 80 y 90:
* **Super Nintendo**: Núcleo C nativo (`libretrosnes.so`).
* **Sega Mega Drive / Genesis**: Núcleo C nativo (`libmegadrive_bridge.so`).
* **Estética de los 80/90**: Cuadrícula neón en perspectiva 3D (estilo Mode 7 / synthwave) con cielo estrellado centelleante, chasis de máquinas arcade con tornillos remachados, distintivos originales (diamante de 4 colores de Super Famicom y sello ovalado dorado de 16-BIT de Mega Drive), LEDs de hardware luminosos, ranura iluminada para cartuchos 3D y simulación de pantalla CRT con cristal curvado.

---

## 2. Sistemas Soportados (SNES y Sega Mega Drive)

| Sistema | Compañía | Extensiones de ROMs | Directorio de ROMs |
| :--- | :--- | :--- | :--- |
| **Super Nintendo** | Nintendo | `.smc`, `.sfc`, `.fig`, `.zip` | `roms/snes/` |
| **Mega Drive / Genesis** | Sega | `.bin`, `.gen`, `.md`, `.smd`, `.zip` | `roms/megadrive/` |

---

## 3. Estructura de Carpetas Multi-Sistema

```text
Retro_Games/
│
├── RetroDeck.sh               # 🚀 Script ejecutable del emulador
├── RetroDeck.desktop          # 🖥️ Lanzador para el escritorio Linux
├── TUTORIAL.md                # 📘 Este manual de instrucciones
├── README.md                  # 📄 Resumen rápido y aviso legal del proyecto
├── .gitignore                 # 🛡️ Protección para Git (ignora ROMs, saves y binarios)
│
├── docs/                      # 🌐 Versión WebAssembly para GitHub Pages
│   ├── index.html             # 🕹️ Interfaz web del emulador
│   ├── style.css              # 🎨 Estética synthwave y CRT web
│   ├── retrodeck-web.js       # ⚡ Motor WebAssembly y Gamepad API
│   └── assets/                # 📦 Demos homebrew y fuentes web
│
├── roms/
│   ├── snes/                  # 📂 ROMs de Super Nintendo (.smc, .sfc)
│   └── megadrive/             # 📂 ROMs de Sega Mega Drive (.bin, .md, .gen)
│
├── boxart/
│   ├── snes/                  # 🖼️ Carátulas SNES (.png o .jpg)
│   └── megadrive/             # 🖼️ Carátulas Mega Drive (.png o .jpg)
│
├── saves/
│   ├── snes/                  # 💾 Partidas de batería SNES (.srm)
│   └── megadrive/             # 💾 Partidas de batería Mega Drive (.srm)
│
├── states/
│   ├── snes/                  # ⚡ Savestates rápidos SNES
│   └── megadrive/             # ⚡ Savestates rápidos Mega Drive
│
├── config/
│   ├── settings.json          # ⚙️ Mapeo de teclas, volumen, pantalla y preferencias
│   └── gamelist_cache.json    # 🗃️ Registro de favoritos y estadísticas
│
├── src/                       # 💻 Código fuente
│   ├── emulator_core/         # 🧠 Núcleos nativos C (SNES y Mega Drive)
│   ├── ui/                    # 🎨 Menús, visor de cartuchos, controles y juego
│   └── core/                  # 🎛️ Gestores de entrada, sistemas y sonido
│
└── assets/                    # 📦 Tipografía pixel, sonidos, iconos y capturas
    └── screenshots/           # 📸 Capturas de pantalla de la interfaz
```

---

## 4. Cómo Añadir y Gestionar Juegos

1. Copia tus juegos a la carpeta correspondiente:
   * Para SNES: `roms/snes/`
   * Para Mega Drive: `roms/megadrive/`
2. Si tienes carátulas, colócalas en `boxart/snes/` o `boxart/megadrive/` con el mismo nombre que la ROM (por ejemplo, `Sonic.bin` -> `Sonic.png`).
3. **Reescanear en caliente:** Si copias nuevos juegos con el emulador ya en ejecución, puedes reescanear la biblioteca al instante desde el menú de Ajustes (**`[S]`** -> Opción *"Reescanear catálogo de ROMs"*) o pulsando **`[A]`** en el catálogo de juegos.

---

## 5. Cómo Ejecutar y Cambiar de Sistema

Ejecuta el programa:
```bash
./RetroDeck.sh
```

### 🔄 Alternar entre Super Nintendo y Mega Drive
- Pulsa la tecla **`[TAB]`** o pulsa los botones superiores **`[L]` / `[R]`** en tu mando.
- También puedes hacer clic sobre las pestañas **`[★ SNES]`** y **`[★ MEGADRIVE]`** en la parte superior derecha.
- Toda la interfaz cambiará de forma instantánea de colores temáticos, cartucho (gris SNES o negro Mega Drive) y lista de juegos.

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
3. **`Asignar Carátula (Selector de Archivos)`**: Abre un explorador de archivos nativo de Linux (`zenity`) para elegir cualquier imagen de tu disco duro.
   * **Formatos soportados:** `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`.
   * La carátula se vincula automáticamente al juego y se renderiza en tiempo real sobre la pegatina del cartucho 3D.
4. **`Abrir Carpeta de Carátulas (boxart/)`**: Abre la carpeta `boxart/snes/` o `boxart/megadrive/` en tu gestor de ventanas Linux para arrastrar imágenes por lotes.
5. **`Quitar Carátula Personalizada`**: Restaura el cartucho a su diseño original con tipografía serigrafiada retro.
6. **`Crear Copia de Seguridad (Backup Partida)`**: Crea un duplicado con fecha y hora de la pila de guardado (`.srm`), ideal antes de un combate difícil o para conservar partidas históricas.
7. **`Borrar Partida de Batería (Reiniciar Save)`**: Elimina el `.srm` si deseas comenzar una partida completamente desde cero.
8. **`Abrir Carpeta de la ROM (roms/)`**: Abre la ubicación física de la ROM en el sistema operativo.
9. **`Resetear Estadísticas de Juego`**: Restablece el contador de partidas jugadas de este título.

---

## 7. Controles y Configuración de Mandos Multi-Consola

RetroDeck permite personalizar los controles **de forma independiente para cada consola** (Super Nintendo y Sega Mega Drive), tanto para teclado como para mandos USB / Gamepads:

### ⚙️ Cómo configurar controles:
1. Pulsa **`[C]`** desde el explorador de juegos (se abrirá automáticamente con la consola que estés explorando).
2. **Selecciona la consola a configurar**: Pulsa **`[TAB]`** (o los gatillos **`[L]` / `[R]`**) o haz clic en las pestañas superiores **`[★ SNES]`** y **`[★ MEGA DRIVE]`**.
3. **Selecciona el dispositivo**: Pulsa **`[◄]`** o **`[►]`** para alternar entre **`⌨ TECLADO`** y **`🎮 MANDO / GAMEPAD`**.
4. **Elige el botón a mapear**: Navega con **`[Arriba]`** y **`[Abajo]`**. A la derecha verás el diagrama de la consola activa (**mando SNES** o **mando de 6 botones de Mega Drive**) iluminando en dorado el botón seleccionado.
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

### Atajos Globales en los Menús
* **`[TAB]` o `[L / R]`**: Cambiar consola activa (SNES <-> Mega Drive).
* **`[C]`**: Abrir configuración de controles con diagrama retro.
* **`[A]` o `[Enter]`**: Iniciar la ROM seleccionada.
* **`[X]` o `[M]`**: Abrir el Menú Propio del Juego (Gestión de carátulas, backups SRAM, estadísticas).
* **`[Y]`**: Marcar o desmarcar juego como Favorito (estrella dorada).
* **`[S]`**: Ajustes generales (Filtro CRT scanlines, intensidad, volumen).
* **`[H]` o `[F1]`**: Ayuda interactiva integrada.
* **`[F11]`**: Alternar Pantalla Completa.

---

## 8. Durante la Partida: Menú de Pausa y Savestates

Tanto en Super Nintendo como en Sega Mega Drive:
* **`[F5]`**: Guardar Estado Rápido (*Savestate* instantáneo).
* **`[F7]`**: Cargar Estado Rápido (*Load State* instantáneo).
* **`[ESC]`**: Abre el **Menú de Pausa retro** para continuar, guardar, cargar, reiniciar o salir de forma segura.
* Las partidas con pila interna (batería SRAM) se guardan en sus respectivas carpetas `saves/snes/` y `saves/megadrive/` en formato `.srm`.

---

## 9. Arquitectura Interna de los Núcleos C

RetroDeck está construido para maximizar el rendimiento y la fidelidad sin requerir binarios externos pesados:
* **Núcleo SNES (`libretrosnes.so`)**: Compilado en C nativo. Emula la CPU 65816, la PPU con todos los modos gráficos (incluido Mode 7 con rotación y zoom) y el procesador de sonido SPC700 con DSP de 8 canales. Proporciona una superficie de 512x480 a 60 FPS.
* **Núcleo Mega Drive (`libmegadrive_bridge.so`)**: Compilado en C nativo con Genesis Plus GX. Emula la CPU Motorola 68000 a 7.6 MHz, el chip de audio dual Yamaha YM2612 (FM) + TI SN76489 (PSG) y el procesador VDP con planos de scroll A y B.
* **Integración Pygame con Ctypes**: Puente de datos de alta velocidad en memoria compartida, permitiendo post-procesado CRT y scanlines en tiempo real.

---

## 10. Preguntas Frecuentes

**¿Puedo usar imágenes `.webp` o `.jpg` para las carátulas?**  
Sí, el menú de cada juego soporta `.png`, `.jpg`, `.jpeg`, `.webp` y `.bmp`. Además puedes asignarlas seleccionándolas con el diálogo de archivos (`zenity`) o colocándolas en `boxart/<sistema>/`.

**¿Cómo restauro los controles originales si me equivoco al mapear?**  
Entra a Controles con **`[C]`**, elige la consola y el dispositivo (Teclado o Mando) y pulsa **`[X]`** o **`[S]`** para restaurar los valores por defecto.

**¿Se pierden mis partidas si reinstalo o cambio carátulas?**  
No. Todas las partidas en pila (`.srm`) están a salvo en la carpeta `saves/`. Además, desde el menú del juego puedes crear copias de seguridad de tus partidas en cualquier momento.

**¿Es seguro subir este proyecto a GitHub?**  
Sí, es completamente legal. La emulación de consolas mediante ingeniería inversa de hardware es legítima. El proyecto ya cuenta con un archivo `.gitignore` configurado para omitir automáticamente cualquier ROM comercial, imagen de carátula con derechos de autor o partida privada, garantizando que el repositorio solo comparta código fuente de acceso libre.

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
