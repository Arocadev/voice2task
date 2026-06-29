import whisper

from app.core.config import settings

_model = None


def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model


def transcribir_audio(ruta_audio: str) -> str:
    model = get_model()
    resultado = model.transcribe(ruta_audio)
    return resultado["text"].strip()