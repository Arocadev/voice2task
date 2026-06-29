from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.tarea import Prioridad, Origen


class TareaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    prioridad: Prioridad = Prioridad.MEDIA


class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    prioridad: Optional[Prioridad] = None


class TareaResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]
    fecha_limite: Optional[datetime]
    prioridad: Prioridad
    completada: bool
    fecha_completada: Optional[datetime]
    origen: Origen
    audio_transcripcion: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AudioProcesamientoResponse(BaseModel):
    titulo: str
    descripcion: str
    fecha_limite: Optional[datetime]
    prioridad: Prioridad
    audio_transcripcion: str