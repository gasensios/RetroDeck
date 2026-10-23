/**
 * RetroDeck Web - WebAssembly Retro Player for GitHub Pages (v3.0)
 * Uses high-performance WebAssembly cores (Snes9x & Genesis Plus GX via EmulatorJS)
 * User: https://github.com/gasensios
 */

(function () {
  'use strict';

  // State
  let currentSystem = 'snes'; // 'snes' or 'megadrive'
  let isCrtEnabled = true;
  let isLoading = false;

  // DOM Elements
  const body = document.body;
  const starfield = document.getElementById('starfield');
  const emulatorContainer = document.getElementById('emulator-container');
  const overlay = document.getElementById('crt-overlay');
  const crtViewport = document.getElementById('crt-viewport');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const toast = document.getElementById('retro-toast');

  const btnSnes = document.getElementById('tab-snes');
  const btnMd = document.getElementById('tab-megadrive');
  const systemBadge = document.getElementById('system-badge');
  const cartLabel = document.getElementById('cart-label');

  const btnCrt = document.getElementById('btn-crt');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnEject = document.getElementById('btn-eject');

  const btnDemoSnes = document.getElementById('btn-demo-snes');
  const btnDemoMd = document.getElementById('btn-demo-md');

  // Initialize
  function init() {
    createStarfield();
    setupSystemTabs();
    setupDragAndDrop();
    setupControls();
    setupDemos();
  }

  // 1. Starfield Background
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

  // 3. Emulator Launch using WebAssembly EmulatorJS
  function launchRom(fileOrUrl, filename = 'Juego') {
    if (isLoading) return;
    isLoading = true;

    // Detect system core from filename extension
    const parts = filename.split('.');
    const ext = parts.length > 1 ? parts.pop().toLowerCase() : '';
    let core = 'snes';

    if (['bin', 'gen', 'md', 'smd'].includes(ext)) {
      core = 'segaMD';
      setSystem('megadrive');
    } else if (['smc', 'sfc', 'fig'].includes(ext)) {
      core = 'snes';
      setSystem('snes');
    } else {
      core = currentSystem === 'megadrive' ? 'segaMD' : 'snes';
    }

    showToast(`⚡ Preparando ${filename}...`);

    // Prepare ROM object URL
    let romUrl = '';
    if (typeof fileOrUrl === 'string') {
      romUrl = fileOrUrl;
    } else if (fileOrUrl instanceof Blob || fileOrUrl instanceof File) {
      romUrl = URL.createObjectURL(fileOrUrl);
    } else {
      showToast('❌ Formato de archivo no reconocido');
      isLoading = false;
      return;
    }

    // Reset container and show player screen
    overlay.classList.add('hidden');
    emulatorContainer.style.display = 'block';
    emulatorContainer.innerHTML = '<div id="game" style="width: 100%; height: 100%;"></div>';

    // Set EmulatorJS global parameters
    window.EJS_player = '#game';
    window.EJS_core = core;
    window.EJS_gameUrl = romUrl;
    window.EJS_gameName = filename;
    window.EJS_color = core === 'segaMD' ? '#00e5ff' : '#a855f7';
    window.EJS_startOnLoaded = true;
    window.EJS_pathtodata = 'https://cdn.emulatorjs.org/stable/data/';

    // Remove existing script if any
    const existingScript = document.getElementById('ejs-loader');
    if (existingScript) existingScript.remove();

    // Inject official loader
    const script = document.createElement('script');
    script.id = 'ejs-loader';
    script.src = 'https://cdn.emulatorjs.org/stable/data/loader.js';
    script.onload = () => {
      isLoading = false;
      showToast(`▶ Jugando: ${filename} (60 FPS)`, 4000);
    };
    script.onerror = () => {
      isLoading = false;
      showToast('❌ Error al conectar con el servidor WebAssembly', 5000);
      ejectRom(true);
    };

    document.body.appendChild(script);
  }

  // 4. Drag & Drop and File Input
  function setupDragAndDrop() {
    dropzone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        launchRom(file, file.name);
        fileInput.value = '';
      }
    });

    ['dragenter', 'dragover'].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
      crtViewport.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    // Single unified drop handler for the CRT screen
    crtViewport.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        launchRom(file, file.name);
      }
    });

    // Global dragover prevention
    window.addEventListener('dragover', (e) => e.preventDefault());
  }

  // 5. Demos Launcher
  function setupDemos() {
    if (btnDemoSnes) {
      btnDemoSnes.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        launchRom('assets/demos/Astrohawk.smc', 'Astrohawk (SNES).smc');
      });
    }

    if (btnDemoMd) {
      btnDemoMd.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        launchRom('assets/demos/BombX.bin', 'BombX (Mega Drive).bin');
      });
    }
  }

  // 6. Controls & HUD Buttons
  function setupControls() {
    // CRT Filter Toggle
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

    // Fullscreen Toggle
    btnFullscreen.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        crtViewport.requestFullscreen().catch((err) => {
          showToast('Pantalla completa no disponible: ' + err.message);
        });
      } else {
        document.exitFullscreen();
      }
    });

    // Eject / Back to Menu
    btnEject.addEventListener('click', () => ejectRom(false));
  }

  function ejectRom(silent = false) {
    isLoading = false;
    emulatorContainer.innerHTML = '';
    emulatorContainer.style.display = 'none';
    overlay.classList.remove('hidden');

    const script = document.getElementById('ejs-loader');
    if (script) script.remove();

    if (!silent) {
      showToast('Cartucho expulsado. Volviendo al menú principal.');
    }
  }

  // Start on DOM ready
  document.addEventListener('DOMContentLoaded', init);
})();
