"""
ADSE Visual - Router principal de generación visual
Genera imágenes y videos usando GPU local (RTX 4090).

Motor:
  - local: Wan 2.6 (video) + Qwen Image (imágenes) → GRATIS, corre en GPU local
"""

import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("adse.visual")

# =============================================
# CONFIGURACIÓN VISUAL
# =============================================
BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_IMAGENES = OUTPUTS_DIR / "imagenes"
OUTPUTS_VIDEOS = OUTPUTS_DIR / "videos"

# Crear carpetas de salida si no existen
OUTPUTS_IMAGENES.mkdir(parents=True, exist_ok=True)
OUTPUTS_VIDEOS.mkdir(parents=True, exist_ok=True)

# Tier por defecto
VISUAL_TIER_DEFAULT = os.environ.get("ADSE_VISUAL_TIER", "local").lower()

# =============================================
# TIPOS DE GENERACIÓN SOPORTADOS
# =============================================
TIPOS_VALIDOS = {
    "imagen": {
        "text2img": "Genera imagen desde texto",
        "img2img": "Edita/transforma una imagen existente",
    },
    "video": {
        "text2vid": "Genera video desde texto",
        "img2vid": "Anima una imagen estática a video",
    }
}

# =============================================
# ESTADO DE MOTORES
# =============================================
_motor_local_disponible = None


def verificar_motor_local() -> bool:
    """Verifica si los modelos locales (Wan + Qwen) están disponibles."""
    global _motor_local_disponible
    if _motor_local_disponible is not None:
        return _motor_local_disponible
    try:
        from adse_visual_local import verificar_disponibilidad
        _motor_local_disponible = verificar_disponibilidad()
    except ImportError:
        logger.warning("Motor local (adse_visual_local) no disponible")
        _motor_local_disponible = False
    return _motor_local_disponible


def obtener_estado() -> dict:
    """Retorna el estado actual del motor visual local."""
    return {
        "local": {
            "disponible": verificar_motor_local(),
            "modelos": {
                "imagen": "Qwen Image (local)",
                "video": "Wan 2.6 (local)"
            },
            "costo": "Gratis (GPU local RTX 4090)"
        }
    }


# =============================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =============================================
def generar_visual(
    tipo: str,
    prompt: str,
    imagen_referencia: str = None,
    tier: str = None,
    usuario_id: int = None,
    opciones: dict = None
) -> dict:
    """
    Genera contenido visual (imagen o video).

    Args:
        tipo: "imagen" o "video"
        prompt: Descripción de lo que se quiere generar
        imagen_referencia: Ruta a imagen de referencia (para img2img / img2vid)
        tier: "local" (generación en GPU local)
        usuario_id: ID del usuario que solicita
        opciones: Opciones adicionales (resolución, duración, estilo, etc.)

    Returns:
        dict con:
            - exito: bool
            - archivo: str (ruta al archivo generado)
            - tipo: "imagen" o "video"
            - motor: str (nombre del motor usado)
            - duracion_ms: int (tiempo de generación)
            - error: str (si exito=False)
    """
    if opciones is None:
        opciones = {}

    tier = (tier or VISUAL_TIER_DEFAULT).lower()
    inicio = datetime.now()

    # Mapear subtipos a tipos principales (text2img → imagen, text2vid → video)
    MAPEO_TIPOS = {"text2img": "imagen", "img2img": "imagen", "text2vid": "video", "img2vid": "video"}
    if tipo in MAPEO_TIPOS:
        tipo = MAPEO_TIPOS[tipo]

    # Validar tipo
    if tipo not in TIPOS_VALIDOS:
        return {
            "exito": False,
            "error": f"Tipo '{tipo}' no válido. Usa: {list(TIPOS_VALIDOS.keys())}",
            "tipo": tipo,
            "motor": "ninguno",
            "duracion_ms": 0
        }

    # Determinar subtipo
    if imagen_referencia:
        subtipo = "img2img" if tipo == "imagen" else "img2vid"
    else:
        subtipo = "text2img" if tipo == "imagen" else "text2vid"

    logger.info(f"Generación visual: tipo={tipo}, subtipo={subtipo}, tier={tier}, usuario={usuario_id}")

    # Generar nombre de archivo de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if tipo == "imagen":
        extension = "png"
        carpeta_salida = OUTPUTS_IMAGENES
    else:
        extension = "mp4"
        carpeta_salida = OUTPUTS_VIDEOS

    archivo_salida = str(carpeta_salida / f"{tipo}_{timestamp}_{usuario_id or 'anon'}.{extension}")

    # Enrutar al motor correcto
    try:
        resultado = _ejecutar_generacion(
            tier=tier,
            tipo=tipo,
            subtipo=subtipo,
            prompt=prompt,
            imagen_referencia=imagen_referencia,
            archivo_salida=archivo_salida,
            opciones=opciones
        )
    except Exception as e:
        logger.error(f"Error en generación visual: {e}")
        resultado = {
            "exito": False,
            "error": str(e),
            "archivo": None,
            "motor": tier
        }

    # Calcular duración
    duracion = (datetime.now() - inicio).total_seconds() * 1000

    resultado["tipo"] = tipo
    resultado["subtipo"] = subtipo
    resultado["duracion_ms"] = int(duracion)
    resultado["tier"] = tier

    if resultado["exito"]:
        logger.info(f"Generación exitosa: {archivo_salida} ({duracion:.0f}ms)")
    else:
        logger.warning(f"Generación fallida: {resultado.get('error', 'desconocido')}")

    return resultado


def _ejecutar_generacion(
    tier: str,
    tipo: str,
    subtipo: str,
    prompt: str,
    imagen_referencia: str,
    archivo_salida: str,
    opciones: dict
) -> dict:
    """Ejecuta la generación en el motor correspondiente al tier."""

    # ---- TIER LOCAL (Gratis) ----
    if tier == "local":
        if not verificar_motor_local():
            return {
                "exito": False,
                "error": "Motor local no disponible. Verifica que los modelos Wan/Qwen estén descargados.",
                "archivo": None,
                "motor": "local"
            }
        from adse_visual_local import generar as generar_local
        return generar_local(
            tipo=tipo,
            subtipo=subtipo,
            prompt=prompt,
            imagen_referencia=imagen_referencia,
            archivo_salida=archivo_salida,
            opciones=opciones
        )

    else:
        return {
            "exito": False,
            "error": f"Tier '{tier}' no reconocido. Solo disponible: local",
            "archivo": None,
            "motor": "desconocido"
        }


# =============================================
# UTILIDADES
# =============================================
def listar_generaciones(tipo: str = None, limite: int = 20) -> list:
    """Lista los archivos generados más recientes."""
    archivos = []

    if tipo is None or tipo == "imagen":
        for f in sorted(OUTPUTS_IMAGENES.glob("*.*"), key=lambda x: x.stat().st_mtime, reverse=True)[:limite]:
            archivos.append({
                "archivo": str(f),
                "nombre": f.name,
                "tipo": "imagen",
                "tamaño_kb": f.stat().st_size // 1024,
                "fecha": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })

    if tipo is None or tipo == "video":
        for f in sorted(OUTPUTS_VIDEOS.glob("*.*"), key=lambda x: x.stat().st_mtime, reverse=True)[:limite]:
            archivos.append({
                "archivo": str(f),
                "nombre": f.name,
                "tipo": "video",
                "tamaño_kb": f.stat().st_size // 1024,
                "fecha": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })

    return sorted(archivos, key=lambda x: x["fecha"], reverse=True)[:limite]


def limpiar_outputs(tipo: str = "todas", dias_antiguos: int = 7) -> int:
    """Elimina archivos generados. tipo: 'todas', 'imagen' o 'video'."""
    eliminados = 0
    limite = datetime.now().timestamp() - (dias_antiguos * 86400)

    carpetas = []
    if tipo in ("todas", "imagen"):
        carpetas.append(OUTPUTS_IMAGENES)
    if tipo in ("todas", "video"):
        carpetas.append(OUTPUTS_VIDEOS)

    for carpeta in carpetas:
        for f in carpeta.glob("*.*"):
            if f.stat().st_mtime < limite:
                f.unlink()
                eliminados += 1

    logger.info(f"Limpieza ({tipo}): {eliminados} archivos eliminados (>{dias_antiguos} días)")
    return eliminados
