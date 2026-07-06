import json
import re
from datetime import datetime

from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)
MODELO = settings.GROQ_MODEL

PRIORIDADES_VALIDAS = {"BAJA", "MEDIA", "ALTA"}

SYSTEM_PROMPT = """Eres un asistente que convierte texto transcrito en tareas estructuradas.

Devuelve EXCLUSIVAMENTE un JSON válido con estos campos:
- titulo: string, máximo 10 palabras
- descripcion: string, descripción clara de la tarea
- fecha_limite: string en formato YYYY-MM-DD o null si no se menciona fecha
- prioridad: "BAJA", "MEDIA" o "ALTA"

No añadas explicaciones, markdown ni texto fuera del JSON.

Ejemplo de salida:
{"titulo": "Comprar pintura y llamar a Juan", "descripcion": "Comprar pintura el viernes y contactar a Juan para coordinar", "fecha_limite": "2026-07-03", "prioridad": "MEDIA"}"""


def _limpiar_json(contenido: str) -> str:
    """Extrae el bloque JSON del contenido crudo del LLM."""
    contenido = contenido.strip()
    # Eliminar bloques <think>
    contenido = re.sub(r"<think>.*?</think>", "", contenido, flags=re.DOTALL).strip()
    # Eliminar fences de markdown
    if contenido.startswith("```"):
        contenido = re.sub(r"^```(?:json)?\s*", "", contenido)
        contenido = re.sub(r"\s*```$", "", contenido).strip()
    # Extraer primer objeto JSON
    match = re.search(r"\{.*\}", contenido, re.DOTALL)
    if match:
        return match.group(0)
    return contenido


def _validar_prioridad(valor: str) -> str:
    """Normaliza y valida el campo prioridad."""
    if not valor:
        return "MEDIA"
    normalizado = str(valor).upper().strip()
    return normalizado if normalizado in PRIORIDADES_VALIDAS else "MEDIA"


def _validar_fecha(valor) -> str | None:
    """Valida que la fecha tenga formato YYYY-MM-DD y no sea pasada."""
    if not valor or str(valor).lower() in ("null", "none", ""):
        return None
    try:
        fecha = datetime.strptime(str(valor), "%Y-%m-%d")
        # Rechazar fechas claramente erróneas (año fuera de rango razonable)
        if fecha.year < 2020 or fecha.year > 2100:
            return None
        return str(valor)
    except ValueError:
        return None


def _titulo_fallback(titulo: str, transcripcion: str) -> str:
    """Si el título está vacío, genera uno a partir de la transcripción."""
    titulo = (titulo or "").strip()
    if titulo:
        return titulo[:255]
    # Tomar las primeras 10 palabras de la transcripción como fallback
    palabras = transcripcion.strip().split()
    return " ".join(palabras[:10]) or "Tarea sin título"


def procesar_transcripcion(texto: str) -> dict:
    respuesta = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Convierte esta nota de voz en una tarea: {texto}"},
        ],
        temperature=0.3,
        reasoning_effort="none",
    )

    contenido = respuesta.choices[0].message.content or ""
    contenido_limpio = _limpiar_json(contenido)

    if not contenido_limpio:
        raise ValueError("El modelo no devolvió contenido válido")

    try:
        datos = json.loads(contenido_limpio)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido del LLM: {e} | Contenido: {contenido_limpio[:200]}")

    if not isinstance(datos, dict):
        raise ValueError(f"Se esperaba un objeto JSON, se obtuvo: {type(datos)}")

    return {
        "titulo": _titulo_fallback(datos.get("titulo", ""), texto),
        "descripcion": (datos.get("descripcion") or "").strip()[:2000],
        "fecha_limite": _validar_fecha(datos.get("fecha_limite")),
        "prioridad": _validar_prioridad(datos.get("prioridad")),
    }