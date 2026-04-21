"""
ADSE - Agente Director Secundaria Educacion - Servidor Web + API
Conecta el frontend con el orquestador ADSE usando FastAPI + WebSocket.
Incluye autenticacion usuario/contrasena.
Puerto: 8006
"""

import os
import re
import asyncio
import logging
import json
import hmac
import hashlib
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Importar todo desde el modulo ADSE
from adse_core import (
    BASE_DIR, OBLIGACIONES_ADSE,
    GPT_DISPONIBLE,
    TAVILY_API_KEY, BASE_CONOCIMIENTO,
    buscar_en_internet, necesita_busqueda_web,
    buscar_conocimiento_local, clasificar_obligacion,
    cargar_memoria, agregar_a_memoria, obtener_contexto_reciente,
    obtener_historial, preguntar_gpt,
    crear_usuario, autenticar_usuario, validar_token, cerrar_sesion,
    crear_carpeta_usuario, guardar_dato_adse, obtener_datos_adse,
    verificar_suscripcion, SISTEMA_ADSE,
    get_db, logger
)

# INDEX_HTML se importa directamente como string Python
from adse_html import INDEX_HTML

# Exportacion a Word
try:
    from adse_export import crear_documento_sep, generar_nombre_archivo
    EXPORT_DISPONIBLE = True
    logger.info("Modulo de exportacion Word cargado")
except ImportError:
    EXPORT_DISPONIBLE = False
    logger.warning("Modulo de exportacion no disponible")

# Importar Stripe (opcional)
try:
    import stripe
    STRIPE_DISPONIBLE = True
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if STRIPE_API_KEY:
        stripe.api_key = STRIPE_API_KEY
    logger.info("Stripe cargado correctamente")
except ImportError:
    STRIPE_DISPONIBLE = False
    logger.warning("Stripe no disponible")


# ============================================
# CONFIGURACION DEL SERVIDOR
# ============================================

WEB_DIR = str(BASE_DIR / "web")

app = FastAPI(title="Agente Director Secundaria Educacion")


@app.get("/health")
async def health_check():
    """Endpoint de salud usado por el wrapper Electron para saber si el backend arranco."""
    return {"ok": True, "app": "adse", "mode": os.getenv("ADSE_MODE", "server")}

_default_origins = "http://localhost:8006,http://127.0.0.1:8006"
_cors_env = os.getenv("ADSE_CORS_ORIGINS", _default_origins)
CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
    ],
    allow_credentials=True,
)


# ============================================
# MIDDLEWARE ANTI-CACHE PARA HTML
# ============================================

@app.middleware("http")
async def agregar_headers_anticache(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/app") or request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# ============================================
# RUTAS HTML
# ============================================

@app.get("/app", response_class=HTMLResponse)
async def app_page():
    return INDEX_HTML

@app.get("/app2", response_class=HTMLResponse)
async def app_page2():
    return INDEX_HTML

@app.get("/app3", response_class=HTMLResponse)
async def app_page3():
    return INDEX_HTML

@app.get("/app4", response_class=HTMLResponse)
async def app_page4():
    return INDEX_HTML

@app.get("/app5", response_class=HTMLResponse)
async def app_page5():
    return INDEX_HTML

@app.get("/app6", response_class=HTMLResponse)
async def app_page6():
    return INDEX_HTML

@app.get("/app7", response_class=HTMLResponse)
async def app_page7():
    return INDEX_HTML

@app.get("/adse", response_class=HTMLResponse)
async def adse_page():
    return INDEX_HTML

@app.get("/adse2", response_class=HTMLResponse)
async def adse_page2():
    return INDEX_HTML

@app.get("/adse3", response_class=HTMLResponse)
async def adse_page3():
    return INDEX_HTML

@app.get("/adse4", response_class=HTMLResponse)
async def adse_page4():
    return INDEX_HTML

@app.get("/adse5", response_class=HTMLResponse)
async def adse_page5():
    return INDEX_HTML


# ============================================
# EXPORTACION A WORD
# ============================================

class ExportRequest(BaseModel):
    contenido: str
    funcion: Optional[str] = ''
    herramienta: Optional[str] = ''
    titulo: Optional[str] = 'Documento ADSE'
    zona: Optional[str] = ''
    escuela: Optional[str] = ''
    director: Optional[str] = ''

@app.post("/api/export/word")
async def export_word(req: ExportRequest):
    if not EXPORT_DISPONIBLE:
        raise HTTPException(status_code=500, detail="Modulo de exportacion no disponible")

    metadata = {
        'funcion': req.funcion,
        'herramienta': req.herramienta,
        'titulo': req.titulo,
        'zona': req.zona,
        'escuela': req.escuela,
        'director': req.director,
        'fecha': datetime.now().strftime('%d de %B de %Y')
    }

    buffer = crear_documento_sep(req.contenido, metadata)
    filename = generar_nombre_archivo(req.funcion or 'ADSE', req.herramienta or 'documento')

    return StreamingResponse(
        buffer,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


# ============================================
# MODELOS PYDANTIC
# ============================================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    nombre: str = ""
    email: str = ""

class DatosSincronizarRequest(BaseModel):
    funcion: str
    datos: dict

class CheckoutRequest(BaseModel):
    plan: str = "adse_100_monthly"


# ============================================
# AUTENTICACION HELPERS
# ============================================

def obtener_usuario_opcional(request: Request) -> dict | None:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        token = request.cookies.get("adse_token", "")
    if token:
        return validar_token(token)
    return None


def obtener_usuario_requerido(request: Request) -> dict:
    usuario = obtener_usuario_opcional(request)
    if not usuario:
        raise HTTPException(status_code=401, detail="No autenticado")
    return usuario


def requiere_suscripcion(request: Request) -> dict:
    usuario = obtener_usuario_requerido(request)
    suscripcion = verificar_suscripcion(usuario["id"])
    if not suscripcion["activa"]:
        raise HTTPException(
            status_code=403,
            detail="Suscripcion requerida. Activa tu plan de $100 MXN/mes."
        )
    return usuario


# ============================================
# PROCESAMIENTO DE MENSAJES
# ============================================

async def procesar_mensaje(mensaje: str, ws: WebSocket = None, usuario_id: int = None) -> dict:
    async def status(texto: str):
        if ws:
            try:
                await ws.send_json({"tipo": "status", "texto": texto})
            except Exception:
                pass

    await status("Clasificando mensaje...")
    agente_id = await asyncio.to_thread(clasificar_obligacion, mensaje)
    agente = OBLIGACIONES_ADSE[agente_id]
    await status(f"Obligacion asignada: {agente['nombre']} ({agente['grupo']})")

    fuentes = []
    info_web = ""
    info_rag = ""

    if necesita_busqueda_web(mensaje):
        await status("Buscando en internet...")
        res = await asyncio.to_thread(buscar_en_internet, mensaje)
        if res["exito"]:
            fuentes = res["fuentes"]
            info_web = "\n\nINFORMACION DE INTERNET:\n"
            if res["respuesta_directa"]:
                info_web += f"Resumen: {res['respuesta_directa']}\n\n"
            for r in res["resultados"][:3]:
                info_web += f"Fuente: {r['titulo']}\n{r['contenido']}\n\n"
            await status(f"Encontre {len(fuentes)} fuentes")

    await status("Buscando conocimiento RAG...")
    info_rag = await asyncio.to_thread(buscar_conocimiento_local, agente_id, mensaje)
    if info_rag:
        await status("Conocimiento RAG cargado")

    contexto = await asyncio.to_thread(obtener_contexto_reciente, 3, usuario_id)

    sistema = f"""{SISTEMA_ADSE}

Eres {agente['nombre']}, obligacion del Agente Director Secundaria Educacion.
Grupo: {agente['grupo']}. {agente['descripcion']}
REGLAS: Responde en espanol mexicano, claro y profesional. Se directo. Usa la info de internet y RAG si hay."""

    prompt = f"{contexto}\n{info_web}\n{info_rag}\nPREGUNTA: {mensaje}\nRespuesta:"

    await status(f"Generando respuesta con {agente['nombre']}...")

    motor_usado = ""
    respuesta = None

    if GPT_DISPONIBLE:
        respuesta = await asyncio.to_thread(preguntar_gpt, prompt, sistema)
        if respuesta:
            motor_usado = "Claude-Haiku"

    if not respuesta:
        respuesta = "No pude generar una respuesta en este momento. Verifica tu conexion a internet o intenta mas tarde."
        motor_usado = "Error"

    await asyncio.to_thread(
        agregar_a_memoria,
        mensaje, respuesta or "", agente["nombre"],
        [f["url"] for f in fuentes], usuario_id
    )

    return {
        "respuesta": respuesta or "Sin respuesta disponible",
        "agente": agente["nombre"],
        "funcion": agente["grupo"],
        "rol": agente["grupo"],
        "motor": motor_usado,
        "fuentes": fuentes
    }


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/api/registro")
async def api_registro(datos: RegisterRequest):
    if len(datos.username) < 3:
        raise HTTPException(400, "El usuario debe tener al menos 3 caracteres")
    if len(datos.password) < 8:
        raise HTTPException(400, "La contrasena debe tener al menos 8 caracteres")
    if len(datos.password) > 128:
        raise HTTPException(400, "La contrasena no puede exceder 128 caracteres")

    resultado = crear_usuario(datos.username, datos.password, datos.nombre, datos.email)
    if not resultado["exito"]:
        raise HTTPException(400, resultado["mensaje"])

    await asyncio.to_thread(crear_carpeta_usuario, resultado["usuario_id"])

    login = autenticar_usuario(datos.username, datos.password)
    response = JSONResponse(content=login)
    if login["exito"]:
        response.set_cookie(
            key="adse_token", value=login["token"],
            httponly=True, samesite="lax", max_age=86400
        )
    return response


@app.post("/api/login")
async def api_login(datos: LoginRequest):
    resultado = autenticar_usuario(datos.username, datos.password)
    if not resultado["exito"]:
        raise HTTPException(401, resultado["mensaje"])

    response = JSONResponse(content=resultado)
    response.set_cookie(
        key="adse_token", value=resultado["token"],
        httponly=True, samesite="lax", max_age=86400
    )
    return response


@app.post("/api/logout")
async def api_logout(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        token = request.cookies.get("adse_token", "")
    if token:
        cerrar_sesion(token)
    response = JSONResponse(content={"exito": True})
    response.delete_cookie("adse_token")
    return response


@app.get("/api/usuario")
async def api_usuario(request: Request):
    usuario = obtener_usuario_opcional(request)
    if not usuario:
        return {"autenticado": False}
    return {"autenticado": True, "usuario": usuario}


# ============================================
# API ENDPOINTS PRINCIPALES
# ============================================

@app.get("/")
async def index():
    return HTMLResponse(content=INDEX_HTML)


@app.get("/manifest.json")
async def manifest():
    return FileResponse(os.path.join(WEB_DIR, "manifest.json"))


@app.get("/api/status")
async def api_status():
    rag_count = 0
    if os.path.exists(BASE_CONOCIMIENTO):
        for f in os.listdir(BASE_CONOCIMIENTO):
            if f.endswith('.json'):
                rag_count += 1

    return {
        "gpt": GPT_DISPONIBLE,
        "claude": GPT_DISPONIBLE,
        "tavily": bool(TAVILY_API_KEY),
        "rag_archivos": rag_count,
        "obligaciones": len(OBLIGACIONES_ADSE),
        "motor": "Claude-Haiku",
        "auth": True,
        "suscripcion_requerida": True
    }


@app.get("/api/obligaciones")
async def api_obligaciones():
    return OBLIGACIONES_ADSE


@app.get("/api/memoria")
async def api_memoria(request: Request):
    usuario = obtener_usuario_opcional(request)
    usuario_id = usuario["id"] if usuario else None
    return obtener_historial(usuario_id, 20)


@app.get("/api/contexto")
async def api_contexto_get(request: Request):
    usuario = obtener_usuario_opcional(request)
    return {
        "obligaciones": len(OBLIGACIONES_ADSE),
        "gpt": GPT_DISPONIBLE,
        "claude": GPT_DISPONIBLE,
        "usuario_autenticado": usuario is not None
    }


@app.post("/api/contexto")
async def api_contexto_post(request: Request):
    usuario = obtener_usuario_opcional(request)
    try:
        datos = await request.json()
    except Exception:
        raise HTTPException(400, "JSON invalido")
    return {"exito": True, "mensaje": "Contexto guardado"}


@app.post("/api/consulta")
async def api_consulta(request: Request):
    usuario = obtener_usuario_opcional(request)
    usuario_id = usuario["id"] if usuario else None

    try:
        datos = await request.json()
    except Exception:
        raise HTTPException(400, "JSON invalido")

    mensaje = datos.get("consulta", "").strip()
    if not mensaje:
        raise HTTPException(400, "Consulta vacia")

    resultado = await procesar_mensaje(mensaje, ws=None, usuario_id=usuario_id)
    return resultado


# ============================================
# ENDPOINTS DE SINCRONIZACION DE DATOS
# ============================================

@app.post("/api/datos/sincronizar")
async def sincronizar_datos(datos: DatosSincronizarRequest, request: Request):
    usuario = obtener_usuario_requerido(request)

    try:
        resultado = await asyncio.to_thread(
            guardar_dato_adse,
            usuario["id"],
            datos.funcion,
            datos.datos
        )
        return {"exito": True, "mensaje": f"Datos de {datos.funcion} sincronizados"}
    except Exception as e:
        logger.error(f"Error al sincronizar datos: {e}")
        raise HTTPException(500, f"Error al sincronizar datos: {str(e)}")


@app.get("/api/datos/{funcion}")
async def obtener_datos_funcion(funcion: str, request: Request):
    usuario = obtener_usuario_requerido(request)

    try:
        datos = await asyncio.to_thread(
            obtener_datos_adse,
            usuario["id"],
            funcion
        )
        return {"exito": True, "funcion": funcion, "datos": datos}
    except Exception as e:
        raise HTTPException(500, f"Error al obtener datos: {str(e)}")


@app.post("/api/datos/{funcion}")
async def guardar_datos_funcion(funcion: str, request: Request):
    usuario = obtener_usuario_requerido(request)

    try:
        body = await request.json()
        resultado = await asyncio.to_thread(
            guardar_dato_adse,
            usuario["id"],
            funcion,
            body
        )
        return {"exito": True, "funcion": funcion, "mensaje": "Datos guardados"}
    except Exception as e:
        raise HTTPException(500, f"Error al guardar datos: {str(e)}")


# ============================================
# DOCUMENTOS ENCRIPTADOS DEL USUARIO (E2E)
# ============================================

@app.post("/api/documentos/guardar")
async def guardar_documento(request: Request):
    usuario = obtener_usuario_requerido(request)
    body = await request.json()

    required = ["funcion", "herramienta", "titulo", "contenido_encriptado", "iv", "salt"]
    for campo in required:
        if campo not in body:
            raise HTTPException(400, f"Falta campo requerido: {campo}")

    try:
        with get_db() as db:
            db.execute(
                """INSERT INTO documentos_usuario
                   (usuario_id, funcion, herramienta, titulo, contenido_encriptado, iv, salt, tamano)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (usuario["id"], body["funcion"], body["herramienta"], body["titulo"],
                 body["contenido_encriptado"], body["iv"], body["salt"],
                 len(body["contenido_encriptado"]))
            )
        return {"exito": True, "mensaje": "Documento respaldado de forma segura"}
    except Exception as e:
        raise HTTPException(500, "Error al guardar documento")


@app.get("/api/documentos/listar")
async def listar_documentos(request: Request):
    usuario = obtener_usuario_requerido(request)

    try:
        with get_db() as db:
            rows = db.execute(
                """SELECT id, funcion, herramienta, titulo, tamano, creado_en
                   FROM documentos_usuario WHERE usuario_id = ?
                   ORDER BY creado_en DESC""",
                (usuario["id"],)
            ).fetchall()
        docs = [{"id": r["id"], "funcion": r["funcion"], "herramienta": r["herramienta"],
                 "titulo": r["titulo"], "tamano": r["tamano"], "creado_en": r["creado_en"]}
                for r in rows]
        return {"exito": True, "documentos": docs, "total": len(docs)}
    except Exception as e:
        raise HTTPException(500, "Error al listar documentos")


@app.get("/api/documentos/{doc_id}")
async def obtener_documento(doc_id: int, request: Request):
    usuario = obtener_usuario_requerido(request)

    try:
        with get_db() as db:
            row = db.execute(
                """SELECT id, funcion, herramienta, titulo, contenido_encriptado, iv, salt, creado_en
                   FROM documentos_usuario WHERE id = ? AND usuario_id = ?""",
                (doc_id, usuario["id"])
            ).fetchone()
        if not row:
            raise HTTPException(404, "Documento no encontrado")
        return {"exito": True, "documento": {
            "id": row["id"], "funcion": row["funcion"], "herramienta": row["herramienta"],
            "titulo": row["titulo"], "contenido_encriptado": row["contenido_encriptado"],
            "iv": row["iv"], "salt": row["salt"], "creado_en": row["creado_en"]
        }}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, "Error al obtener documento")


# ============================================
# SUSCRIPCION
# ============================================

@app.get("/api/suscripcion")
async def obtener_suscripcion(request: Request):
    usuario = obtener_usuario_requerido(request)
    suscripcion = verificar_suscripcion(usuario["id"])
    return suscripcion


# ============================================
# WEBSOCKET
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    origin = ws.headers.get("origin", "")
    allowed_origins = [
        "http://localhost:8006",
        "http://127.0.0.1:8006",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
    ]

    if origin and origin not in allowed_origins:
        await ws.close(code=1008, reason="Origen no permitido")
        return

    await ws.accept()
    logger.info("WebSocket cliente conectado")
    usuario_id = None
    usuario_tiene_suscripcion = False

    try:
        while True:
            data = await ws.receive_json()

            if data.get("tipo") == "auth":
                token = data.get("token", "")
                usuario = validar_token(token)
                if usuario:
                    usuario_id = usuario["id"]
                    suscripcion = verificar_suscripcion(usuario_id)
                    usuario_tiene_suscripcion = suscripcion.get("activa", False)
                    await ws.send_json({
                        "tipo": "auth",
                        "exito": True,
                        "usuario": usuario,
                        "suscripcion_activa": usuario_tiene_suscripcion
                    })
                else:
                    await ws.send_json({"tipo": "auth", "exito": False})
                continue

            if usuario_id and not usuario_tiene_suscripcion:
                await ws.send_json({
                    "tipo": "error",
                    "texto": "Suscripcion requerida. Activa tu plan de $100 MXN/mes."
                })
                continue

            mensaje = data.get("consulta", data.get("mensaje", "")).strip()
            if not mensaje:
                continue

            try:
                resultado = await procesar_mensaje(mensaje, ws, usuario_id)

                await ws.send_json({
                    "tipo": "respuesta",
                    "respuesta": resultado.get("respuesta", "Sin respuesta"),
                    "agente": resultado.get("agente", "ADSE"),
                    "rol": resultado.get("rol", "General"),
                    "motor": resultado.get("motor", "N/A"),
                    "fuentes": resultado.get("fuentes", [])
                })
            except Exception as proc_err:
                logger.error(f"Error procesando mensaje: {proc_err}")
                await ws.send_json({"tipo": "error", "texto": f"Error al procesar: {str(proc_err)}"})

    except WebSocketDisconnect:
        logger.info("WebSocket cliente desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        try:
            await ws.send_json({"tipo": "error", "texto": str(e)})
        except Exception:
            pass


# ============================================
# ARCHIVOS ESTATICOS
# ============================================
if os.path.exists(WEB_DIR):
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


# ============================================
# INICIO
# ============================================
if __name__ == "__main__":
    stripe_status = "ACTIVO" if STRIPE_DISPONIBLE else "NO DISPONIBLE"
    claude_status = "ACTIVO" if GPT_DISPONIBLE else "NO DISPONIBLE"

    banner = f"""
+==================================================+
|  AGENTE DIRECTOR SECUNDARIA EDUCACION (ADSE)     |
|  Servidor Web: http://localhost:8006             |
|  Motor IA: Claude Haiku (Anthropic)              |
|  Obligaciones ADSE: 7 | Tareas: 67              |
|  Normatividad: Acuerdo 98 | NEM Fase 6           |
|  Estado:                                         |
|  - Claude: {claude_status:<33} |
|  - Stripe: {stripe_status:<33} |
|  Auth: usuario/contrasena habilitado             |
+==================================================+
"""
    print(banner)
    os.makedirs(WEB_DIR, exist_ok=True)
    host = os.getenv("ADSE_HOST", "0.0.0.0")
    port = int(os.getenv("ADSE_PORT", "8006"))
    reload = os.getenv("ADSE_RELOAD", "1") == "1"
    uvicorn.run("servidor_adse:app", host=host, port=port, reload=reload)
