import re
from typing import Optional

from pydantic import BaseModel, field_validator

# Colores hex válidos: #RGB o #RRGGBB
_HEX_COLOR_RE = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


class ListaCreate(BaseModel):
    nombre: str
    color: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        if len(v) > 100:
            raise ValueError("El nombre no puede superar 100 caracteres")
        return v

    @field_validator("color")
    @classmethod
    def color_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not _HEX_COLOR_RE.match(v):
            raise ValueError("El color debe ser un valor hexadecimal válido (ej: #7c3aed)")
        return v


class ListaUpdate(BaseModel):
    nombre: Optional[str] = None
    color: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío")
            if len(v) > 100:
                raise ValueError("El nombre no puede superar 100 caracteres")
        return v

    @field_validator("color")
    @classmethod
    def color_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not re.match(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$", v):
            raise ValueError("El color debe ser un valor hexadecimal válido (ej: #7c3aed)")
        return v


class ListaResponse(BaseModel):
    id: int
    nombre: str
    color: Optional[str]

    class Config:
        from_attributes = True