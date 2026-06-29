from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ListaCreate(BaseModel):
    nombre: str
    color: Optional[str] = None


class ListaUpdate(BaseModel):
    nombre: Optional[str] = None
    color: Optional[str] = None


class ListaResponse(BaseModel):
    id: int
    nombre: str
    color: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True