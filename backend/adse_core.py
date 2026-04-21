"""
ADSE Core - Módulo especializado para Agente Director Secundaria Educación
Centraliza configuración, 7 obligaciones / 67 tareas, memoria (SQLite),
RAG (TF-IDF), clasificación híbrida, autenticación y Anthropic Claude.
"""

import os
import re
import json
import sqlite3
import hashlib
import logging
import requests
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
except ImportError:
    pass

# =============================================
# LOGGING
# =============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("adse")

# =============================================
# CONFIGURACIÓN
# =============================================
BASE_DIR = Path(__file__).resolve().parent

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
TAVILY_URL = "https://api.tavily.com/search"
BASE_CONOCIMIENTO = str(BASE_DIR / "conocimiento_adse")
DB_PATH = str(BASE_DIR / "adse.db")
DATOS_USUARIOS_DIR = BASE_DIR / "datos_usuarios"

DATOS_USUARIOS_DIR.mkdir(exist_ok=True)

JWT_SECRET = os.environ.get("ADSE_JWT_SECRET", "adse-dev-secret-cambiar-en-produccion")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# =============================================
# ANTHROPIC CLAUDE CONFIGURATION
# =============================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_DISPONIBLE = False
cliente_anthropic = None

try:
    from anthropic import Anthropic
    if ANTHROPIC_API_KEY:
        cliente_anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        CLAUDE_DISPONIBLE = True
        logger.info("Anthropic Claude disponible")
    else:
        logger.warning("ANTHROPIC_API_KEY no configurada")
except ImportError:
    logger.warning("Módulo anthropic no instalado, ejecuta: pip install anthropic")

GPT_DISPONIBLE = CLAUDE_DISPONIBLE

# =============================================
# STRIPE CONFIGURATION
# =============================================
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# =============================================
# TF-IDF para RAG mejorado
# =============================================
_tfidf_vectorizer = None
_tfidf_matrix = None
_tfidf_docs = []
_tfidf_initialized = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    TFIDF_DISPONIBLE = True
    logger.info("TF-IDF (scikit-learn) disponible")
except ImportError:
    TFIDF_DISPONIBLE = False
    logger.warning("scikit-learn no instalado, usando búsqueda por keywords")

# =============================================
# 7 OBLIGACIONES DEL DIRECTOR DE SECUNDARIA (67 TAREAS)
# =============================================
AGENTES_ADSE = {

    # ══════════════════════════════════════════════
    # OBLIGACION 1: GESTION ACADEMICO-PEDAGOGICA (8 tareas)
    # ══════════════════════════════════════════════

    "O1A": {
        "nombre": "Programa Analitico (PA) Fase 6",
        "icono": "📋",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Codiseno del PA en CTE para secundaria, lectura de la realidad, contenidos por asignatura (Espanol, Matematicas, Ciencias, Historia, etc.), firmas del colectivo docente",
        "palabras_clave": ["programa analitico", "pa", "codiseno", "contenidos", "asignatura", "fase 6", "pda", "programa sintetico", "plan de estudios"]
    },
    "O1B": {
        "nombre": "PEMC (Programa Escolar de Mejora Continua)",
        "icono": "📊",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Diagnostico integral 8 ambitos, objetivos, metas, acciones de mejora, indicadores, seguimiento en CTE, semaforo de avance",
        "palabras_clave": ["pemc", "mejora continua", "diagnostico", "8 ambitos", "objetivo", "meta", "indicador", "semaforo"]
    },
    "O1C": {
        "nombre": "Acompanamiento Pedagogico",
        "icono": "👁️",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Visitas a aulas, laboratorios y talleres; observacion de clases por asignatura; retroalimentacion docente; bitacora; calendario de visitas a multiples maestros",
        "palabras_clave": ["acompanamiento", "visita", "observacion", "retroalimentacion", "indicador", "bitacora", "aula", "laboratorio", "taller"]
    },
    "O1D": {
        "nombre": "Evaluacion del Aprendizaje",
        "icono": "📝",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Evaluacion trimestral con calificaciones numericas (5-10), concentrados por grupo y asignatura, analisis de resultados, boletas, PLANEA/MEJOREDU",
        "palabras_clave": ["evaluacion", "calificacion", "boleta", "trimestral", "concentrado", "periodo", "aprendizaje", "planea", "mejoredu", "resultado"]
    },
    "O1E": {
        "nombre": "Materiales y LTG",
        "icono": "📚",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Acta de recepcion de libros de texto por asignatura y grado, inventario, distribucion a docentes y alumnos, checklist de uso",
        "palabras_clave": ["material", "ltg", "libro", "texto gratuito", "inventario", "recepcion", "distribucion", "asignatura"]
    },
    "O1F": {
        "nombre": "Inclusion y NEE/USAER",
        "icono": "♿",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Deteccion de alumnos con NEE, coordinacion con USAER, ajustes razonables, registro de BAP, seguimiento, atencion a diversidad (lengua indigena, discapacidad, aptitudes sobresalientes)",
        "palabras_clave": ["inclusion", "nee", "necesidades especiales", "usaer", "bap", "discapacidad", "barrera", "deteccion", "ajuste razonable", "diversidad"]
    },
    "O1G": {
        "nombre": "Tutorias y Orientacion Educativa",
        "icono": "🧭",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Programa de tutorias por grupo, Plan de Accion Tutorial, seguimiento a tutores, orientador educativo, atencion a problemas academicos y conductuales, canalizacion",
        "palabras_clave": ["tutoria", "tutor", "orientacion", "orientador", "plan accion tutorial", "conducta", "canalizacion", "apoyo"]
    },
    "O1H": {
        "nombre": "Orientacion Vocacional 3er Grado",
        "icono": "🎯",
        "grupo": "OBL1",
        "obligacion": "Gestion Academico-Pedagogica",
        "color": "#4A148C",
        "descripcion": "Programa de orientacion vocacional para 3er grado, tests vocacionales, informacion de opciones EMS (preparatoria, bachillerato, CONALEP), ferias vocacionales, vinculacion con instituciones",
        "palabras_clave": ["vocacional", "orientacion vocacional", "tercer grado", "preparatoria", "bachillerato", "ems", "test vocacional", "feria", "opciones"]
    },

    # ══════════════════════════════════════════════
    # OBLIGACION 2: CONSEJO TECNICO ESCOLAR (6 tareas)
    # ══════════════════════════════════════════════

    "O2A": {
        "nombre": "Instalacion del CTE",
        "icono": "🏫",
        "grupo": "OBL2",
        "obligacion": "Consejo Tecnico Escolar",
        "color": "#1565C0",
        "descripcion": "Acta constitutiva del CTE, convocatoria a todo el colectivo docente (maestros por asignatura, subdirector, orientador, prefectos), Acuerdo 05/04/24",
        "palabras_clave": ["instalar cte", "acta constitutiva", "convocatoria", "consejo tecnico", "cte", "colectivo"]
    },
    "O2B": {
        "nombre": "Fase Intensiva CTE",
        "icono": "📅",
        "grupo": "OBL2",
        "obligacion": "Consejo Tecnico Escolar",
        "color": "#1565C0",
        "descripcion": "5 dias agosto, diagnostico socioeducativo, lectura de la realidad, elaboracion PA y PEMC, itinerario del CTE para el ciclo",
        "palabras_clave": ["fase intensiva", "agosto", "diagnostico", "lectura de la realidad", "itinerario"]
    },
    "O2C": {
        "nombre": "Sesiones Ordinarias CTE",
        "icono": "📆",
        "grupo": "OBL2",
        "obligacion": "Consejo Tecnico Escolar",
        "color": "#1565C0",
        "descripcion": "8-10 sesiones mensuales (1er viernes de cada mes), temas del itinerario, seguimiento al PEMC, acuerdos, productos, participacion del colectivo",
        "palabras_clave": ["sesion ordinaria", "sesion cte", "mensual", "acuerdo", "producto", "tema", "viernes"]
    },
    "O2D": {
        "nombre": "Comite de Planeacion y Evaluacion",
        "icono": "📋",
        "grupo": "OBL2",
        "obligacion": "Consejo Tecnico Escolar",
        "color": "#1565C0",
        "descripcion": "Conformar comite con subdirector y docentes clave, coordinar formulacion y evaluacion del PEMC, sistematizar informacion del diagnostico",
        "palabras_clave": ["comite planeacion", "comite evaluacion", "formulacion", "sistematizar", "subdirector"]
    },
    "O2E": {
        "nombre": "Seguimiento al PEMC en CTE",
        "icono": "📈",
        "grupo": "OBL2",
        "obligacion": "Consejo Tecnico Escolar",
        "color": "#1565C0",
        "descripcion": "Revision de avances de cada meta en sesion ordinaria, ajustes a acciones, reorientacion de estrategias, analisis de indicadores",
        "palabras_clave": ["seguimiento", "avance", "ajuste", "reorientacion", "revision pemc", "indicador"]
    },
    "O2F": {
        "nombre": "Actas y Evidencias CTE",
        "icono": "📁",
        "grupo": "OBL2",
        "obligacion": "Consejo Tecnico Escolar",
        "color": "#1565C0",
        "descripcion": "Actas de sesion firmadas por colectivo, listas de asistencia, portafolio de evidencias, registro fotografico, productos de sesion",
        "palabras_clave": ["acta cte", "lista asistencia", "evidencia", "portafolio", "firma", "registro", "producto"]
    },

    # ══════════════════════════════════════════════
    # OBLIGACION 3: CONTROL ESCOLAR (10 tareas)
    # ══════════════════════════════════════════════

    "O3A": {
        "nombre": "Inscripciones y SAID",
        "icono": "📝",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Inscripcion de alumnos de 1er grado, verificacion de certificado de primaria, CURP, documentacion completa, captura en SIGED, Sistema SAID donde aplique",
        "palabras_clave": ["inscripcion", "nuevo ingreso", "said", "primer grado", "documentacion", "expediente", "certificado primaria"]
    },
    "O3B": {
        "nombre": "Reinscripciones",
        "icono": "🔄",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Registro de alumnos que pasan a 2do y 3er grado, actualizacion de datos, verificacion de acreditacion del grado anterior",
        "palabras_clave": ["reinscripcion", "continuan", "actualizacion", "segundo grado", "tercer grado", "promovido"]
    },
    "O3C": {
        "nombre": "Preinscripciones",
        "icono": "📋",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Proceso febrero para siguiente ciclo escolar, convocatoria a primarias de la zona, difusion de oferta educativa, SAID",
        "palabras_clave": ["preinscripcion", "convocatoria", "siguiente ciclo", "febrero", "oferta educativa"]
    },
    "O3D": {
        "nombre": "Acreditacion y Promocion",
        "icono": "✅",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Calificaciones numericas 5-10, criterios de acreditacion, alumnos en riesgo de reprobacion, evaluaciones extraordinarias, promocion de grado",
        "palabras_clave": ["acreditacion", "promocion", "grado", "calificacion", "reprobacion", "extraordinaria", "acreditar", "promover"]
    },
    "O3E": {
        "nombre": "Certificacion 3er Grado",
        "icono": "🎓",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Certificado de terminacion de educacion secundaria, captura de calificaciones finales, tramite ante control escolar, entrega en ceremonia de graduacion",
        "palabras_clave": ["certificacion", "certificado", "tercer grado", "3er grado", "terminacion", "secundaria", "graduacion"]
    },
    "O3F": {
        "nombre": "Boletas de Evaluacion",
        "icono": "📄",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "3 trimestres, calificaciones numericas por asignatura (Espanol, Matematicas, Ciencias, Historia, Geografia, FCyE, Artes, Tecnologia, Ed. Fisica, Ingles, Tutorias), entrega a padres",
        "palabras_clave": ["boleta", "evaluacion", "entrega", "calificacion", "asignatura", "padres", "trimestre"]
    },
    "O3G": {
        "nombre": "Estadistica 911.5",
        "icono": "📊",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Formato 911.5 para secundaria, matricula por grado/grupo/genero, inicio y fin de cursos, desercion, reprobacion, eficiencia terminal, plataforma f911.sep.gob.mx",
        "palabras_clave": ["estadistica", "911", "formato 911", "911.5", "matricula", "f911", "inicio cursos", "fin cursos", "desercion", "eficiencia"]
    },
    "O3H": {
        "nombre": "SIGED",
        "icono": "💻",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Sistema de Informacion y Gestion Educativa, captura de datos de alumnos y personal, CCT de la secundaria, actualizacion permanente",
        "palabras_clave": ["siged", "sistema", "informacion", "gestion educativa", "captura", "cct"]
    },
    "O3I": {
        "nombre": "Altas, Bajas y Traslados",
        "icono": "🔀",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Gestion de movimientos de alumnos, constancias de traslado, registro en sistema, recepcion de alumnos de otras secundarias, documentacion requerida",
        "palabras_clave": ["alta", "baja", "traslado", "movimiento", "constancia", "cambio escuela", "transferencia"]
    },
    "O3J": {
        "nombre": "Expedientes y Kardex",
        "icono": "📂",
        "grupo": "OBL3",
        "obligacion": "Control Escolar",
        "color": "#2E7D32",
        "descripcion": "Expediente completo: acta nacimiento, CURP, certificado primaria, boletas, kardex con historial academico por asignatura, fotografia, documentacion medica",
        "palabras_clave": ["expediente", "kardex", "historial", "acta nacimiento", "curp", "documentacion alumno", "fotografia"]
    },

    # ══════════════════════════════════════════════
    # OBLIGACION 4: GESTION ADMINISTRATIVA (10 tareas)
    # ══════════════════════════════════════════════

    "O4A": {
        "nombre": "Inventario de Bienes",
        "icono": "📦",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Inventario de muebles, equipo de laboratorio, equipo de taller, computo, inmuebles, altas/bajas de bienes, activo fijo, sello oficial",
        "palabras_clave": ["inventario", "bienes", "mueble", "inmueble", "activo fijo", "laboratorio", "taller", "equipo", "computo"]
    },
    "O4B": {
        "nombre": "Resguardo Documental",
        "icono": "🔒",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Custodia de documentacion oficial, archivo actualizado, actas, oficios, sello y firma del director, control de documentos sensibles",
        "palabras_clave": ["resguardo", "custodia", "documento oficial", "archivo", "documentacion", "sello", "firma"]
    },
    "O4C": {
        "nombre": "Recursos Materiales y Laboratorios",
        "icono": "🔬",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Administracion de laboratorios de ciencias (Fisica, Quimica, Biologia), talleres tecnologicos, materiales didacticos, reactivos, equipo de computo",
        "palabras_clave": ["recurso material", "laboratorio", "taller", "reactivo", "material didactico", "computo", "ciencias"]
    },
    "O4D": {
        "nombre": "Mantenimiento del Plantel",
        "icono": "🔧",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Conservacion de aulas, laboratorios, talleres, canchas, sanitarios, bardas, instalaciones electricas e hidraulicas, coordinacion con APF y autoridades",
        "palabras_clave": ["mantenimiento", "conservacion", "inmueble", "plantel", "reparacion", "instalaciones", "cancha", "sanitario"]
    },
    "O4E": {
        "nombre": "Archivo Escolar",
        "icono": "🗄️",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Archivo de tramite y concentracion, inventario de transferencia, organizacion documental, expedientes de generaciones anteriores",
        "palabras_clave": ["archivo escolar", "archivo tramite", "transferencia", "organizacion", "expediente", "generacion"]
    },
    "O4F": {
        "nombre": "Correspondencia Oficial",
        "icono": "✉️",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Oficios, memorandums, circulares, comunicados, registro de entrada/salida de documentos, distribucion al personal",
        "palabras_clave": ["oficio", "memorandum", "circular", "correspondencia", "comunicado", "registro"]
    },
    "O4G": {
        "nombre": "Informes a Supervision",
        "icono": "📤",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Datos estadisticos, reportes a supervision escolar y jefatura de sector, informacion para autoridades educativas, informes mensuales y bimestrales",
        "palabras_clave": ["informe", "supervision", "reporte", "estadistico", "autoridad educativa", "jefatura", "sector"]
    },
    "O4H": {
        "nombre": "Gestion de Personal",
        "icono": "👥",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Plantilla de personal: director, subdirector(es), docentes por asignatura, prefectos, orientador, trabajador social, administrativos, intendencia. Control de asistencia, incidencias, permisos, licencias",
        "palabras_clave": ["personal", "asistencia", "incidencia", "permiso", "licencia", "plantilla", "subdirector", "prefecto", "orientador", "trabajador social", "docente"]
    },
    "O4I": {
        "nombre": "Programa La Escuela es Nuestra",
        "icono": "🏛️",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "PLEEN, recursos federales, acompanamiento al CEAP, rendicion de cuentas, administracion transparente de recursos",
        "palabras_clave": ["escuela es nuestra", "leen", "pleen", "recurso federal", "ceap", "presupuesto"]
    },
    "O4J": {
        "nombre": "Gestion de Horarios",
        "icono": "🕐",
        "grupo": "OBL4",
        "obligacion": "Gestion Administrativa",
        "color": "#E65100",
        "descripcion": "Elaboracion de horarios complejos: multiples docentes por asignatura, distribucion de aulas, laboratorios y talleres, turnos matutino/vespertino, horas de tutorias",
        "palabras_clave": ["horario", "turno", "matutino", "vespertino", "distribucion", "asignatura", "aula", "carga horaria"]
    },

    # ══════════════════════════════════════════════
    # OBLIGACION 5: PARTICIPACION SOCIAL (7 tareas)
    # ══════════════════════════════════════════════

    "O5A": {
        "nombre": "Conformacion del CEAP",
        "icono": "🤝",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Comite Escolar de Administracion Participativa, asamblea escolar, eleccion de integrantes, representantes de padres y docentes",
        "palabras_clave": ["ceap", "comite escolar", "asamblea", "administracion participativa", "eleccion"]
    },
    "O5B": {
        "nombre": "Asambleas con Padres",
        "icono": "👨‍👩‍👧",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Asambleas bimestrales, convocatoria, informar avances academicos y administrativos, participacion comunitaria, firma de asistencia",
        "palabras_clave": ["asamblea", "padres", "reunion", "bimestral", "comunidad", "participacion"]
    },
    "O5C": {
        "nombre": "Rendicion de Cuentas",
        "icono": "💰",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Informe bimestral de gastos, transparencia de recursos, periodico mural, fotografias antes/despues de mejoras, reporte a supervision",
        "palabras_clave": ["rendicion", "cuentas", "transparencia", "gasto", "informe", "periodico mural"]
    },
    "O5D": {
        "nombre": "Asociacion de Padres de Familia",
        "icono": "👪",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Constitucion de APF en primeros 15 dias del ciclo, acta constitutiva, mesa directiva, plan de trabajo, coordinacion con direccion",
        "palabras_clave": ["apf", "asociacion padres", "mesa directiva", "constitucion", "padre familia"]
    },
    "O5E": {
        "nombre": "Sociedad de Alumnos",
        "icono": "🎒",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Integracion obligatoria (Acuerdo 98), eleccion democratica, plan de actividades, participacion estudiantil, eventos culturales y deportivos",
        "palabras_clave": ["sociedad alumnos", "eleccion", "representante", "estudiantil", "participacion", "democratica"]
    },
    "O5F": {
        "nombre": "Vinculacion Comunitaria",
        "icono": "🌐",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Coordinacion con autoridades municipales, programas de bienestar, actividades culturales y civicas, servicio comunitario de alumnos",
        "palabras_clave": ["vinculacion", "comunidad", "municipio", "bienestar", "cultural", "civica", "servicio comunitario"]
    },
    "O5G": {
        "nombre": "Contraloria Social",
        "icono": "🔍",
        "grupo": "OBL5",
        "obligacion": "Participacion Social",
        "color": "#6A1B9A",
        "descripcion": "Comite de Contraloria Social, vocales de transparencia, vigilancia del uso de recursos, informes publicos",
        "palabras_clave": ["contraloria", "vigilancia", "transparencia", "vocal", "supervision recursos"]
    },

    # ══════════════════════════════════════════════
    # OBLIGACION 6: SEGURIDAD, SALUD Y CONVIVENCIA (10 tareas)
    # ══════════════════════════════════════════════

    "O6A": {
        "nombre": "Comite de Proteccion Civil",
        "icono": "🛡️",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Comite de Proteccion Civil y Seguridad Escolar, acta constitutiva, formato EX-01, Acuerdo Secretarial 535",
        "palabras_clave": ["proteccion civil", "comite seguridad", "acta constitutiva", "seguridad escolar"]
    },
    "O6B": {
        "nombre": "Programa Interno Proteccion Civil",
        "icono": "📕",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "PIPCE, plan de emergencia, directorio de emergencias, Ley General de Proteccion Civil, rutas de evacuacion, puntos de reunion",
        "palabras_clave": ["pipce", "programa interno", "proteccion civil", "emergencia", "plan emergencia"]
    },
    "O6C": {
        "nombre": "Simulacros",
        "icono": "🚨",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Minimo 4 por ciclo, calendario, bitacora, evaluacion post-simulacro, coordinacion con UMPC, participacion de toda la comunidad escolar",
        "palabras_clave": ["simulacro", "evacuacion", "sismo", "incendio", "bitacora", "calendario simulacro"]
    },
    "O6D": {
        "nombre": "Botiquin y Primeros Auxilios",
        "icono": "🏥",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Botiquin vigente en direccion y laboratorios, inventario actualizado, manual de primeros auxilios, capacitacion de brigadas",
        "palabras_clave": ["botiquin", "primeros auxilios", "medicamento", "curacion", "inventario botiquin"]
    },
    "O6E": {
        "nombre": "Senalizacion y Extintores",
        "icono": "🧯",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "NOM-026-STPS senalizacion, rutas evacuacion, salidas emergencia, croquis del plantel, extintores con certificado vigente (NOM-002-STPS), recarga anual",
        "palabras_clave": ["senalizacion", "ruta evacuacion", "extintor", "salida emergencia", "croquis", "senal", "nom"]
    },
    "O6F": {
        "nombre": "Brigadas Escolares",
        "icono": "🦺",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "4 brigadas: evacuacion, primeros auxilios, prevencion de incendios, comunicacion. Constancias anuales, capacitacion, integracion con personal y alumnos",
        "palabras_clave": ["brigada", "brigadista", "evacuacion", "capacitacion brigada", "constancia"]
    },
    "O6G": {
        "nombre": "Protocolo Acoso Escolar (Bullying)",
        "icono": "🚫",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Protocolo SEP para erradicacion del acoso escolar: Deteccion, Notificacion, Intervencion, Seguimiento. Practicas restaurativas, documentacion de casos, reporte a supervision",
        "palabras_clave": ["acoso", "bullying", "protocolo acoso", "violencia escolar", "deteccion", "intervencion", "restaurativa", "convivencia"]
    },
    "O6H": {
        "nombre": "Revision de Instalaciones",
        "icono": "🏗️",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Diagnostico de seguridad del plantel, riesgos internos y externos, mapa de riesgos, revision de laboratorios, talleres, canchas, sanitarios, bardas",
        "palabras_clave": ["instalaciones", "diagnostico seguridad", "riesgo", "mapa riesgos", "inmueble"]
    },
    "O6I": {
        "nombre": "Comite de Salud Escolar",
        "icono": "❤️",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Acta de instalacion, REPASE, higiene del plantel, nutricion y tienda escolar saludable, jornadas de limpieza, campanas de salud",
        "palabras_clave": ["comite salud", "salud escolar", "higiene", "nutricion", "limpieza", "repase", "tienda escolar"]
    },
    "O6J": {
        "nombre": "Protocolo de Maltrato Infantil",
        "icono": "⚠️",
        "grupo": "OBL6",
        "obligacion": "Seguridad, Salud y Convivencia",
        "color": "#C62828",
        "descripcion": "Identificacion de senales de alerta, notificacion a DIF/Ministerio Publico, resguardo del alumno, documentacion, seguimiento, vinculacion con autoridades",
        "palabras_clave": ["maltrato", "abuso", "alerta", "dif", "ministerio publico", "denuncia", "proteccion", "victima"]
    },

    # ══════════════════════════════════════════════
    # OBLIGACION 7: FORMACION CONTINUA (6 tareas)
    # ══════════════════════════════════════════════

    "O7A": {
        "nombre": "TIFC (Taller Intensivo)",
        "icono": "🎓",
        "grupo": "OBL7",
        "obligacion": "Formacion Continua",
        "color": "#00695C",
        "descripcion": "Talleres intensivos de formacion continua en agosto y julio, sesiones para directivos y docentes, temas del ciclo escolar",
        "palabras_clave": ["tifc", "taller intensivo", "formacion continua", "taller", "agosto", "julio"]
    },
    "O7B": {
        "nombre": "Diagnostico de Necesidades Formativas",
        "icono": "🔎",
        "grupo": "OBL7",
        "obligacion": "Formacion Continua",
        "color": "#00695C",
        "descripcion": "Encuestas al personal docente, observaciones en aula, matrices de necesidades, areas de fortalecimiento del colectivo por asignatura",
        "palabras_clave": ["diagnostico necesidades", "necesidades formativas", "encuesta", "fortalecimiento", "asignatura"]
    },
    "O7C": {
        "nombre": "Plan de Formacion del Colectivo",
        "icono": "📖",
        "grupo": "OBL7",
        "obligacion": "Formacion Continua",
        "color": "#00695C",
        "descripcion": "Acciones formativas alineadas al diagnostico, cronograma anual, Estrategia Estatal de Formacion, temas prioritarios por academia/asignatura",
        "palabras_clave": ["plan formacion", "acciones formativas", "estrategia", "cronograma formacion", "academia"]
    },
    "O7D": {
        "nombre": "Procesos USICAMM",
        "icono": "🏅",
        "grupo": "OBL7",
        "obligacion": "Formacion Continua",
        "color": "#00695C",
        "descripcion": "Convocatorias de admision, promocion vertical y horizontal, reconocimiento docente, procesos de seleccion, informar al personal",
        "palabras_clave": ["usicamm", "promocion", "admision", "reconocimiento", "convocatoria", "seleccion"]
    },
    "O7E": {
        "nombre": "Cursos y Catalogos de Formacion",
        "icono": "💻",
        "grupo": "OBL7",
        "obligacion": "Formacion Continua",
        "color": "#00695C",
        "descripcion": "Catalogo de formacion continua DGFCDD, inscripcion del personal a cursos, seguimiento de participacion, constancias de formacion",
        "palabras_clave": ["dgfcdd", "catalogo", "curso", "formacion continua", "inscripcion curso", "constancia"]
    },
    "O7F": {
        "nombre": "Formacion de Directivos",
        "icono": "👔",
        "grupo": "OBL7",
        "obligacion": "Formacion Continua",
        "color": "#00695C",
        "descripcion": "Desarrollo profesional del director y subdirector, liderazgo escolar, gestion educativa, comunidades de aprendizaje entre directivos",
        "palabras_clave": ["formacion directivo", "liderazgo", "desarrollo profesional", "comunidad aprendizaje", "gestion"]
    },
}

CARPETAS_CONOCIMIENTO = {k: v["nombre"].lower() for k, v in AGENTES_ADSE.items()}

# Alias para compatibilidad
OBLIGACIONES_ADSE = AGENTES_ADSE

# =============================================
# OBLIGACIONES PARA EL FRONTEND
# =============================================
OBLIGACIONES_LISTA_ADSE = [
    {
        "id": "OBL1",
        "nombre": "Gestion Academico-Pedagogica",
        "icono": "📋",
        "color": "#4A148C",
        "descripcion": "Programa Analitico Fase 6, PEMC, acompanamiento pedagogico, evaluacion, materiales, inclusion, tutorias, orientacion vocacional"
    },
    {
        "id": "OBL2",
        "nombre": "Consejo Tecnico Escolar",
        "icono": "🏫",
        "color": "#1565C0",
        "descripcion": "Instalacion del CTE, fase intensiva, sesiones ordinarias, comite de planeacion, seguimiento al PEMC, actas y evidencias"
    },
    {
        "id": "OBL3",
        "nombre": "Control Escolar",
        "icono": "📊",
        "color": "#2E7D32",
        "descripcion": "Inscripciones/SAID, reinscripciones, acreditacion, certificacion, boletas, 911.5, SIGED, expedientes, kardex, traslados"
    },
    {
        "id": "OBL4",
        "nombre": "Gestion Administrativa",
        "icono": "🗂️",
        "color": "#E65100",
        "descripcion": "Inventario, laboratorios, talleres, mantenimiento, archivo, correspondencia, personal (subdirector, prefectos, orientador), horarios, PLEEN"
    },
    {
        "id": "OBL5",
        "nombre": "Participacion Social",
        "icono": "👨‍👩‍👧",
        "color": "#6A1B9A",
        "descripcion": "CEAP, asambleas, rendicion de cuentas, APF, Sociedad de Alumnos (obligatoria Acuerdo 98), vinculacion, contraloria social"
    },
    {
        "id": "OBL6",
        "nombre": "Seguridad, Salud y Convivencia",
        "icono": "🛡️",
        "color": "#C62828",
        "descripcion": "Proteccion civil, simulacros, brigadas, protocolo acoso escolar (bullying), maltrato infantil, instalaciones, salud escolar"
    },
    {
        "id": "OBL7",
        "nombre": "Formacion Continua",
        "icono": "🎓",
        "color": "#00695C",
        "descripcion": "TIFC, diagnostico de necesidades, plan de formacion, USICAMM, cursos DGFCDD, formacion de directivos"
    },
]

# =============================================
# SISTEMA PROMPT PARA ADSE
# =============================================
SISTEMA_ADSE = """Eres ADSE (Agente Director Secundaria Educacion), un asistente especializado para
directores de escuelas secundarias en Mexico, bajo el marco de la SEP.

Tu conocimiento incluye:
- Acuerdo Secretarial 98 (organizacion y funcionamiento de secundarias, 73 articulos)
- Nueva Escuela Mexicana (NEM) Fase 6 (1ro, 2do y 3er grado de secundaria)
- Plan de estudios de secundaria: Espanol, Matematicas, Ciencias (Biologia, Fisica, Quimica),
  Historia, Geografia, Formacion Civica y Etica, Artes, Tecnologia, Educacion Fisica, Ingles, Tutorias
- Gestion de personal complejo: subdirector(es), docentes por asignatura, prefectos,
  orientador educativo, trabajador social, administrativos, intendencia
- Control escolar con calificaciones numericas (5-10), boletas trimestrales, kardex,
  certificacion de 3er grado, Formato 911.5
- PEMC, CTE (sesiones intensivas y ordinarias), acompanamiento pedagogico
- Tutorias, orientacion vocacional para 3er grado
- Programa de la Escuela es Nuestra (PLEEN)
- Protocolos: acoso escolar (bullying), proteccion civil, maltrato infantil
- Sociedad de Alumnos (obligatoria Acuerdo 98)
- USICAMM: promocion, admision, reconocimiento
- Elaboracion de horarios complejos (multiples docentes, asignaturas, laboratorios, talleres)
- Lineamientos de control escolar DGAIR vigentes
- SIGED, SAID, estadistica 911.5

Respondes en espanol de Mexico, de forma clara, practica y profesional.
Cuando el director pregunte sobre una obligacion o tarea, proporcionas informacion
precisa basada en la normativa SEP vigente, con ejemplos concretos y formatos listos para usar.
Si no conoces algo con certeza, lo indicas honestamente.
Nunca inventas normatividad — solo citas la real y vigente."""

# =============================================
# BASE DE DATOS SQLite
# =============================================

@contextmanager
def get_db():
    """Context manager para conexiones SQLite thread-safe."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_db():
    """Crea las tablas si no existen."""
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre TEXT DEFAULT '',
                email TEXT DEFAULT '',
                rol TEXT DEFAULT 'usuario',
                suscripcion_activa INTEGER DEFAULT 0,
                stripe_customer_id TEXT DEFAULT '',
                suscripcion_expira TEXT DEFAULT '',
                carpeta_datos TEXT DEFAULT '',
                creado_en TEXT DEFAULT (datetime('now')),
                ultimo_acceso TEXT
            );

            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                fecha TEXT DEFAULT (datetime('now')),
                mensaje TEXT NOT NULL,
                respuesta TEXT,
                funcion TEXT,
                motor TEXT,
                fuentes TEXT DEFAULT '[]',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                creado_en TEXT DEFAULT (datetime('now')),
                expira_en TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS datos_adse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                funcion TEXT NOT NULL,
                tipo_dato TEXT NOT NULL,
                datos TEXT NOT NULL,
                creado_en TEXT DEFAULT (datetime('now')),
                actualizado_en TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS documentos_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                funcion TEXT NOT NULL,
                herramienta TEXT NOT NULL,
                titulo TEXT NOT NULL,
                contenido_encriptado TEXT NOT NULL,
                iv TEXT NOT NULL,
                salt TEXT NOT NULL,
                tamano INTEGER DEFAULT 0,
                creado_en TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );

            CREATE INDEX IF NOT EXISTS idx_conv_usuario ON conversaciones(usuario_id);
            CREATE INDEX IF NOT EXISTS idx_conv_fecha ON conversaciones(fecha);
            CREATE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token);
            CREATE INDEX IF NOT EXISTS idx_datos_adse_usuario ON datos_adse(usuario_id);
            CREATE INDEX IF NOT EXISTS idx_datos_adse_funcion ON datos_adse(funcion);
            CREATE INDEX IF NOT EXISTS idx_docs_usuario ON documentos_usuario(usuario_id);
            CREATE INDEX IF NOT EXISTS idx_docs_funcion ON documentos_usuario(funcion);
        """)
    logger.info("Base de datos ADSE inicializada")


# =============================================
# AUTENTICACIÓN
# =============================================

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def _verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, TypeError):
        salt = os.environ.get("ADSE_SALT", "adse-salt-2026")
        legacy_hash = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
        return legacy_hash == password_hash


inicializar_db()


def _crear_admin_si_no_existe():
    try:
        with get_db() as db:
            existe = db.execute(
                "SELECT id FROM usuarios WHERE username = 'admin'"
            ).fetchone()
            if not existe:
                db.execute(
                    """INSERT INTO usuarios (username, password_hash, nombre, email, rol, suscripcion_activa, suscripcion_expira)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    ("admin", _hash_password("Kimon19731989"), "CHIPOCLE", "superkrne19731989@gmail.com",
                     "admin", 1, "2099-12-31T23:59:59")
                )
                logger.info("Cuenta de administrador creada")
            else:
                db.execute(
                    "UPDATE usuarios SET suscripcion_activa = 1, rol = 'admin', suscripcion_expira = '2099-12-31T23:59:59' WHERE username = 'admin'",
                )
    except Exception as e:
        logger.error(f"Error creando admin: {e}")

_crear_admin_si_no_existe()


def crear_usuario(username: str, password: str, nombre: str = "", email: str = "") -> dict:
    try:
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO usuarios (username, password_hash, nombre, email) VALUES (?, ?, ?, ?)",
                (username.lower().strip(), _hash_password(password), nombre, email)
            )
            usuario_id = cursor.lastrowid
            carpeta = crear_carpeta_usuario(usuario_id, username)
            db.execute(
                "UPDATE usuarios SET carpeta_datos = ? WHERE id = ?",
                (carpeta, usuario_id)
            )
            return {"exito": True, "mensaje": "Usuario creado", "usuario_id": usuario_id}
    except sqlite3.IntegrityError:
        return {"exito": False, "mensaje": "El usuario ya existe"}
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return {"exito": False, "mensaje": str(e)}


def crear_carpeta_usuario(usuario_id: int, username: str = "") -> str:
    carpeta = DATOS_USUARIOS_DIR / f"user_{usuario_id}_{username.lower()}"
    carpeta.mkdir(exist_ok=True)
    (carpeta / "documentos").mkdir(exist_ok=True)
    (carpeta / "reportes").mkdir(exist_ok=True)
    (carpeta / "respaldos").mkdir(exist_ok=True)
    logger.info(f"Carpeta de usuario creada: {carpeta}")
    return str(carpeta)


def autenticar_usuario(username: str, password: str) -> dict:
    with get_db() as db:
        usuario = db.execute(
            "SELECT id, username, nombre, rol, suscripcion_activa, password_hash FROM usuarios WHERE username = ?",
            (username.lower().strip(),)
        ).fetchone()

        if not usuario or not _verificar_password(password, usuario["password_hash"]):
            return {"exito": False, "mensaje": "Usuario o contraseña incorrectos"}

        import secrets
        token = secrets.token_urlsafe(32)
        expira = (datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)).isoformat()

        db.execute(
            "INSERT INTO sesiones (usuario_id, token, expira_en) VALUES (?, ?, ?)",
            (usuario["id"], token, expira)
        )
        db.execute(
            "UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?",
            (datetime.now().isoformat(), usuario["id"])
        )

        return {
            "exito": True,
            "token": token,
            "usuario": {
                "id": usuario["id"],
                "username": usuario["username"],
                "nombre": usuario["nombre"],
                "rol": usuario["rol"],
                "suscripcion_activa": bool(usuario["suscripcion_activa"])
            }
        }


def validar_token(token: str) -> dict | None:
    if not token:
        return None
    with get_db() as db:
        sesion = db.execute(
            """SELECT s.usuario_id, s.expira_en, u.username, u.nombre, u.rol, u.suscripcion_activa
               FROM sesiones s JOIN usuarios u ON s.usuario_id = u.id
               WHERE s.token = ? AND s.activo = 1""",
            (token,)
        ).fetchone()

        if not sesion:
            return None

        if datetime.fromisoformat(sesion["expira_en"]) < datetime.now():
            db.execute("UPDATE sesiones SET activo = 0 WHERE token = ?", (token,))
            return None

        return {
            "id": sesion["usuario_id"],
            "username": sesion["username"],
            "nombre": sesion["nombre"],
            "rol": sesion["rol"],
            "suscripcion_activa": bool(sesion["suscripcion_activa"])
        }


def cerrar_sesion(token: str) -> bool:
    with get_db() as db:
        db.execute("UPDATE sesiones SET activo = 0 WHERE token = ?", (token,))
        return True


# =============================================
# BÚSQUEDA WEB (Tavily)
# =============================================

def buscar_en_internet(consulta: str, max_resultados: int = 5) -> dict:
    if not TAVILY_API_KEY:
        return {"respuesta_directa": "", "resultados": [], "fuentes": [], "exito": False}

    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": consulta,
            "search_depth": "basic",
            "max_results": max_resultados,
            "include_answer": True,
            "include_raw_content": False
        }
        respuesta = requests.post(TAVILY_URL, json=payload, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()

        resultados = []
        fuentes = []
        for r in datos.get("results", []):
            resultados.append({
                "titulo": r.get("title", "Sin titulo"),
                "url": r.get("url", ""),
                "contenido": r.get("content", "")[:500]
            })
            fuentes.append({
                "titulo": r.get("title", ""),
                "url": r.get("url", "")
            })

        return {
            "respuesta_directa": datos.get("answer", ""),
            "resultados": resultados,
            "fuentes": fuentes,
            "exito": True
        }
    except requests.RequestException as e:
        logger.error(f"Error en búsqueda web: {e}")
        return {"respuesta_directa": "", "resultados": [], "fuentes": [], "exito": False}


def necesita_busqueda_web(mensaje: str) -> bool:
    indicadores = [
        "busca", "buscar", "investiga", "que es", "quien es", "cuando",
        "noticias", "actual", "reciente", "ultimo", "nueva", "nuevo",
        "precio", "costo", "donde queda", "como llego", "horario",
        "clima", "tiempo", "resultado", "marcador", "dolar", "tipo de cambio",
        "informacion sobre", "dime sobre", "que paso con", "actualidad",
        "hoy", "ayer", "esta semana", "este mes", "2025", "2026"
    ]
    mensaje_lower = mensaje.lower()
    return any(ind in mensaje_lower for ind in indicadores)


# =============================================
# RAG MEJORADO CON TF-IDF
# =============================================

def _cargar_documentos_rag() -> list:
    documentos = []
    if not os.path.exists(BASE_CONOCIMIENTO):
        return documentos

    for carpeta in CARPETAS_CONOCIMIENTO.values():
        ruta = os.path.join(BASE_CONOCIMIENTO, carpeta)
        if not os.path.exists(ruta):
            continue
        for archivo in os.listdir(ruta):
            if not archivo.endswith('.json'):
                continue
            ruta_arch = os.path.join(ruta, archivo)
            try:
                with open(ruta_arch, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                texto_partes = [datos.get("tema", ""), datos.get("respuesta_directa", "")]
                for fuente in datos.get("fuentes", []):
                    texto_partes.append(fuente.get("titulo", ""))
                    texto_partes.append(fuente.get("contenido", ""))
                texto_completo = " ".join(texto_partes)
                documentos.append({"texto": texto_completo, "datos": datos, "carpeta": carpeta, "archivo": archivo})
            except (json.JSONDecodeError, IOError):
                continue

    return documentos


def inicializar_tfidf():
    global _tfidf_vectorizer, _tfidf_matrix, _tfidf_docs, _tfidf_initialized

    if not TFIDF_DISPONIBLE:
        return

    _tfidf_docs = _cargar_documentos_rag()
    if not _tfidf_docs:
        return

    textos = [doc["texto"] for doc in _tfidf_docs]
    _tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=1, max_df=0.95)
    _tfidf_matrix = _tfidf_vectorizer.fit_transform(textos)
    _tfidf_initialized = True
    logger.info(f"TF-IDF inicializado con {len(_tfidf_docs)} documentos")


def buscar_conocimiento_tfidf(pregunta: str, funcion_id: str = None, max_resultados: int = 3) -> str:
    global _tfidf_initialized

    if not _tfidf_initialized:
        inicializar_tfidf()

    if not _tfidf_initialized or not _tfidf_docs:
        return buscar_conocimiento_keywords(funcion_id, pregunta) if funcion_id else ""

    try:
        query_vec = _tfidf_vectorizer.transform([pregunta])
        scores = cosine_similarity(query_vec, _tfidf_matrix).flatten()

        indices_relevantes = []
        carpeta_funcion = CARPETAS_CONOCIMIENTO.get(funcion_id, "").lower() if funcion_id else None

        for i, score in enumerate(scores):
            if score > 0.05:
                if carpeta_funcion and _tfidf_docs[i]["carpeta"] != carpeta_funcion:
                    score *= 0.5
                indices_relevantes.append((i, score))

        indices_relevantes.sort(key=lambda x: x[1], reverse=True)

        if not indices_relevantes:
            return ""

        ctx = "\nCONOCIMIENTO LOCAL ADSE (RAG):\n"
        for idx, score in indices_relevantes[:max_resultados]:
            d = _tfidf_docs[idx]["datos"]
            ctx += f"Tema: {d.get('tema', '')} (relevancia: {score:.2f})\n"
            if d.get("respuesta_directa"):
                ctx += f"Resumen: {d['respuesta_directa'][:300]}\n"
            for fuente in d.get("fuentes", [])[:2]:
                ctx += f"- {fuente.get('titulo', '')}: {fuente.get('contenido', '')[:200]}\n"

        return ctx

    except Exception as e:
        logger.warning(f"Error en búsqueda TF-IDF: {e}")
        return buscar_conocimiento_keywords(funcion_id, pregunta) if funcion_id else ""


def buscar_conocimiento_keywords(funcion_id: str, pregunta: str, max_resultados: int = 2) -> str:
    if funcion_id not in CARPETAS_CONOCIMIENTO:
        return ""

    carpeta = CARPETAS_CONOCIMIENTO[funcion_id]
    ruta = os.path.join(BASE_CONOCIMIENTO, carpeta)
    if not os.path.exists(ruta):
        return ""

    palabras = [p for p in pregunta.lower().split() if len(p) > 3]
    archivos_rel = []

    for archivo in os.listdir(ruta):
        if not archivo.endswith('.json'):
            continue
        ruta_arch = os.path.join(ruta, archivo)
        try:
            with open(ruta_arch, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            texto = json.dumps(datos, ensure_ascii=False).lower()
            score = sum(1 for p in palabras if p in texto)
            if score > 0:
                archivos_rel.append({"score": score, "datos": datos})
        except (json.JSONDecodeError, IOError):
            continue

    if not archivos_rel:
        return ""

    archivos_rel.sort(key=lambda x: x["score"], reverse=True)
    ctx = "\nCONOCIMIENTO LOCAL ADSE:\n"
    for item in archivos_rel[:max_resultados]:
        d = item["datos"]
        ctx += f"Tema: {d.get('tema', '')}\n"
        if d.get("respuesta_directa"):
            ctx += f"Resumen: {d['respuesta_directa'][:300]}\n"
        for fuente in d.get("fuentes", [])[:2]:
            ctx += f"- {fuente.get('titulo', '')}: {fuente.get('contenido', '')[:200]}\n"
    return ctx


def buscar_conocimiento_local(funcion_id: str, pregunta: str, max_resultados: int = 2) -> str:
    if TFIDF_DISPONIBLE:
        return buscar_conocimiento_tfidf(pregunta, funcion_id, max_resultados)
    return buscar_conocimiento_keywords(funcion_id, pregunta, max_resultados)


# =============================================
# MEMORIA (SQLite)
# =============================================

def cargar_memoria(usuario_id: int = None) -> dict:
    try:
        with get_db() as db:
            if usuario_id:
                rows = db.execute(
                    "SELECT fecha, mensaje, respuesta, funcion, fuentes FROM conversaciones WHERE usuario_id = ? ORDER BY id DESC LIMIT 50",
                    (usuario_id,)
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT fecha, mensaje, respuesta, funcion, fuentes FROM conversaciones ORDER BY id DESC LIMIT 50"
                ).fetchall()

            conversaciones = []
            for row in reversed(rows):
                conversaciones.append({
                    "fecha": row["fecha"],
                    "mensaje": row["mensaje"],
                    "respuesta": row["respuesta"] or "",
                    "funcion": row["funcion"] or "GENERAL",
                    "fuentes": json.loads(row["fuentes"]) if row["fuentes"] else []
                })
            return {"conversaciones": conversaciones}
    except Exception as e:
        logger.warning(f"Error cargando memoria: {e}")
        return {"conversaciones": []}


def agregar_a_memoria(mensaje: str, respuesta: str, funcion: str,
                      fuentes: list = None, usuario_id: int = None) -> None:
    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO conversaciones (usuario_id, mensaje, respuesta, funcion, fuentes) VALUES (?, ?, ?, ?, ?)",
                (usuario_id, mensaje[:500], (respuesta or "")[:2000], funcion,
                 json.dumps(fuentes or []))
            )
    except Exception as e:
        logger.error(f"Error guardando en memoria: {e}")


def obtener_contexto_reciente(n: int = 3, usuario_id: int = None) -> str:
    try:
        with get_db() as db:
            if usuario_id:
                rows = db.execute(
                    "SELECT mensaje, respuesta, funcion FROM conversaciones WHERE usuario_id = ? ORDER BY id DESC LIMIT ?",
                    (usuario_id, n)
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT mensaje, respuesta, funcion FROM conversaciones ORDER BY id DESC LIMIT ?",
                    (n,)
                ).fetchall()

            if not rows:
                return ""

            contexto = "CONVERSACIONES RECIENTES:\n"
            for row in reversed(rows):
                contexto += f"- Usuario: {row['mensaje']}\n"
                contexto += f"  Función ({row['funcion']}): {(row['respuesta'] or '')[:100]}...\n"
            return contexto
    except Exception as e:
        logger.warning(f"Error obteniendo contexto: {e}")
        return ""


def obtener_historial(usuario_id: int = None, limite: int = 20) -> list:
    try:
        with get_db() as db:
            if usuario_id:
                rows = db.execute(
                    "SELECT fecha, mensaje, respuesta, funcion, fuentes FROM conversaciones WHERE usuario_id = ? ORDER BY id DESC LIMIT ?",
                    (usuario_id, limite)
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT fecha, mensaje, respuesta, funcion, fuentes FROM conversaciones ORDER BY id DESC LIMIT ?",
                    (limite,)
                ).fetchall()

            return [
                {
                    "fecha": row["fecha"],
                    "mensaje": row["mensaje"],
                    "respuesta": row["respuesta"],
                    "funcion": row["funcion"],
                    "fuentes": json.loads(row["fuentes"]) if row["fuentes"] else []
                }
                for row in rows
            ]
    except Exception as e:
        logger.warning(f"Error obteniendo historial: {e}")
        return []


# =============================================
# CLASIFICACIÓN DE FUNCIONES (Híbrido)
# =============================================

CLASIFICACION_UMBRAL_LLM = 8

def clasificar_funcion_keywords(mensaje: str) -> tuple:
    mensaje_lower = mensaje.lower()
    mejor_funcion = None
    mejor_score = 0

    for id_funcion, funcion in AGENTES_ADSE.items():
        score = 0
        for palabra in funcion["palabras_clave"]:
            if palabra in mensaje_lower:
                bonus = 1.5 if " " in palabra else 1.0
                score += len(palabra) * bonus
        if score > mejor_score:
            mejor_score = score
            mejor_funcion = id_funcion

    return mejor_funcion or "O1A", int(mejor_score)


def clasificar_funcion_llm(mensaje: str) -> str:
    if not CLAUDE_DISPONIBLE:
        return "O1A"

    funciones_desc = "\n".join([
        f"- {k}: {v['nombre']} — {v['descripcion']}"
        for k, v in AGENTES_ADSE.items()
    ])

    prompt_clasificacion = f"""Clasifica el siguiente mensaje del usuario a la funcion ADSE mas apropiada.
Responde SOLO con el ID de la funcion (O1A-O7F).

FUNCIONES DISPONIBLES:
{funciones_desc}

MENSAJE: {mensaje}

FUNCION:"""

    try:
        respuesta = preguntar_gpt(prompt_clasificacion)
        if respuesta:
            funcion_id = respuesta.strip().upper().split()[0]
            if funcion_id in AGENTES_ADSE:
                return funcion_id
    except Exception as e:
        logger.warning(f"Error en clasificación con Claude: {e}")

    return "O1A"


def clasificar_funcion(mensaje: str) -> str:
    funcion, score = clasificar_funcion_keywords(mensaje)

    if score >= CLASIFICACION_UMBRAL_LLM:
        return funcion

    if score > 0:
        return clasificar_funcion_llm(mensaje)
    else:
        return clasificar_funcion_llm(mensaje)


clasificar_agente = clasificar_funcion
clasificar_obligacion = clasificar_funcion


# =============================================
# ANTHROPIC CLAUDE
# =============================================

def preguntar_gpt(prompt: str, sistema: str = None) -> str:
    if not CLAUDE_DISPONIBLE or not cliente_anthropic:
        return "Error: Anthropic API no configurada"
    try:
        kwargs = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }
        if sistema:
            kwargs["system"] = sistema

        respuesta = cliente_anthropic.messages.create(**kwargs)
        return respuesta.content[0].text if respuesta.content else "Sin respuesta"
    except Exception as e:
        logger.error(f"Error con Claude: {e}")
        return f"Error al generar respuesta: {str(e)}"


def preguntar_modelo(prompt: str, sistema: str = None) -> tuple:
    if CLAUDE_DISPONIBLE:
        respuesta = preguntar_gpt(prompt, sistema=sistema)
        return respuesta, "Claude-Haiku"

    logger.error("Claude no está disponible")
    return "Error: Anthropic API no configurada", "ninguno"


# =============================================
# DATOS ADSE
# =============================================

def guardar_dato_adse(usuario_id: int, funcion: str, tipo_dato=None, datos: dict = None) -> bool:
    if tipo_dato is not None and not isinstance(tipo_dato, str):
        datos = tipo_dato
        tipo_dato = None

    if datos is None and isinstance(tipo_dato, dict):
        datos = tipo_dato
        tipo_dato = None

    if datos is None:
        datos = {}

    tipo_dato = tipo_dato or "datos"

    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO datos_adse (usuario_id, funcion, tipo_dato, datos) VALUES (?, ?, ?, ?)",
                (usuario_id, funcion, tipo_dato, json.dumps(datos))
            )
        return True
    except Exception as e:
        logger.error(f"Error guardando dato ADSE: {e}")
        return False

guardar_dato_adke = guardar_dato_adse


def obtener_datos_adse(usuario_id: int, funcion: str = None) -> list:
    try:
        with get_db() as db:
            if funcion:
                rows = db.execute(
                    "SELECT funcion, tipo_dato, datos, creado_en FROM datos_adse WHERE usuario_id = ? AND funcion = ? ORDER BY creado_en DESC",
                    (usuario_id, funcion)
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT funcion, tipo_dato, datos, creado_en FROM datos_adse WHERE usuario_id = ? ORDER BY creado_en DESC",
                    (usuario_id,)
                ).fetchall()

            return [
                {
                    "funcion": row["funcion"],
                    "tipo_dato": row["tipo_dato"],
                    "datos": json.loads(row["datos"]),
                    "creado_en": row["creado_en"]
                }
                for row in rows
            ]
    except Exception as e:
        logger.warning(f"Error obteniendo datos ADSE: {e}")
        return []

obtener_datos_adke = obtener_datos_adse


def verificar_suscripcion(usuario_id: int) -> dict:
    try:
        with get_db() as db:
            usuario = db.execute(
                "SELECT suscripcion_activa, suscripcion_expira, stripe_customer_id, rol FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            if not usuario:
                return {"activa": False, "mensaje": "Usuario no encontrado"}

            if usuario["rol"] == "admin":
                return {"activa": True, "expira": "2099-12-31", "stripe_customer_id": "", "mensaje": "Administrador"}

            activa = bool(usuario["suscripcion_activa"])
            expira = usuario["suscripcion_expira"] or ""

            if activa and expira:
                if datetime.fromisoformat(expira) < datetime.now():
                    db.execute("UPDATE usuarios SET suscripcion_activa = 0 WHERE id = ?", (usuario_id,))
                    return {"activa": False, "mensaje": "Suscripción expirada", "expira": expira}

            return {
                "activa": activa,
                "expira": expira,
                "stripe_customer_id": usuario["stripe_customer_id"] or "",
                "mensaje": "Suscripción activa" if activa else "Sin suscripción"
            }
    except Exception as e:
        logger.error(f"Error verificando suscripción: {e}")
        return {"activa": False, "mensaje": str(e)}


# =============================================
# UTILIDADES
# =============================================

def formatear_fuentes(fuentes: list) -> str:
    if not fuentes:
        return ""
    texto = "\n📋 FUENTES:\n"
    for i, fuente in enumerate(fuentes, 1):
        titulo = fuente.get("titulo", "Sin titulo")
        url = fuente.get("url", "")
        texto += f"  [{i}] {titulo}\n      🔗 {url}\n"
    return texto


def leer_archivo(ruta: str) -> dict:
    try:
        if not os.path.exists(ruta):
            return {"contenido": "", "exito": False, "error": "Archivo no encontrado"}

        extension = os.path.splitext(ruta)[1].lower()
        extensiones_validas = ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv', '.log']

        if extension not in extensiones_validas:
            return {"contenido": "", "exito": False, "error": f"Tipo no soportado: {extension}"}

        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()
        return {"contenido": contenido, "exito": True, "tipo": "texto"}
    except IOError as e:
        return {"contenido": "", "exito": False, "error": str(e)}


def detectar_archivo(mensaje: str) -> str | None:
    patron = r'[A-Za-z]:\\[^\s]+\.\w+'
    rutas = re.findall(patron, mensaje)
    return rutas[0] if rutas else None


def obtener_info_sistema() -> dict:
    return {
        "nombre": "Agente Director Secundaria Educación",
        "version": "1.0.0",
        "funciones_disponibles": len(AGENTES_ADSE),
        "claude_disponible": CLAUDE_DISPONIBLE,
        "gpt_disponible": CLAUDE_DISPONIBLE,
        "tavily_disponible": bool(TAVILY_API_KEY),
        "tfidf_disponible": TFIDF_DISPONIBLE,
        "db_inicializada": os.path.exists(DB_PATH),
        "timestamp": datetime.now().isoformat()
    }
