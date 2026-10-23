# 🎮 RetroDeck - Emulador Multi-Sistema Retro para Linux (SNES & Sega Mega Drive)

**RetroDeck** es una estación de juegos retro para **Super Nintendo (SNES)** y **Sega Mega Drive / Genesis** completamente **autónoma y multi-sistema**, con motores de emulación propios en C de alto rendimiento y una interfaz gráfica artística inspirada en los salones recreativos (Arcade) y consolas de 16 bits de los años 80 y 90 (fondo Mode 7 neón, chasis metálico con tornillos remachados, badges originales y bahía de cartuchos 3D).

> 🌐 **¿Quieres jugar directamente en tu navegador?**  
> ¡Prueba la versión WebAssembly online sin instalar nada en GitHub Pages!  
> 🕹️ **[Probar RetroDeck Web Online](https://gasensios.github.io/RetroDeck/)**

---

## 🌟 Sistemas Soportados

| Consola | Compañía | Extensiones Soportadas | Resolución Nativa |
| :--- | :--- | :--- | :--- |
| **Super Nintendo (SNES)** | Nintendo | `.smc`, `.sfc`, `.fig`, `.zip` | 512×480 (4:3) |
| **Mega Drive / Genesis** | Sega | `.bin`, `.gen`, `.md`, `.smd`, `.zip` | 320×224 (4:3) |

---

## 📁 Estructura Multi-Sistema de Carpetas

```text
Retro_Games/
├── RetroDeck.sh               # 🚀 Ejecutable principal
├── RetroDeck.desktop          # 🖥️ Lanzador para el escritorio Linux
├── TUTORIAL.md                # 📘 Manual completo de uso y arquitectura
│
├── roms/
│   ├── snes/                  # 📂 Juegos de Super Nintendo (.smc, .sfc)
│   └── megadrive/             # 📂 Juegos de Sega Mega Drive (.bin, .md, .gen)
│
├── boxart/
│   ├── snes/                  # 🖼️ Carátulas de SNES
│   └── megadrive/             # 🖼️ Carátulas de Mega Drive
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
│   └── core/                  # 🎛️ Gestores de entrada, sistemas y sonido
└── assets/                    # 📦 Fuentes, sonidos retro, iconos y capturas
    └── screenshots/           # 📸 Capturas de pantalla de la interfaz
```

---

## 🚀 Cómo Jugar y Cambiar de Sistema

Ejecuta el lanzador:
```bash
./RetroDeck.sh
```

### 🔄 Selector de Consola y Opciones en el Menú
- Pulsa **`[TAB]`** (o los botones **`[L]` / `[R]`** en mando) para alternar instantáneamente entre **Super Nintendo** y **Sega Mega Drive**.
- La interfaz cambiará automáticamente de colores, carátulas, cartuchos 3D y catálogo de juegos.
- Pulsa **`[A]`** o **`[ENTER]`** para iniciar la ROM seleccionada.
- Pulsa **`[X]`** (en mando) o **`[M]`** (en teclado) para abrir el **Menú de Opciones del Juego** (asignación de carátulas `.png`, `.jpg`, `.webp`, `.bmp`, copias de seguridad de partidas `.srm` y estadísticas).

---

## 🕹️ Controles Durante la Partida

* **`[F5]`**: Guardar Estado Rápido (*Quick Save*).
* **`[F7]`**: Cargar Estado Rápido (*Quick Load*).
* **`[F11]`**: Alternar Pantalla Completa.
* **`[ESC]`**: **Menú de Pausa retro integrado** (Continuar, Guardar, Cargar, Reiniciar consola o Volver al menú de juegos).

---

## 🌐 Versión WebAssembly para GitHub Pages

RetroDeck cuenta con una versión web interactiva en la carpeta `docs/`, optimizada con **WebAssembly (WASM)** y lista para ejecutarse en GitHub Pages:

* **Acceso instantáneo sin descargas:** Puedes jugar desde cualquier navegador en PC, Mac o móvil en:  
  👉 **`https://gasensios.github.io/RetroDeck/`**
* **Arrastrar y soltar ROMs (Drag & Drop):** Arrastra cualquier archivo `.smc`, `.sfc`, `.bin`, `.gen`, `.md` sobre la pantalla del emulador para cargarlo al vuelo.
* **Demos integradas:** Incluye demos de juegos homebrew libres (*Astrohawk* para SNES y *BombX* para Mega Drive) listas para jugar con un clic.
* **Soporte de Mandos USB / Bluetooth:** Detecta automáticamente mandos de Xbox, PlayStation o mandos retro mediante la *Web Gamepad API*.
* **Filtro CRT en tiempo real:** Activa o desactiva las líneas de escaneado y la curvatura de tubo clásico.

### ⚙️ Cómo activar GitHub Pages en tu cuenta:
1. Crea tu repositorio en GitHub con el nombre `RetroDeck` (o el que prefieras) bajo tu cuenta `gasensios`.
2. Sube el código:
   ```bash
   git remote add origin https://github.com/gasensios/RetroDeck.git
   git add .
   git commit -m "RetroDeck: Edición dual Desktop (Linux) y Web (WebAssembly)"
   git push -u origin main
   ```
3. En GitHub, entra en tu repositorio y dirígete a **Settings** > **Pages**.
4. En **Build and deployment** > **Source**, selecciona **Deploy from a branch** -> Rama `main` -> Carpeta `/docs` -> Pulsa **Save**.
5. En un par de minutos, tu emulador estará activo en la red.

---

## 🛠️ Recompilación de los Núcleos C (Opcional)

Si descargas el código fuente o realizas cambios en los motores nativos C (`snes/` o `megadrive_bridge.c`), puedes compilar ambos núcleos compartidos ejecutando:
```bash
make -C src/emulator_core
```

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
