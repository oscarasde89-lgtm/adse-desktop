/**
 * ADSE Desktop — Proceso principal Electron
 *
 * Flujo:
 *   1. Al arrancar, muestra splash.html
 *   2. Lanza el backend Python (bundled) en un puerto local libre
 *   3. Espera a que el backend responda en /health
 *   4. Valida la licencia contra licencias_app (servidor central)
 *   5. Si la licencia es válida → abre la ventana principal apuntando a localhost:PORT
 *   6. Al cerrar la app, mata el backend
 */
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const net = require('net');
const { spawn } = require('child_process');
const https = require('https');

const Store = require('electron-store').default || require('electron-store');
const store = new Store({
  name: 'adse-config',
  encryptionKey: 'adse-v1-do-not-change',   // NO es seguridad real, solo ofuscación
});

const LICENCIAS_URL = 'https://agenteseducacion.com.mx/api/licencia';
const IS_DEV = !app.isPackaged;

let backendProc = null;
let backendPort = 0;
let mainWindow = null;
let splashWindow = null;

// ========= Utilidades =========
function findFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on('error', reject);
    srv.listen(0, '127.0.0.1', () => {
      const port = srv.address().port;
      srv.close(() => resolve(port));
    });
  });
}

function waitFor(url, timeoutMs = 20000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const tick = () => {
      const http = require('http');
      http.get(url, (res) => { res.destroy(); resolve(true); })
          .on('error', () => {
            if (Date.now() - start > timeoutMs) reject(new Error('timeout'));
            else setTimeout(tick, 300);
          });
    };
    tick();
  });
}

function backendDir() {
  if (IS_DEV) return path.join(__dirname, 'backend');
  return path.join(process.resourcesPath, 'backend');
}

function backendExe() {
  // En producción, el binario bundleado por PyInstaller
  if (process.platform === 'win32') {
    return path.join(backendDir(), 'servidor_adse.exe');
  }
  return path.join(backendDir(), 'servidor_adse');
}

// ========= Launch backend =========
async function launchBackend() {
  backendPort = await findFreePort();
  const exe = backendExe();
  const cwd = backendDir();

  let cmd, args;
  if (IS_DEV && !fs.existsSync(exe)) {
    // En dev, correr con Python del sistema
    cmd = process.platform === 'win32' ? 'python' : 'python3';
    args = ['servidor_adse.py'];
  } else {
    cmd = exe;
    args = [];
  }

  backendProc = spawn(cmd, args, {
    cwd,
    env: {
      ...process.env,
      ADSE_PORT: String(backendPort),
      ADSE_HOST: '127.0.0.1',
      ADSE_MODE: 'desktop',
      ADSE_DATA_DIR: path.join(app.getPath('userData'), 'data'),
    },
    stdio: IS_DEV ? 'inherit' : 'ignore',
    windowsHide: true,
  });

  backendProc.on('error', (err) => {
    dialog.showErrorBox('Error al iniciar ADSE', String(err));
    app.quit();
  });
  backendProc.on('exit', (code) => {
    if (code !== 0 && mainWindow) {
      dialog.showErrorBox('ADSE se cerró inesperadamente', `Código: ${code}`);
    }
  });

  await waitFor(`http://127.0.0.1:${backendPort}/health`, 30000);
}

function killBackend() {
  if (backendProc && !backendProc.killed) {
    try { backendProc.kill(); } catch (_) {}
    backendProc = null;
  }
}

// ========= Licencia =========
function validarLicencia({ email, password }) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ email, password });
    const req = https.request(`${LICENCIAS_URL}/validar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
      timeout: 15000,
    }, (res) => {
      let data = '';
      res.on('data', (c) => data += c);
      res.on('end', () => {
        try {
          const j = JSON.parse(data);
          if (res.statusCode === 200 && j.activa) resolve(j);
          else reject(new Error(j.detail || j.mensaje || 'Licencia no activa'));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('sin conexión al servidor de licencias')); });
    req.write(body);
    req.end();
  });
}

async function checkLicenciaCacheada() {
  const key = store.get('license_key');
  const email = store.get('email');
  if (!key || !email) return null;

  return new Promise((resolve) => {
    const body = JSON.stringify({ license_key: key });
    const req = https.request(`${LICENCIAS_URL}/estado`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
      timeout: 8000,
    }, (res) => {
      let data = '';
      res.on('data', (c) => data += c);
      res.on('end', () => {
        try {
          const j = JSON.parse(data);
          resolve(j.activa ? { email, license_key: key, plan: j.plan, expira: j.expira } : null);
        } catch (_) { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.write(body);
    req.end();
  });
}

// ========= Ventanas =========
function createSplash() {
  splashWindow = new BrowserWindow({
    width: 480, height: 340,
    frame: false, resizable: false, alwaysOnTop: true,
    center: true, transparent: false, show: false,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true },
  });
  splashWindow.loadFile('splash.html');
  splashWindow.once('ready-to-show', () => splashWindow.show());
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400, height: 900,
    minWidth: 1000, minHeight: 700,
    backgroundColor: '#0a0a0f',
    show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false },
    title: 'ADSE · Director Secundaria',
  });
  mainWindow.loadURL(`http://127.0.0.1:${backendPort}/`);
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (splashWindow) { splashWindow.destroy(); splashWindow = null; }
  });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
  mainWindow.on('closed', () => { mainWindow = null; });
}

// ========= IPC (splash → validar licencia) =========
ipcMain.handle('licencia:login', async (_e, { email, password }) => {
  try {
    const r = await validarLicencia({ email, password });
    store.set('license_key', r.license_key);
    store.set('email', email);
    return { ok: true, ...r };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('licencia:abrir', async () => {
  if (!mainWindow) createMainWindow();
});

ipcMain.handle('licencia:salir', () => { app.quit(); });

// ========= Lifecycle =========
app.whenReady().then(async () => {
  createSplash();
  try {
    await launchBackend();
  } catch (e) {
    dialog.showErrorBox('No se pudo iniciar ADSE', 'El backend no respondió. Reinicia la app.\n\n' + e.message);
    app.quit();
    return;
  }

  // Si hay licencia cacheada válida → saltar splash
  const cached = await checkLicenciaCacheada();
  if (cached) {
    createMainWindow();
    if (splashWindow) { splashWindow.destroy(); splashWindow = null; }
  }
  // Si no, el splash muestra formulario de login (ver splash.html)
});

app.on('window-all-closed', () => {
  killBackend();
  app.quit();
});

app.on('before-quit', killBackend);
