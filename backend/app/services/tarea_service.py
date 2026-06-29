import os
import tempfile
from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.tarea import EstadoProcesamiento, Origen, ProcesamientoAudio, Tarea
from app.schemas.tarea import AudioProcesamientoResponse, TareaCreate
from app.services import llm_service, whisper_service


def get_tareas_usuario(db: Session, usuario_id: int) -> List[Tarea]:
    return db.query(Tarea).filter(Tarea.usuario_id == usuario_id).order_by(Tarea.created_at.desc()).all()


def get_tarea(db: Session, tarea_id: int, usuario_id: int) -> Optional[Tarea]:
    return db.query(Tarea).filter(Tarea.id == tarea_id, Tarea.usuario_id == usuario_id).first()


def crear_tarea(db: Session, datos: TareaCreate, usuario_id: int) -> Tarea:
    tarea = Tarea(
        usuario_id=usuario_id,
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


def crear_tarea_desde_audio_datos(db: Session, datos: dict, usuario_id: int) -> Tarea:
    fecha_limite = None
    if datos.get("fecha_limite"):
        try:
            fecha_limite = datetime.strptime(datos["fecha_limite"], "%Y-%m-%d")
        except ValueError:
            pass

    tarea = Tarea(
        usuario_id=usuario_id,
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


async def procesar_audio(db: Session, audio: UploadFile, usuario_id: int) -> AudioProcesamientoResponse:
    procesamiento = ProcesamientoAudio(
        usuario_id=usuario_id,
        estado=EstadoProcesamiento.PROCESANDO,
    )
    db.add(procesamiento)
    db.commit()

    try:
        sufijo = os.path.splitext(audio.filename)[1] if audio.filename else ".ogg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
            contenido = await audio.read()
            tmp.write(contenido)
            ruta_tmp = tmp.name

        transcripcion = whisper_service.transcribir_audio(ruta_tmp)
        os.unlink(ruta_tmp)

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


def completar_tarea(db: Session, tarea: Tarea) -> Tarea:
    tarea.completada = True
    tarea.fecha_completada = datetime.utcnow()
    db.commit()
    db.refresh(tarea)
    return tarea


def eliminar_tarea(db: Session, tarea: Tarea) -> None:
    db.delete(tarea)
    db.commit()