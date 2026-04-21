"""
ADSE Visual Local - Motor de generación visual con modelos locales
Usa Wan 2.6 para video y Qwen Image para imágenes.
Requiere GPU NVIDIA con CUDA (recomendado: RTX 5080 Ti 16GB+).

Modelos:
  - Wan 2.6 (1.3B): Video ligero, ~4GB VRAM
  - Wan 2.6 (14B): Video completo, ~16GB VRAM (cuantizado INT4)
  - Qwen Image 2.0 (7B): Imágenes, ~8-10GB VRAM
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger("adse.visual.local")

# =============================================
# CONFIGURACIÓN
# =============================================
BASE_DIR = Path(__file__).resolve().parent
MODELOS_DIR = BASE_DIR / "modelos"
WAN_MODEL_DIR = MODELOS_DIR / "wan"
QWEN_IMAGE_MODEL_DIR = MODELOS_DIR / "qwen-image"

# Tamaño del modelo Wan: "1.3b" o "14b"
WAN_MODEL_SIZE = os.environ.get("WAN_MODEL_SIZE", "1.3b").lower()

# IDs de HuggingFace para descarga
MODELOS_HF = {
    "wan_1.3b": "Wan-AI/Wan2.6-T2V-1.3B",
    "wan_14b": "Wan-AI/Wan2.6-T2V-14B",
    "wan_i2v_1.3b": "Wan-AI/Wan2.6-I2V-1.3B",
    "wan_i2v_14b": "Wan-AI/Wan2.6-I2V-14B",
    "qwen_image": "Qwen/Qwen-Image",
}

# Estado de los modelos cargados
_wan_pipeline = None
_wan_i2v_pipeline = None
_qwen_pipeline = None
_gpu_disponible = None


# =============================================
# VERIFICACIÓN DE HARDWARE
# =============================================
def verificar_gpu() -> dict:
    """Verifica la GPU disponible y su VRAM."""
    global _gpu_disponible
    try:
        import torch
        if torch.cuda.is_available():
            nombre = torch.cuda.get_device_name(0)
            vram_total = torch.cuda.get_device_properties(0).total_mem / (1024**3)
            vram_libre = (torch.cuda.get_device_properties(0).total_mem -
                         torch.cuda.memory_allocated(0)) / (1024**3)
            _gpu_disponible = True
            return {
                "disponible": True,
                "nombre": nombre,
                "vram_total_gb": round(vram_total, 1),
                "vram_libre_gb": round(vram_libre, 1),
                "cuda_version": torch.version.cuda
            }
        else:
            _gpu_disponible = False
            return {"disponible": False, "error": "CUDA no disponible"}
    except ImportError:
        _gpu_disponible = False
        return {"disponible": False, "error": "PyTorch no instalado"}


def verificar_disponibilidad() -> bool:
    """Verifica si el motor local puede funcionar."""
    gpu_info = verificar_gpu()
    if not gpu_info["disponible"]:
        logger.warning(f"GPU no disponible: {gpu_info.get('error', 'desconocido')}")
        return False

    # Verificar que al menos un modelo existe
    wan_existe = WAN_MODEL_DIR.exists() and any(WAN_MODEL_DIR.iterdir())
    qwen_existe = QWEN_IMAGE_MODEL_DIR.exists() and any(QWEN_IMAGE_MODEL_DIR.iterdir())

    if not wan_existe and not qwen_existe:
        logger.warning("Ningún modelo local descargado. Ejecuta descargar_modelos()")
        return False

    logger.info(f"Motor local disponible - GPU: {gpu_info['nombre']}, "
                f"VRAM: {gpu_info['vram_total_gb']}GB, "
                f"Wan: {'sí' if wan_existe else 'no'}, "
                f"Qwen: {'sí' if qwen_existe else 'no'}")
    return True


# =============================================
# DESCARGA DE MODELOS
# =============================================
def descargar_modelos(solo_video: bool = False, solo_imagen: bool = False) -> dict:
    """
    Descarga los modelos desde HuggingFace.
    Requiere: pip install huggingface_hub

    Args:
        solo_video: Solo descarga Wan (video)
        solo_imagen: Solo descarga Qwen Image (imágenes)
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        return {"exito": False, "error": "Instala huggingface_hub: pip install huggingface_hub"}

    resultados = {}

    # Descargar Wan (video)
    if not solo_imagen:
        wan_id = f"wan_{WAN_MODEL_SIZE}"
        wan_hf = MODELOS_HF.get(wan_id)
        wan_i2v_id = f"wan_i2v_{WAN_MODEL_SIZE}"
        wan_i2v_hf = MODELOS_HF.get(wan_i2v_id)

        if wan_hf:
            logger.info(f"Descargando Wan {WAN_MODEL_SIZE} Text-to-Video...")
            try:
                snapshot_download(
                    repo_id=wan_hf,
                    local_dir=str(WAN_MODEL_DIR / f"t2v-{WAN_MODEL_SIZE}"),
                    resume_download=True
                )
                resultados["wan_t2v"] = {"exito": True, "modelo": wan_hf}
            except Exception as e:
                resultados["wan_t2v"] = {"exito": False, "error": str(e)}

        if wan_i2v_hf:
            logger.info(f"Descargando Wan {WAN_MODEL_SIZE} Image-to-Video...")
            try:
                snapshot_download(
                    repo_id=wan_i2v_hf,
                    local_dir=str(WAN_MODEL_DIR / f"i2v-{WAN_MODEL_SIZE}"),
                    resume_download=True
                )
                resultados["wan_i2v"] = {"exito": True, "modelo": wan_i2v_hf}
            except Exception as e:
                resultados["wan_i2v"] = {"exito": False, "error": str(e)}

    # Descargar Qwen Image
    if not solo_video:
        qwen_hf = MODELOS_HF["qwen_image"]
        logger.info("Descargando Qwen Image...")
        try:
            snapshot_download(
                repo_id=qwen_hf,
                local_dir=str(QWEN_IMAGE_MODEL_DIR),
                resume_download=True
            )
            resultados["qwen_image"] = {"exito": True, "modelo": qwen_hf}
        except Exception as e:
            resultados["qwen_image"] = {"exito": False, "error": str(e)}

    return resultados


# =============================================
# CARGA DE MODELOS EN MEMORIA
# =============================================
def _cargar_wan_t2v():
    """Carga el pipeline de Wan Text-to-Video."""
    global _wan_pipeline
    if _wan_pipeline is not None:
        return _wan_pipeline

    import torch
    from diffusers import WanPipeline

    modelo_dir = WAN_MODEL_DIR / f"t2v-{WAN_MODEL_SIZE}"
    if not modelo_dir.exists():
        raise FileNotFoundError(f"Modelo Wan T2V no encontrado en {modelo_dir}")

    logger.info(f"Cargando Wan T2V {WAN_MODEL_SIZE}...")
    _wan_pipeline = WanPipeline.from_pretrained(
        str(modelo_dir),
        torch_dtype=torch.float16
    )
    _wan_pipeline.to("cuda")
    _wan_pipeline.enable_model_cpu_offload()
    logger.info("Wan T2V cargado exitosamente")
    return _wan_pipeline


def _cargar_wan_i2v():
    """Carga el pipeline de Wan Image-to-Video."""
    global _wan_i2v_pipeline
    if _wan_i2v_pipeline is not None:
        return _wan_i2v_pipeline

    import torch
    from diffusers import WanI2VPipeline

    modelo_dir = WAN_MODEL_DIR / f"i2v-{WAN_MODEL_SIZE}"
    if not modelo_dir.exists():
        raise FileNotFoundError(f"Modelo Wan I2V no encontrado en {modelo_dir}")

    logger.info(f"Cargando Wan I2V {WAN_MODEL_SIZE}...")
    _wan_i2v_pipeline = WanI2VPipeline.from_pretrained(
        str(modelo_dir),
        torch_dtype=torch.float16
    )
    _wan_i2v_pipeline.to("cuda")
    _wan_i2v_pipeline.enable_model_cpu_offload()
    logger.info("Wan I2V cargado exitosamente")
    return _wan_i2v_pipeline


def _cargar_qwen_image():
    """Carga el pipeline de Qwen Image."""
    global _qwen_pipeline
    if _qwen_pipeline is not None:
        return _qwen_pipeline

    import torch
    from diffusers import FluxPipeline  # Qwen Image usa arquitectura Flux-like

    if not QWEN_IMAGE_MODEL_DIR.exists():
        raise FileNotFoundError(f"Modelo Qwen Image no encontrado en {QWEN_IMAGE_MODEL_DIR}")

    logger.info("Cargando Qwen Image...")
    _qwen_pipeline = FluxPipeline.from_pretrained(
        str(QWEN_IMAGE_MODEL_DIR),
        torch_dtype=torch.float16
    )
    _qwen_pipeline.to("cuda")
    _qwen_pipeline.enable_model_cpu_offload()
    logger.info("Qwen Image cargado exitosamente")
    return _qwen_pipeline


# =============================================
# GENERACIÓN
# =============================================
def generar(
    tipo: str,
    subtipo: str,
    prompt: str,
    imagen_referencia: str = None,
    archivo_salida: str = None,
    opciones: dict = None
) -> dict:
    """
    Genera imagen o video con modelos locales.

    Args:
        tipo: "imagen" o "video"
        subtipo: "text2img", "img2img", "text2vid", "img2vid"
        prompt: Texto descriptivo
        imagen_referencia: Ruta a imagen (para img2img / img2vid)
        archivo_salida: Ruta donde guardar el resultado
        opciones: Dict con opciones adicionales:
            - width: int (default 1024)
            - height: int (default 1024)
            - steps: int (pasos de inferencia, default 30)
            - duration_seconds: float (duración video, default 4)
            - fps: int (frames por segundo, default 24)
            - negative_prompt: str
            - seed: int (para reproducibilidad)
    """
    if opciones is None:
        opciones = {}

    try:
        if tipo == "imagen":
            return _generar_imagen(subtipo, prompt, imagen_referencia, archivo_salida, opciones)
        elif tipo == "video":
            return _generar_video(subtipo, prompt, imagen_referencia, archivo_salida, opciones)
        else:
            return {"exito": False, "error": f"Tipo no soportado: {tipo}", "archivo": None, "motor": "local"}
    except Exception as e:
        logger.error(f"Error en generación local: {e}")
        return {"exito": False, "error": str(e), "archivo": None, "motor": "local"}


def _generar_imagen(subtipo, prompt, imagen_referencia, archivo_salida, opciones):
    """Genera imagen con Qwen Image."""
    import torch
    from PIL import Image

    pipeline = _cargar_qwen_image()

    width = opciones.get("width", 1024)
    height = opciones.get("height", 1024)
    steps = opciones.get("steps", 30)
    negative_prompt = opciones.get("negative_prompt", "blurry, low quality, distorted")
    seed = opciones.get("seed", None)

    generator = None
    if seed is not None:
        generator = torch.Generator(device="cuda").manual_seed(seed)

    if subtipo == "text2img":
        resultado = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            generator=generator
        )
    elif subtipo == "img2img":
        if not imagen_referencia or not os.path.exists(imagen_referencia):
            return {"exito": False, "error": "Imagen de referencia no proporcionada", "archivo": None, "motor": "Qwen Image (local)"}

        img_ref = Image.open(imagen_referencia).convert("RGB")
        resultado = pipeline(
            prompt=prompt,
            image=img_ref,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            generator=generator
        )
    else:
        return {"exito": False, "error": f"Subtipo no soportado: {subtipo}", "archivo": None, "motor": "Qwen Image (local)"}

    # Guardar resultado
    imagen = resultado.images[0]
    imagen.save(archivo_salida, quality=95)

    return {
        "exito": True,
        "archivo": archivo_salida,
        "motor": "Qwen Image (local)",
        "resolucion": f"{width}x{height}",
        "pasos": steps
    }


def _generar_video(subtipo, prompt, imagen_referencia, archivo_salida, opciones):
    """Genera video con Wan 2.6."""
    import torch
    from PIL import Image

    duration = opciones.get("duration_seconds", 4)
    fps = opciones.get("fps", 24)
    width = opciones.get("width", 832)
    height = opciones.get("height", 480)
    steps = opciones.get("steps", 30)
    seed = opciones.get("seed", None)

    num_frames = int(duration * fps)

    generator = None
    if seed is not None:
        generator = torch.Generator(device="cuda").manual_seed(seed)

    if subtipo == "text2vid":
        pipeline = _cargar_wan_t2v()
        resultado = pipeline(
            prompt=prompt,
            num_frames=num_frames,
            width=width,
            height=height,
            num_inference_steps=steps,
            generator=generator
        )
    elif subtipo == "img2vid":
        if not imagen_referencia or not os.path.exists(imagen_referencia):
            return {"exito": False, "error": "Imagen de referencia no proporcionada", "archivo": None, "motor": "Wan 2.6 (local)"}

        pipeline = _cargar_wan_i2v()
        img_ref = Image.open(imagen_referencia).convert("RGB").resize((width, height))
        resultado = pipeline(
            prompt=prompt,
            image=img_ref,
            num_frames=num_frames,
            num_inference_steps=steps,
            generator=generator
        )
    else:
        return {"exito": False, "error": f"Subtipo no soportado: {subtipo}", "archivo": None, "motor": "Wan 2.6 (local)"}

    # Exportar video a MP4
    from diffusers.utils import export_to_video
    export_to_video(resultado.frames[0], archivo_salida, fps=fps)

    return {
        "exito": True,
        "archivo": archivo_salida,
        "motor": f"Wan 2.6 {WAN_MODEL_SIZE} (local)",
        "resolucion": f"{width}x{height}",
        "duracion_s": duration,
        "fps": fps,
        "frames": num_frames
    }


# =============================================
# LIBERACIÓN DE MEMORIA
# =============================================
def liberar_modelos():
    """Libera los modelos de la GPU para recuperar VRAM."""
    global _wan_pipeline, _wan_i2v_pipeline, _qwen_pipeline
    import torch

    if _wan_pipeline is not None:
        del _wan_pipeline
        _wan_pipeline = None
    if _wan_i2v_pipeline is not None:
        del _wan_i2v_pipeline
        _wan_i2v_pipeline = None
    if _qwen_pipeline is not None:
        del _qwen_pipeline
        _qwen_pipeline = None

    torch.cuda.empty_cache()
    logger.info("Modelos locales liberados de la GPU")
