from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegistroRequest, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroRequest, db: Session = Depends(get_db)):
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
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if not usuario or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token(data={"sub": str(usuario.id)})
    return TokenResponse(access_token=token)