import os
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.tarea import (
    AudioProcesamientoResponse,
    BusquedaResponse,
    TareaCreate,
    TareaResponse,
    TareaUpdate,
)
from app.services import tarea_service

router = APIRouter(prefix="/tareas", tags=["tareas"])
limiter = Limiter(key_func=get_remote_address)

_T = os.getenv("TESTING") == "1"


@router.get("/", response_model=List[TareaResponse])
def listar_tareas(
    lista_id: Optional[int] = None,
    completada: Optional[bool] = None,
    importante: Optional[bool] = None,
    prioridad: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    hay_filtros = any(p is not None for p in [completada, importante, prioridad])
    if hay_filtros or lista_id is not None:
        return tarea_service.filtrar_tareas(
            db, usuario.id,
            lista_id=lista_id,
            completada=completada,
            importante=importante,
            prioridad=prioridad,
        )
    return tarea_service.get_tareas_usuario(db, usuario.id, lista_id)


@router.get("/importantes", response_model=List[TareaResponse])
def listar_importantes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return tarea_service.get_tareas_importantes(db, usuario.id)


@router.get("/buscar", response_model=BusquedaResponse)
def buscar(
    q: str = Query(..., min_length=1, max_length=200),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tareas = tarea_service.buscar_tareas(db, usuario.id, q)
    return BusquedaResponse(total=len(tareas), tareas=tareas)


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


@router.patch("/{tarea_id}", response_model=TareaResponse)
def editar_tarea(
    tarea_id: int,
    datos: TareaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tarea = tarea_service.get_tarea(db, tarea_id, usuario.id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea_service.editar_tarea(db, tarea, datos)


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


@router.put("/{tarea_id}/importante", response_model=TareaResponse)
def marcar_importante(
    tarea_id: int,
    importante: bool = Query(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    tarea = tarea_service.get_tarea(db, tarea_id, usuario.id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea_service.marcar_importante(db, tarea, importante)


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


@router.post("/audio", response_model=AudioProcesamientoResponse)
@limiter.limit("10000/minute" if _T else "10/minute")
async def procesar_audio(
    request: Request,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    try:
        return await tarea_service.procesar_audio(db, audio, usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirmar", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def confirmar_tarea_audio(
    datos: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return tarea_service.crear_tarea_desde_audio_datos(db, datos, usuario.id)