"""
Empaqueta el backend ADSE en un solo ejecutable para incluirlo con Electron.

Requisitos (instalar primero):
    pip install pyinstaller fastapi uvicorn anthropic python-dotenv pydantic \
                scikit-learn bcrypt python-docx requests websockets

Uso:
    python build_backend.py

Genera: ./backend_dist/servidor_adse[.exe] (+ dependencias)
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
OUT = ROOT / "backend_dist"
BUILD = ROOT / "build_pyi"

def main():
    if not BACKEND.exists():
        sys.exit(f"No existe {BACKEND}. Copia primero los .py de ADSE aquí.")

    if OUT.exists():
        shutil.rmtree(OUT)
    if BUILD.exists():
        shutil.rmtree(BUILD)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--name", "servidor_adse",
        "--distpath", str(OUT.parent / "_pyi_dist"),
        "--workpath", str(BUILD),
        "--specpath", str(BUILD),
        "--console",             # dejamos consola visible solo en dev; en prod usar --windowed
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "anthropic",
        "--collect-submodules", "anthropic",
        "--add-data", f"{BACKEND / 'conocimiento_adse'}{os.pathsep}conocimiento_adse",
        "--add-data", f"{BACKEND / 'adse_html.py'}{os.pathsep}.",
        str(BACKEND / "servidor_adse.py"),
    ]
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)

    produced = ROOT / "_pyi_dist" / "servidor_adse"
    if not produced.exists():
        sys.exit(f"PyInstaller no produjo {produced}")

    OUT.mkdir(parents=True, exist_ok=True)
    for item in produced.iterdir():
        dest = OUT / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    shutil.rmtree(ROOT / "_pyi_dist", ignore_errors=True)
    shutil.rmtree(BUILD, ignore_errors=True)
    print(f"\nListo. Backend empaquetado en: {OUT}")

if __name__ == "__main__":
    main()
