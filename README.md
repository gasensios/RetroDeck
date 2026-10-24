# 🎮 RetroDeck - Estación de Emulación Multi-Sistema de 16 Bits (Linux, Windows y Web)

**RetroDeck** es una plataforma de juegos retro para **Super Nintendo (SNES)** y **Sega Mega Drive / Genesis** completamente **autónoma, multiplataforma y multi-sistema**, con motores de emulación propios en C de alto rendimiento y una interfaz gráfica artística inspirada en los salones recreativos (Arcade) y consolas de 16 bits de los años 80 y 90 (fondo Mode 7 neón en perspectiva, chasis metálico con tornillos remachados, badges oficiales y bahía de cartuchos 3D).

El proyecto está diseñado y diferenciado para disfrutarse en **tres plataformas principales**:
1. 🐧 **Versión Linux (Nativa):** Máximo rendimiento mediante núcleos en C (`.so`) y lanzador interactivo.
2. 🪟 **Versión Windows (Nativa):** Doble clic con instalador virtual integrado (`.bat` / `.vbs`) y opción de empaquetado a `.exe`.
3. 🌐 **Versión Web (GitHub Pages):** Ejecución instantánea en el navegador a 60 FPS mediante WebAssembly sin instalar nada.

> 🌐 **¿Quieres jugar ahora mismo desde tu navegador?**  
> ¡Prueba la versión WebAssembly online sin descargar nada!  
> 🕹️ **[Jugar a RetroDeck Web Online](https://gasensios.github.io/RetroDeck/)**

---

## 🌟 Sistemas Soportados

| Consola | Compañía | Extensiones Soportadas | Resolución Nativa |
| :--- | :--- | :--- | :--- |
| **Super Nintendo (SNES)** | Nintendo | `.smc`, `.sfc`, `.fig`, `.zip` | 512×480 (4:3) |
| **Mega Drive / Genesis** | Sega | `.bin`, `.gen`, `.md`, `.smd`, `.zip` | 320×224 (4:3) |

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
├── .gitignore                 # 🛡️ Protección de Git (ignora ROMs, saves y binarios)
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
│   └── megadrive/             # 📂 Juegos de Sega Mega Drive (.bin, .md, .gen)
│
├── boxart/
│   ├── snes/                  # 🖼️ Carátulas de SNES (.png, .jpg, .webp)
│   └── megadrive/             # 🖼️ Carátulas de Mega Drive (.png, .jpg, .webp)
│
├── saves/
│   ├── snes/                  # 💾 Partidas de batería SNES (.srm)
│   └── megadrive/             # 💾 Partidas de batería Mega Drive (.srm)
│
├── states/
│   ├── snes/                  # ⚡ Savestates rápidos SNES
│   └── megadrive/             # ⚡ Savestates rápidos Mega Drive
│
├── src/
│   ├── emulator_core/         # 🧠 Motores nativos C (SNES y Mega Drive)
│   ├── ui/                    # 🎨 Menús, selector de sistema y juego
│   └── core/                  # 🎛️ Gestores de entrada, plataformas y sonido
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
- **`[TAB]`** (o los gatillos **`[L]` / `[R]`** en mando): Alternar consola activa (Super Nintendo <-> Sega Mega Drive).
- **`[A]`, `[ENTER]` o `[ESPACIO]`**: Iniciar el juego seleccionado.
- **`[F11]` o `[ALT + ENTER]`**: Alternar entre Pantalla Completa y Modo Ventana.
- **`[X]` o `[M]`**: Abrir el **Menú Propio del Juego** (asignación de carátulas en múltiples formatos, copias de seguridad de partidas `.srm` y estadísticas).
- **`[C]`**: Abrir la configuración interactiva de mandos con diagrama retro.
- **`[S]`**: Menú de Ajustes generales (filtro CRT scanlines, volumen, etc.).
- **`[H]` o `[F1]`**: Guía rápida y ayuda en pantalla.

---

## 🕹️ Atajos Durante la Partida

* **`[F5]`**: Guardado Rápido instantáneo (*Quick Save*).
* **`[F7]`**: Carga Rápida instantánea (*Quick Load*).
* **`[F11]` o `[ALT + ENTER]`**: Alternar Pantalla Completa / Ventana en tiempo real.
* **`[ESC]`**: **Menú de Pausa retro integrado** (Continuar, Guardar, Cargar, Pantalla Completa, Reiniciar consola o Volver al catálogo).

---

## 🛠️ Recompilación de los Núcleos C (Opcional)

* **En Linux:**
  ```bash
  make -C src/emulator_core
  ```
  *Compila `libretrosnes.so` y `libmegadrive_bridge.so`.*
* **En Windows:**
  Ejecuta con doble clic el script `windows\compile_cores.bat` (requiere tener instalado MinGW/GCC o MSYS2).  
  *Compila `libretrosnes.dll` y `libmegadrive_bridge.dll`.*

---

## ⚖️ Aviso Legal y Descargo de Responsabilidad (*Disclaimer*)

Este proyecto ha sido desarrollado con fines exclusivamente **educativos, de investigación técnica y de preservación histórica del software de videojuegos**.

1. **Sin Contenido Protegido por Derechos de Autor:**  
   Este repositorio **no aloja ni distribuye ninguna ROM comercial, juego protegido por copyright, volcado de BIOS propietaria ni material audiovisual registrado**. Los usuarios deben suministrar sus propias copias de seguridad legítimas de los cartuchos físicos de su propiedad.
2. **Marcas Registradas (*Trademarks*):**  
   *Super Nintendo*, *SNES*, *Famicom*, *Sega*, *Mega Drive*, *Genesis* y todos los nombres comerciales, logotipos o marcas asociadas pertenecen a **Nintendo Co., Ltd.** y **Sega Games Co., Ltd.** respectivamente. Su mención en este proyecto se realiza bajo el amparo de la doctrina de **Uso Legítimo Nominativo (*Nominative Fair Use*)** exclusivamente con propósitos de descripción de compatibilidad de software.
3. **Legalidad de la Emulación:**  
   De acuerdo con la jurisprudencia consolidada sobre propiedad intelectual y compatibilidad de software, el desarrollo de emuladores mediante técnicas limpias de especificación e ingeniería inversa es completamente legal.
4. **Licencias de Código Abierto:**  
   El núcleo de Sega Mega Drive utiliza componentes basados en *Genesis Plus GX* (GNU General Public License v2) y el núcleo de Super Nintendo implementa arquitecturas abiertas de libre distribución. Consulte los archivos de cabecera para los créditos y licencias correspondientes.
