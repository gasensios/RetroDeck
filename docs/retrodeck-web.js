/**
 * RetroDeck Web - WebAssembly Retro Player for GitHub Pages
 * User: https://github.com/gasensios
 */

(function () {
  'use strict';

  // State
  let currentSystem = 'snes'; // 'snes' or 'megadrive'
  let nostalgistInstance = null;
  let isCrtEnabled = true;
  let isPaused = false;
  let isMuted = false;
  let currentRomName = '';

  // DOM Elements
  const body = document.body;
  const starfield = document.getElementById('starfield');
  const canvas = document.getElementById('emulator-canvas');
  const overlay = document.getElementById('crt-overlay');
  const crtViewport = document.getElementById('crt-viewport');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const toast = document.getElementById('retro-toast');

  const btnSnes = document.getElementById('tab-snes');
  const btnMd = document.getElementById('tab-megadrive');
  const systemBadge = document.getElementById('system-badge');
  const cartLabel = document.getElementById('cart-label');
  const cartBox = document.getElementById('cart-box');

  const btnPause = document.getElementById('btn-pause');
  const btnSave = document.getElementById('btn-save');
  const btnLoad = document.getElementById('btn-load');
  const btnCrt = document.getElementById('btn-crt');
  const btnMute = document.getElementById('btn-mute');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnEject = document.getElementById('btn-eject');

  const btnDemoSnes = document.getElementById('btn-demo-snes');
  const btnDemoMd = document.getElementById('btn-demo-md');

  // Initialize
  function init() {
    createStarfield();
    setupSystemTabs();
    setupDragAndDrop();
    setupGamepadListener();
    setupControls();
    setupDemos();
  }

  // 1. Starfield
  function createStarfield() {
    if (!starfield) return;
    const numStars = 65;
    for (let i = 0; i < numStars; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      const size = Math.random() * 2 + 1;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      star.style.left = `${Math.random() * 100}%`;
      star.style.top = `${Math.random() * 100}%`;
      star.style.animationDelay = `${Math.random() * 3}s`;
      star.style.animationDuration = `${Math.random() * 2 + 1.5}s`;
      starfield.appendChild(star);
    }
  }

  // Toast Notification
  function showToast(message, duration = 3000) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.classList.remove('show');
    }, duration);
  }

  // 2. System Tabs
  function setSystem(sys) {
    currentSystem = sys;
    if (sys === 'snes') {
      body.classList.remove('theme-megadrive');
      btnSnes.classList.add('active');
      btnMd.classList.remove('active');
      systemBadge.textContent = 'SUPER NINTENDO 16-BIT';
      cartLabel.innerHTML = '<span class="cart-label-text">SUPER NINTENDO<br>INSERT COIN</span>';
      showToast('Consola: Super Nintendo activa');
    } else {
      body.classList.add('theme-megadrive');
      btnMd.classList.add('active');
      btnSnes.classList.remove('active');
      systemBadge.textContent = 'SEGA MEGA DRIVE 16-BIT';
      cartLabel.innerHTML = '<span class="cart-label-text" style="color:#00e5ff;">SEGA MEGA DRIVE<br>HIGH DEFINITION</span>';
      showToast('Consola: Sega Mega Drive activa');
    }
  }

  function setupSystemTabs() {
    btnSnes.addEventListener('click', () => setSystem('snes'));
    btnMd.addEventListener('click', () => setSystem('megadrive'));
  }

  // 3. Gamepad Detection
  function setupGamepadListener() {
    window.addEventListener('gamepadconnected', (e) => {
      const pad = e.gamepad;
      showToast(`🎮 Mando detectado: ${pad.id.slice(0, 24)}...`);
    });
    window.addEventListener('gamepaddisconnected', () => {
      showToast('⚠️ Mando desconectado');
    });
  }

  // 4. Emulator Launch using WebAssembly Nostalgist
  async function launchRom(fileOrBlob, filename = 'Juego') {
    currentRomName = filename;
    const ext = filename.split('.').pop().toLowerCase();
    
    // Choose core
    let coreName = 'snes9x';
    if (['bin', 'gen', 'md', 'smd'].includes(ext)) {
      coreName = 'genesis_plus_gx';
      setSystem('megadrive');
    } else if (['smc', 'sfc', 'fig'].includes(ext)) {
      coreName = 'snes9x';
      setSystem('snes');
    } else {
      coreName = currentSystem === 'megadrive' ? 'genesis_plus_gx' : 'snes9x';
    }

    showToast(`⚡ Iniciando ${filename} en WebAssembly...`);

    // Stop previous instance if running
    if (nostalgistInstance) {
      try {
        await nostalgistInstance.exit();
      } catch (e) {
        console.warn('Error al salir de instancia previa:', e);
      }
      nostalgistInstance = null;
    }

    // Switch view
    overlay.classList.add('hidden');
    canvas.style.display = 'block';

    try {
      if (typeof Nostalgist === 'undefined') {
        throw new Error('Nostalgist WebAssembly loader no está listo todavía.');
      }

      nostalgistInstance = await Nostalgist.launch({
        core: coreName,
        rom: fileOrBlob,
        element: canvas,
        resolveCoreJs(core) {
          return `https://cdn.jsdelivr.net/npm/nostalgist/dist/cores/${core}_libretro.js`;
        },
        resolveCoreWasm(core) {
          return `https://cdn.jsdelivr.net/npm/nostalgist/dist/cores/${core}_libretro.wasm`;
        }
      });

      isPaused = false;
      btnPause.textContent = '⏸ PAUSAR';
      showToast(`▶ Jugando: ${filename} (60 FPS)`);
    } catch (err) {
      console.error('Error al cargar emulador WebAssembly:', err);
      showToast(`❌ Error al cargar ROM: ${err.message}`, 4000);
      ejectRom();
    }
  }

  // 5. Drag & Drop and File Input
  function setupDragAndDrop() {
    dropzone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) launchRom(file, file.name);
    });

    ['dragenter', 'dragover'].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
      crtViewport.addEventListener(eventName, (e) => {
        e.preventDefault();
      });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    crtViewport.addEventListener('drop', (e) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) launchRom(file, file.name);
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) launchRom(file, file.name);
    });
  }

  // 6. Demos Launcher
  function setupDemos() {
    if (btnDemoSnes) {
      btnDemoSnes.addEventListener('click', async () => {
        try {
          showToast('Descargando demo SNES: Astrohawk...');
          const resp = await fetch('assets/demos/Astrohawk.smc');
          const blob = await resp.blob();
          launchRom(blob, 'Astrohawk (SNES)');
        } catch (e) {
          showToast('No se pudo cargar la demo local: ' + e.message);
        }
      });
    }

    if (btnDemoMd) {
      btnDemoMd.addEventListener('click', async () => {
        try {
          showToast('Descargando demo Mega Drive: BombX...');
          const resp = await fetch('assets/demos/BombX.bin');
          const blob = await resp.blob();
          launchRom(blob, 'BombX (Mega Drive)');
        } catch (e) {
          showToast('No se pudo cargar la demo local: ' + e.message);
        }
      });
    }
  }

  // 7. Controls & HUD Buttons
  function setupControls() {
    // Pause / Resume
    btnPause.addEventListener('click', async () => {
      if (!nostalgistInstance) return;
      if (isPaused) {
        await nostalgistInstance.resume();
        btnPause.textContent = '⏸ PAUSAR';
        isPaused = false;
        showToast('Juego reanudado');
      } else {
        await nostalgistInstance.pause();
        btnPause.textContent = '▶ CONTINUAR';
        isPaused = true;
        showToast('Juego en pausa');
      }
    });

    // Save State
    btnSave.addEventListener('click', async () => {
      if (!nostalgistInstance) return;
      try {
        const state = await nostalgistInstance.saveState();
        localStorage.setItem(`retrodeck_state_${currentRomName}`, JSON.stringify(Array.from(new Uint8Array(state.state))));
        showToast('💾 Savestate guardado en el navegador');
      } catch (e) {
        showToast('Error al guardar estado: ' + e.message);
      }
    });

    // Load State
    btnLoad.addEventListener('click', async () => {
      if (!nostalgistInstance) return;
      try {
        const saved = localStorage.getItem(`retrodeck_state_${currentRomName}`);
        if (!saved) {
          showToast('No hay partida guardada para este juego');
          return;
        }
        const stateArray = new Uint8Array(JSON.parse(saved));
        await nostalgistInstance.loadState(stateArray.buffer);
        showToast('⚡ Savestate restaurado');
      } catch (e) {
        showToast('Error al cargar estado: ' + e.message);
      }
    });

    // CRT Toggle
    btnCrt.addEventListener('click', () => {
      isCrtEnabled = !isCrtEnabled;
      if (isCrtEnabled) {
        crtViewport.classList.remove('crt-off');
        btnCrt.classList.add('active');
        showToast('Filtro CRT Scanlines: ACTIVADO');
      } else {
        crtViewport.classList.add('crt-off');
        btnCrt.classList.remove('active');
        showToast('Filtro CRT Scanlines: DESACTIVADO');
      }
    });

    // Mute / Sound
    btnMute.addEventListener('click', () => {
      isMuted = !isMuted;
      if (isMuted) {
        btnMute.textContent = '🔇 MUTE';
        btnMute.classList.add('active');
      } else {
        btnMute.textContent = '🔊 AUDIO';
        btnMute.classList.remove('active');
      }
      showToast(isMuted ? 'Audio silenciado' : 'Audio activado');
    });

    // Fullscreen
    btnFullscreen.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        crtViewport.requestFullscreen().catch((err) => {
          showToast('Error al activar pantalla completa: ' + err.message);
        });
      } else {
        document.exitFullscreen();
      }
    });

    // Eject / Back to Menu
    btnEject.addEventListener('click', () => ejectRom());
  }

  function ejectRom() {
    if (nostalgistInstance) {
      try {
        nostalgistInstance.exit();
      } catch (e) {}
      nostalgistInstance = null;
    }
    canvas.style.display = 'none';
    overlay.classList.remove('hidden');
    showToast('Cartucho expulsado. Volviendo al menú principal.');
  }

  // Keyboard Shortcuts (F5 = Save, F7 = Load, F11 = Fullscreen, ESC = Pause)
  window.addEventListener('keydown', (e) => {
    if (e.key === 'F5') {
      e.preventDefault();
      btnSave.click();
    } else if (e.key === 'F7') {
      e.preventDefault();
      btnLoad.click();
    } else if (e.key === 'Escape' && nostalgistInstance) {
      e.preventDefault();
      btnPause.click();
    }
  });

  // Start on DOM ready
  document.addEventListener('DOMContentLoaded', init);
})();
