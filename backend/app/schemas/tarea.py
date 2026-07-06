from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.models.tarea import Origen, Prioridad


# ── Crear ──────────────────────────────────────────────────────────────────────

class TareaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    prioridad: Prioridad = Prioridad.MEDIA
    lista_id: Optional[int] = None

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El título no puede estar vacío")
        if len(v) > 255:
            raise ValueError("El título no puede superar 255 caracteres")
        return v

    @field_validator("descripcion")
    @classmethod
    def descripcion_longitud(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("La descripción no puede superar 2000 caracteres")
        return v


# ── Editar ─────────────────────────────────────────────────────────────────────

class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    prioridad: Optional[Prioridad] = None
    lista_id: Optional[int] = None
    importante: Optional[bool] = None

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El título no puede estar vacío")
            if len(v) > 255:
                raise ValueError("El título no puede superar 255 caracteres")
        return v

    @field_validator("descripcion")
    @classmethod
    def descripcion_longitud(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("La descripción no puede superar 2000 caracteres")
        return v


# ── Respuesta ──────────────────────────────────────────────────────────────────

class TareaResponse(BaseModel):
    id: int
    lista_id: Optional[int]
    titulo: str
    descripcion: Optional[str]
    fecha_limite: Optional[datetime]
    prioridad: Prioridad
    completada: bool
    importante: bool
    fecha_completada: Optional[datetime]
    origen: Origen
    audio_transcripcion: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Audio ──────────────────────────────────────────────────────────────────────

class AudioProcesamientoResponse(BaseModel):
    titulo: str
    descripcion: str
    fecha_limite: Optional[datetime]
    prioridad: Prioridad
    audio_transcripcion: str


# ── Búsqueda ───────────────────────────────────────────────────────────────────

class BusquedaResponse(BaseModel):
    total: int
    tareas: List[TareaResponse]