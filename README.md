# ADSE Desktop

Wrapper Electron para la plataforma ADSE (Director Secundaria), versión instalable.

## Arquitectura

```
┌────────────────────────────────────────────────────────────┐
│  Equipo del usuario                                         │
│                                                             │
│   ┌─────────────────────┐       ┌────────────────────────┐  │
│   │  Electron (main)    │──────▶│  Backend ADSE          │  │
│   │  - Splash + login   │       │  (servidor_adse.exe)   │  │
│   │  - BrowserWindow    │       │  - FastAPI en          │  │
│   │                     │       │    127.0.0.1:AUTO      │  │
│   └──────────┬──────────┘       │  - SQLite local        │  │
│              │                  │    %APPDATA%/ADSE/     │  │
│              │ https            └────────────────────────┘  │
└──────────────┼──────────────────────────────────────────────┘
               │
               ▼
  ┌──────────────────────────────────┐
  │  licencias.agenteseducacion…     │
  │  POST /api/licencia/validar      │
  │  POST /api/licencia/estado       │
  │  (solo para validar suscripción) │
  └──────────────────────────────────┘
```

## Desarrollo

```bash
# 1) Instalar Electron
npm install

# 2) Copiar código backend (ya hecho) a ./backend/
#    requirements.txt, servidor_adse.py, adse_core.py, adse_html.py, ...

# 3) Instalar deps Python
cd backend
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt

# 4) Arrancar en modo dev (Electron usa Python del sistema)
cd ..
npm start
```

## Build de producción (Windows)

```bash
# 1) Empaquetar backend con PyInstaller
pip install pyinstaller
python build_backend.py       # genera ./backend_dist/

# 2) Empaquetar Electron + backend
npm run build:win             # genera ./dist/ADSE-Setup-1.0.0.exe
```

El instalador resultante (`ADSE-Setup-x.y.z.exe`) contiene:
- Electron runtime (Chromium)
- Backend ADSE bundleado (PyInstaller)
- No requiere que el usuario tenga Python instalado

## Estructura

```
ADSE_desktop/
├── main.js           # Proceso principal Electron
├── preload.js        # Bridge IPC seguro (contextIsolation)
├── splash.html       # Pantalla de login + validación licencia
├── package.json
├── build_backend.py  # Script PyInstaller
├── build/
│   ├── icon.ico      # Icono Windows (pendiente)
│   ├── icon.icns     # Icono macOS (pendiente)
│   └── license.txt   # Términos mostrados en instalador
├── backend/          # Código Python (dev)
│   ├── servidor_adse.py
│   ├── adse_core.py
│   ├── adse_html.py
│   ├── requirements.txt
│   └── conocimiento_adse/
└── backend_dist/     # Backend bundleado (generado por build_backend.py)
```
