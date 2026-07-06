import re

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


class RegistroRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        if len(v) > 50:
            raise ValueError("El username no puede superar 50 caracteres")
        if not _USERNAME_RE.match(v):
            raise ValueError("El username solo puede contener letras, números, guiones y guiones bajos")
        return v

    @field_validator("email")
    @classmethod
    def email_longitud(cls, v: str) -> str:
        if len(v) > 255:
            raise ValueError("El email no puede superar 255 caracteres")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def password_seguro(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if len(v) > 128:
            raise ValueError("La contraseña no puede superar 128 caracteres")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_longitud(cls, v: str) -> str:
        if len(v) > 255:
            raise ValueError("El email no puede superar 255 caracteres")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def password_longitud(cls, v: str) -> str:
        if len(v) > 128:
            raise ValueError("Credenciales incorrectas")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str