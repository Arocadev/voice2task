from pydantic import BaseModel, EmailStr


class RegistroRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True