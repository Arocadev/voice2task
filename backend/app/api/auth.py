import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.blacklist import blacklist_token
from app.core.deps import get_current_user
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegistroRequest, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)
bearer_scheme = HTTPBearer()

_T = os.getenv("TESTING") == "1"


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def password_segura(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if len(v) > 128:
            raise ValueError("La contraseña no puede superar 128 caracteres")
        return v


@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10000/minute" if _T else "5/minute")
def registro(request: Request, datos: RegistroRequest, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if db.query(Usuario).filter(Usuario.username == datos.username).first():
        raise HTTPException(status_code=400, detail="El username ya está en uso")

    usuario = Usuario(
        username=datos.username,
        email=datos.email,
        password_hash=hash_password(datos.password),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10000/minute" if _T else "10/minute")
def login(request: Request, datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if not usuario or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token(data={"sub": str(usuario.id)})
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10000/minute" if _T else "20/minute")
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: Usuario = Depends(get_current_user),
):
    token = credentials.credentials
    payload = decode_token(token)
    if payload:
        jti = payload.get("jti")
        exp = payload.get("exp", 0)
        if jti:
            blacklist_token(jti, exp)


@router.get("/me", response_model=UsuarioResponse)
@limiter.limit("10000/minute" if _T else "30/minute")
def me(request: Request, usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.put("/cambiar-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10000/minute" if _T else "5/minute")
def cambiar_password(
    request: Request,
    datos: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if not verify_password(datos.password_actual, usuario.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    usuario.password_hash = hash_password(datos.password_nueva)
    db.commit()