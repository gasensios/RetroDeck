# 🎮 RetroDeck - Estación de Emulación Multi-Sistema (Linux, Windows y Web)

**RetroDeck** es una plataforma de juegos retro para **Super Nintendo (SNES)**, **Sega Mega Drive / Genesis** y **SNK Neo Geo (MVS / AES)** completamente **autónoma, multiplataforma y multi-sistema**, con motores de emulación propios en C de alto rendimiento y una interfaz gráfica artística inspirada en los salones recreativos (Arcade) y consolas de los años 80 y 90 (fondo Mode 7 neón en perspectiva, chasis metálico con tornillos remachados, badges oficiales y bahía de cartuchos 3D).

El proyecto está diseñado y diferenciado para disfrutarse en **tres plataformas principales**:
1. 🐧 **Versión Linux (Nativa):** Máximo rendimiento mediante núcleos en C (`.so`) y lanzador interactivo.
2. 🪟 **Versión Windows (Nativa):** Doble clic con instalador virtual integrado (`.bat` / `.vbs`) y opción de empaquetado a `.exe`.
3. 🌐 **Versión Web (GitHub Pages):** Ejecución instantánea en el navegador a 60 FPS mediante WebAssembly sin instalar nada.

> 🌐 **¿Quieres jugar ahora mismo desde tu navegador?**  
> ¡Prueba la versión WebAssembly online sin descargar nada!  
> 🕹️ **[Jugar a RetroDeck Web Online](https://gasensios.github.io/RetroDeck/)**

---

## 🌟 Sistemas Soportados

| Consola / Sistema | Fabricante | Extensiones Soportadas | Resolución Nativa | Aspecto |
| :--- | :--- | :--- | :--- | :--- |
| **Super Nintendo (SNES)** | Nintendo | `.smc`, `.sfc`, `.fig`, `.zip` | 512×480 | 4:3 CRT |
| **Mega Drive / Genesis** | Sega | `.bin`, `.gen`, `.md`, `.smd`, `.zip` | 320×224 | 4:3 CRT |
| **Neo Geo (MVS / AES)** | SNK | `.zip`, `.7z`, `.neo` | 320×224 | 4:3 Arcade |

> ℹ️ **Nota de BIOS para Neo Geo:** Por estricto cumplimiento legal con los derechos de autor de SNK y los Términos de Servicio de GitHub, la BIOS propietaria de Neo Geo (`neogeo.zip`) **no se incluye en este repositorio**. Para jugar a juegos de Neo Geo, debes colocar tu archivo legítimo `neogeo.zip` en la carpeta `roms/neogeo/` (consulta [`roms/neogeo/LEEME_BIOS.txt`](file:///home/gasensio/Documentos/Retro_Games/roms/neogeo/LEEME_BIOS.txt)). Se incluye una demo homebrew libre en `roms/neogeo/neogeo_demo.zip` para verificación.

---

## 📁 Estructura del Repositorio y Diferenciación Multiplataforma

```text
Retro_Games/
│
├── RetroDeck.sh               # 🐧 Lanzador ejecutable nativo para Linux
├── RetroDeck.desktop          # 🖥️ Lanzador para el escritorio Linux
├── RetroDeck.bat              # 🪟 Lanzador automático para Windows (doble clic)
├── RetroDeck.vbs              # 🪟 Lanzador silencioso sin consola para Windows
├── TUTORIAL.md                # 📘 Manual completo de uso y arquitectura
├── README.md                  # 📄 Ficha técnica y guía multiplataforma
├── .gitignore                 # 🛡️ Protección de Git (ignora ROMs comerciales, BIOS y saves)
│
├── windows/                   # 🪟 Utilidades exclusivas para Windows
│   ├── README.md              # 📖 Guía rápida para usuarios de Windows
│   ├── compile_cores.bat      # ⚙️ Script de compilación de DLLs con MinGW/GCC
│   └── build_exe.bat          # 📦 Generador de ejecutable portátil RetroDeck.exe
│
├── docs/                      # 🌐 Versión WebAssembly para GitHub Pages
│   ├── index.html             # 🕹️ Interfaz web del emulador arcade
│   ├── style.css              # 🎨 Estética synthwave y filtro CRT web
│   ├── retrodeck-web.js       # ⚡ Motor WebAssembly y Gamepad API
│   └── assets/                # 📦 Demos homebrew y fuentes web
│
├── roms/
│   ├── snes/                  # 📂 Juegos de Super Nintendo (.smc, .sfc)
│   ├── megadrive/             # 📂 Juegos de Sega Mega Drive (.bin, .md, .gen)
│   └── neogeo/                # 📂 Juegos de SNK Neo Geo (.zip, .neo) + LEEME_BIOS.txt
│
├── boxart/
│   ├── snes/                  # 🖼️ Carátulas de SNES (.png, .jpg, .webp)
│   ├── megadrive/             # 🖼️ Carátulas de Mega Drive (.png, .jpg, .webp)
│   └── neogeo/                # 🖼️ Carátulas de Neo Geo (.png, .jpg, .webp)
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
├── src/
│   ├── emulator_core/         # 🧠 Motores nativos C (SNES, Mega Drive y Neo Geo)
│   ├── ui/                    # 🎨 Menús, selector de consola, controles y visor
│   └── core/                  # 🎛️ Gestores de entrada, plataformas, ROMs y sonido
└── assets/                    # 📦 Fuentes, sonidos retro, iconos y capturas
    └── screenshots/           # 📸 Capturas de pantalla oficiales
```

---

## 🚀 Cómo Jugar en Cada Versión

### 🐧 1. Cómo Jugar en Linux (Nativo)

1. Abre tu terminal en la carpeta del proyecto y dale permisos al lanzador (solo la primera vez):
   ```bash
   chmod +x RetroDeck.sh
   ```
2. Ejecuta el programa:
   ```bash
   ./RetroDeck.sh
   ```
   *El script creará automáticamente el entorno virtual `.venv` e instalará dependencias si no existen.*
3. Si lo prefieres, copia el archivo `RetroDeck.desktop` a tu escritorio o a `~/.local/share/applications/` para tener un acceso directo en el menú de aplicaciones de tu distribución Linux.

---

### 🪟 2. Cómo Jugar en Windows (Nativo)

1. **Requisito:** Tener instalado [Python 3.10 o superior](https://www.python.org/downloads/) asegurándote de marcar la casilla **`[X] Add python.exe to PATH`** durante la instalación.
2. **Para jugar al instante:**
   * Haz doble clic sobre **`RetroDeck.bat`** (creará el entorno `.venv` e instalará `pygame` automáticamente la primera vez).
   * O haz doble clic sobre **`RetroDeck.vbs`** para jugar en modo silencioso sin que quede abierta la ventana negra de la consola CMD de Windows.
3. **Mandos en Windows:** Conecta cualquier mando de Xbox (One/Series XInput), PlayStation (DualShock/DualSense) o 8BitDo; se reconocen automáticamente al arrancar.
4. **Empaquetar como `.exe` portátil (Opcional):**
   * Haz doble clic en `windows\build_exe.bat` para compilar un `RetroDeck.exe` totalmente autónomo dentro de la carpeta `dist\RetroDeck\`.
5. Para más detalles técnicos sobre Windows, consulta [`windows/README.md`](file:///home/gasensio/Documentos/Retro_Games/windows/README.md).

---

### 🌐 3. Cómo Jugar en la Web (GitHub Pages / WebAssembly)

No requiere descargar ni instalar absolutamente nada en tu ordenador:

1. Entra con tu navegador (Chrome, Firefox, Edge, Safari o navegadores móviles) a:  
   👉 **`https://gasensios.github.io/RetroDeck/`**
2. **Cargar juegos:**
   * Haz clic sobre las demos de la pantalla (**`ASTROHAWK`** para SNES o **`BOMBX`** para Mega Drive) para jugar de inmediato.
   * O **arrastra y suelta tu propio archivo de ROM** (`.smc`, `.sfc`, `.bin`, `.gen`, `.md`, `.zip`) sobre la ventana. La ROM se carga 100% en la memoria de tu navegador y nunca se sube a internet.
3. Conecta tu mando USB o Bluetooth para jugar con mando físico en el navegador mediante la *Web Gamepad API*.

---

### 🔄 Controles y Navegación en los Menús (Común a Desktop)
- **`[TAB]`** (o los gatillos **`[L]` / `[R]`** en mando): Alternar consola activa (**SNES <-> MEGA DRIVE <-> NEO GEO**).
- **`[A]`, `[ENTER]` o `[ESPACIO]`**: Iniciar el juego seleccionado.
- **`[F3]`**: Activar / desactivar contador de FPS en tiempo real con indicador LED de rendimiento.
- **`[F11]` o `[ALT + ENTER]`**: Alternar entre Pantalla Completa y Modo Ventana.
- **`[X]` o `[M]`**: Abrir el **Menú Propio del Juego** (asignación de carátulas en múltiples formatos, copias de seguridad de partidas `.srm` y estadísticas).
- **`[C]`**: Abrir la configuración interactiva de mandos con diagrama retro y vista previa específica para cada consola (mando SNES, pad 6 botones Mega Drive o Arcade Stick Neo Geo).
- **`[S]`**: Menú de Ajustes generales (tamaño de fuente para portátiles, estilo HD/Pixel, contador FPS, filtro CRT scanlines, volumen, etc.).
- **`[H]` o `[F1]`**: Guía rápida y ayuda en pantalla.

---

## 🎮 Controles por Defecto en Juego (Teclado)

* **Super Nintendo (SNES):**
  - D-Pad: Flechas de dirección
  - Botones B, A, Y, X: `Z`, `X`, `A`, `S`
  - Gatillos L / R: `Q`, `W`
  - Select / Start: `R-SHIFT`, `ENTER`
* **Sega Mega Drive (6 Botones):**
  - D-Pad: Flechas de dirección
  - Fila Inferior (A, B, C): `A`, `S`, `D`
  - Fila Superior (X, Y, Z): `Q`, `W`, `E`
  - Start / Mode: `ENTER`, `R-SHIFT`
* **SNK Neo Geo (Arcade Stick 4 Botones):**
  - Palanca Arcade: Flechas de dirección
  - Botones Arcade (A, B, C, D): `A`, `S`, `D`, `F`
  - 1P Start / Coin (Select): `ENTER`, `R-SHIFT`

---

## 🕹️ Atajos Durante la Partida

* **`[F3]`**: Activar / desactivar monitor de FPS en tiempo real (verde = 60 FPS estables, amarillo/rojo = caídas).
* **`[F5]`**: Guardado Rápido instantáneo (*Quick Save*).
* **`[F7]`**: Carga Rápida instantánea (*Quick Load*).
* **`[F11]` o `[ALT + ENTER]`**: Alternar Pantalla Completa / Ventana en tiempo real.
* **`[ESC]`**: **Menú de Pausa retro integrado** (Continuar, Guardar, Cargar, Contador FPS, Pantalla Completa, Reiniciar consola o Volver al catálogo).

---

## 🛠️ Recompilación de los Núcleos C (Opcional)

* **En Linux:**
  ```bash
  make -C src/emulator_core
  ```
  *Compila `libretrosnes.so`, `libmegadrive_bridge.so` y `libneogeo_bridge.so`.*
* **En Windows:**
  Ejecuta con doble clic el script `windows\compile_cores.bat` (o compila mediante MinGW/GCC / Zig).  
  *Compila `libretrosnes.dll`, `libmegadrive_bridge.dll` y `libneogeo_bridge.dll`.*

---

## ⚖️ Aviso Legal, Cumplimiento en GitHub y Descargo de Responsabilidad (*Disclaimer*)

Este proyecto ha sido desarrollado con fines exclusivamente **educativos, de investigación técnica y de preservación histórica del software de videojuegos**.

1. **Cumplimiento Estricto con GitHub TOS y DMCA (Sin BIOS Propietaria ni ROMs Comerciales):**  
   Este repositorio **no aloja ni distribuye ninguna ROM comercial con derechos de autor ni archivos de firmware/BIOS propietarios** como `neogeo.zip` (`sp-s2.sp1`, etc.). El archivo `.gitignore` prohíbe explícitamente cualquier subida involuntaria de archivos BIOS comerciales o volcados de ROMs protegidas. Los usuarios deben suministrar sus propios volcados legítimos obtenidos de sus consolas físicas o compras digitales autorizadas. Se incluye exclusivamente una demo homebrew de dominio público / libre distribución con fines de prueba técnica.
2. **Marcas Registradas (*Trademarks*):**  
   *Super Nintendo*, *SNES*, *Famicom*, *Sega*, *Mega Drive*, *Genesis*, *SNK*, *Neo Geo*, *MVS*, *AES* y todos los nombres comerciales, logotipos o marcas asociadas pertenecen a sus respectivos titulares de derechos (**Nintendo Co., Ltd.**, **Sega Games Co., Ltd.** y **SNK CORPORATION**). Su mención en este proyecto se realiza bajo el amparo de la doctrina de **Uso Legítimo Nominativo (*Nominative Fair Use*)** exclusivamente con propósitos de descripción técnica y compatibilidad de software.
3. **Legalidad de la Emulación:**  
   De acuerdo con la jurisprudencia internacional consolidada sobre propiedad intelectual (incluyendo los precedentes *Sony v. Bleem* y *Sega v. Accolade*), el desarrollo de emuladores mediante técnicas limpias de especificación e interoperabilidad de software es completamente legal.
4. **Licencias de Código Abierto:**  
   Los motores de emulación utilizados están licenciados bajo software libre (GPLv2 / licencias libres de emulación). FBAlpha 2012 Neo Geo y Genesis Plus GX están sujetos a la GNU General Public License v2. Consulte las cabeceras y fuentes para los créditos correspondientes.
