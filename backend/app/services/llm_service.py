import json
import re

from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)
MODELO = settings.GROQ_MODEL

SYSTEM_PROMPT = """Eres un asistente que convierte texto transcrito en tareas estructuradas.

Devuelve EXCLUSIVAMENTE un JSON válido con estos campos:
- titulo: string, máximo 10 palabras
- descripcion: string, descripción clara de la tarea
- fecha_limite: string en formato YYYY-MM-DD o null si no se menciona fecha
- prioridad: "BAJA", "MEDIA" o "ALTA"

No añadas explicaciones, markdown ni texto fuera del JSON.

Ejemplo de salida:
{"titulo": "Comprar pintura y llamar a Juan", "descripcion": "Comprar pintura el viernes y contactar a Juan para coordinar", "fecha_limite": "2026-07-03", "prioridad": "MEDIA"}"""


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
    contenido = contenido.strip()

    contenido = re.sub(r"<think>.*?</think>", "", contenido, flags=re.DOTALL).strip()

    if contenido.startswith("```"):
        contenido = re.sub(r"^```(?:json)?\s*", "", contenido)
        contenido = re.sub(r"\s*```$", "", contenido).strip()

    match = re.search(r"\{.*\}", contenido, re.DOTALL)
    if match:
        contenido = match.group(0)

    if not contenido:
        raise ValueError("El modelo no devolvió contenido válido")

    datos = json.loads(contenido)

    return {
        "titulo": datos.get("titulo", ""),
        "descripcion": datos.get("descripcion", ""),
        "fecha_limite": datos.get("fecha_limite"),
        "prioridad": datos.get("prioridad", "MEDIA"),
    }