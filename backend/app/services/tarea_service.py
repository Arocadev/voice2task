import os
import tempfile
from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.tarea import EstadoProcesamiento, Origen, ProcesamientoAudio, Tarea
from app.schemas.tarea import AudioProcesamientoResponse, TareaCreate, TareaUpdate
from app.services import llm_service, whisper_service

# Extensiones de audio permitidas
EXTENSIONES_PERMITIDAS = {".ogg", ".wav", ".mp3", ".mp4", ".m4a", ".webm", ".flac"}
MIME_TIPOS_PERMITIDOS = {
    "audio/ogg",
    "audio/wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/webm",
    "audio/flac",
    "audio/x-m4a",
    "audio/m4a",
}
TAMANO_MAXIMO = 25 * 1024 * 1024  # 25 MB


# ── Helpers ────────────────────────────────────────────────────────────────────

def _verificar_audio(audio: UploadFile, contenido: bytes) -> None:
    """Valida extensión, mime type y tamaño del archivo de audio."""
    # Extensión
    nombre = audio.filename or ""
    ext = os.path.splitext(nombre)[1].lower()
    if ext and ext not in EXTENSIONES_PERMITIDAS:
        raise ValueError(f"Extensión no permitida: {ext}. Usa: {', '.join(EXTENSIONES_PERMITIDAS)}")

    # MIME type
    if audio.content_type and audio.content_type not in MIME_TIPOS_PERMITIDOS:
        raise ValueError(f"Tipo de audio no soportado: {audio.content_type}")

    # Tamaño
    if len(contenido) > TAMANO_MAXIMO:
        raise ValueError("El audio no puede superar 25 MB")

    # Archivo vacío
    if len(contenido) == 0:
        raise ValueError("El archivo de audio está vacío")


# ── Consultas ──────────────────────────────────────────────────────────────────

def get_tareas_usuario(db: Session, usuario_id: int, lista_id: Optional[int] = None) -> List[Tarea]:
    query = db.query(Tarea).filter(Tarea.usuario_id == usuario_id)
    if lista_id is not None:
        query = query.filter(Tarea.lista_id == lista_id)
    return query.order_by(Tarea.created_at.desc()).all()


def get_tarea(db: Session, tarea_id: int, usuario_id: int) -> Optional[Tarea]:
    return db.query(Tarea).filter(Tarea.id == tarea_id, Tarea.usuario_id == usuario_id).first()


def buscar_tareas(db: Session, usuario_id: int, q: str) -> List[Tarea]:
    """Búsqueda por texto en título y descripción (case-insensitive)."""
    termino = f"%{q.strip()}%"
    return (
        db.query(Tarea)
        .filter(
            Tarea.usuario_id == usuario_id,
            or_(
                Tarea.titulo.ilike(termino),
                Tarea.descripcion.ilike(termino),
            ),
        )
        .order_by(Tarea.created_at.desc())
        .all()
    )


def filtrar_tareas(
    db: Session,
    usuario_id: int,
    lista_id: Optional[int] = None,
    completada: Optional[bool] = None,
    importante: Optional[bool] = None,
    prioridad: Optional[str] = None,
) -> List[Tarea]:
    """Filtra tareas por cualquier combinación de criterios."""
    query = db.query(Tarea).filter(Tarea.usuario_id == usuario_id)

    if lista_id is not None:
        query = query.filter(Tarea.lista_id == lista_id)
    if completada is not None:
        query = query.filter(Tarea.completada == completada)
    if importante is not None:
        query = query.filter(Tarea.importante == importante)
    if prioridad is not None:
        query = query.filter(Tarea.prioridad == prioridad)

    return query.order_by(Tarea.created_at.desc()).all()


def get_tareas_importantes(db: Session, usuario_id: int) -> List[Tarea]:
    return (
        db.query(Tarea)
        .filter(Tarea.usuario_id == usuario_id, Tarea.importante == True)
        .order_by(Tarea.created_at.desc())
        .all()
    )


# ── Mutaciones ─────────────────────────────────────────────────────────────────

def crear_tarea(db: Session, datos: TareaCreate, usuario_id: int) -> Tarea:
    tarea = Tarea(
        usuario_id=usuario_id,
        lista_id=datos.lista_id,
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        fecha_limite=datos.fecha_limite,
        prioridad=datos.prioridad,
        origen=Origen.MANUAL,
    )
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


def editar_tarea(db: Session, tarea: Tarea, datos: TareaUpdate) -> Tarea:
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(tarea, campo, valor)
    tarea.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tarea)
    return tarea


def marcar_importante(db: Session, tarea: Tarea, importante: bool) -> Tarea:
    tarea.importante = importante
    tarea.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tarea)
    return tarea


def completar_tarea(db: Session, tarea: Tarea) -> Tarea:
    tarea.completada = True
    tarea.fecha_completada = datetime.utcnow()
    db.commit()
    db.refresh(tarea)
    return tarea


def eliminar_tarea(db: Session, tarea: Tarea) -> None:
    db.delete(tarea)
    db.commit()


def crear_tarea_desde_audio_datos(db: Session, datos: dict, usuario_id: int) -> Tarea:
    fecha_limite = None
    if datos.get("fecha_limite"):
        try:
            fecha_limite = datetime.strptime(datos["fecha_limite"], "%Y-%m-%d")
        except ValueError:
            pass

    tarea = Tarea(
        usuario_id=usuario_id,
        lista_id=datos.get("lista_id"),
        titulo=datos["titulo"],
        descripcion=datos["descripcion"],
        fecha_limite=fecha_limite,
        prioridad=datos["prioridad"],
        origen=Origen.AUDIO,
        audio_transcripcion=datos.get("audio_transcripcion"),
    )
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


# ── Audio ──────────────────────────────────────────────────────────────────────

async def procesar_audio(db: Session, audio: UploadFile, usuario_id: int) -> AudioProcesamientoResponse:
    procesamiento = ProcesamientoAudio(
        usuario_id=usuario_id,
        estado=EstadoProcesamiento.PROCESANDO,
    )
    db.add(procesamiento)
    db.commit()

    ruta_tmp = None
    try:
        contenido = await audio.read()
        _verificar_audio(audio, contenido)

        sufijo = os.path.splitext(audio.filename or "")[1] or ".ogg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
            tmp.write(contenido)
            ruta_tmp = tmp.name

        transcripcion = whisper_service.transcribir_audio(ruta_tmp)
        datos_tarea = llm_service.procesar_transcripcion(transcripcion)

        procesamiento.transcripcion = transcripcion
        procesamiento.estado = EstadoProcesamiento.COMPLETADO
        db.commit()

        return AudioProcesamientoResponse(
            titulo=datos_tarea["titulo"],
            descripcion=datos_tarea["descripcion"],
            fecha_limite=datos_tarea.get("fecha_limite"),
            prioridad=datos_tarea["prioridad"],
            audio_transcripcion=transcripcion,
        )

    except Exception as e:
        procesamiento.estado = EstadoProcesamiento.ERROR
        procesamiento.error = str(e)
        db.commit()
        raise

    finally:
        # Siempre limpia el temporal, aunque haya error
        if ruta_tmp and os.path.exists(ruta_tmp):
            os.unlink(ruta_tmp)