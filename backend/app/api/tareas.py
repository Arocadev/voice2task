from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.tarea import AudioProcesamientoResponse, TareaCreate, TareaResponse
from app.services import tarea_service

router = APIRouter(prefix="/tareas", tags=["tareas"])


@router.get("/", response_model=List[TareaResponse])
def listar_tareas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return tarea_service.get_tareas_usuario(db, usuario.id)


@router.get("/{tarea_id}", response_model=TareaResponse)
def detalle_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tarea = tarea_service.get_tarea(db, tarea_id, usuario.id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return tarea_service.crear_tarea(db, datos, usuario.id)


@router.post("/audio", response_model=AudioProcesamientoResponse)
async def procesar_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tipos_permitidos = {"audio/ogg", "audio/wav", "audio/mpeg", "audio/mp4", "audio/webm"}
    if audio.content_type not in tipos_permitidos:
        raise HTTPException(status_code=400, detail="Formato de audio no soportado")

    contenido = await audio.read()
    if len(contenido) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El audio no puede superar 25MB")
    await audio.seek(0)

    return await tarea_service.procesar_audio(db, audio, usuario.id)


@router.post("/confirmar", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def confirmar_tarea_audio(
    datos: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return tarea_service.crear_tarea_desde_audio_datos(db, datos, usuario.id)


@router.put("/{tarea_id}/completar", response_model=TareaResponse)
def completar_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tarea = tarea_service.get_tarea(db, tarea_id, usuario.id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea_service.completar_tarea(db, tarea)


@router.delete("/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tarea = tarea_service.get_tarea(db, tarea_id, usuario.id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea_service.eliminar_tarea(db, tarea)