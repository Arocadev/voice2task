from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
import enum

from app.db.database import Base


class Prioridad(str, enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class Origen(str, enum.Enum):
    MANUAL = "MANUAL"
    AUDIO = "AUDIO"


class EstadoProcesamiento(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_limite = Column(DateTime, nullable=True)
    prioridad = Column(Enum(Prioridad), default=Prioridad.MEDIA)
    completada = Column(Boolean, default=False)
    fecha_completada = Column(DateTime, nullable=True)
    origen = Column(Enum(Origen), default=Origen.MANUAL)
    audio_transcripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProcesamientoAudio(Base):
    __tablename__ = "procesamientos_audio"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    transcripcion = Column(Text, nullable=True)
    estado = Column(Enum(EstadoProcesamiento), default=EstadoProcesamiento.PENDIENTE)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)