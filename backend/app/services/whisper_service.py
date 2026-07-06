from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def transcribir_audio(ruta_audio: str) -> str:
    with open(ruta_audio, "rb") as archivo:
        transcripcion = client.audio.transcriptions.create(
            file=archivo,
            model="whisper-large-v3-turbo",
            language="es",
            response_format="text",
        )
    return transcripcion.strip() if isinstance(transcripcion, str) else transcripcion.text.strip()