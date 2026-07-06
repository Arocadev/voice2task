from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.lista import Lista
from app.models.tarea import Tarea
from app.models.usuario import Usuario
from app.schemas.lista import ListaCreate, ListaResponse, ListaUpdate

router = APIRouter(prefix="/listas", tags=["listas"])
limiter = Limiter(key_func=get_remote_address)

MAX_LISTAS_POR_USUARIO = 50


@router.get("/", response_model=List[ListaResponse])
@limiter.limit("60/minute")
def listar_listas(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return db.query(Lista).filter(Lista.usuario_id == usuario.id).order_by(Lista.created_at).all()


@router.post("/", response_model=ListaResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def crear_lista(
    request: Request,
    datos: ListaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    total = db.query(Lista).filter(Lista.usuario_id == usuario.id).count()
    if total >= MAX_LISTAS_POR_USUARIO:
        raise HTTPException(
            status_code=400,
            detail=f"No puedes tener más de {MAX_LISTAS_POR_USUARIO} listas",
        )

    lista = Lista(
        usuario_id=usuario.id,
        nombre=datos.nombre,
        color=datos.color,
    )
    db.add(lista)
    db.commit()
    db.refresh(lista)
    return lista


@router.put("/{lista_id}", response_model=ListaResponse)
@limiter.limit("30/minute")
def editar_lista(
    request: Request,
    lista_id: int,
    datos: ListaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    lista = db.query(Lista).filter(Lista.id == lista_id, Lista.usuario_id == usuario.id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    if datos.nombre is not None:
        lista.nombre = datos.nombre
    if datos.color is not None:
        lista.color = datos.color
    db.commit()
    db.refresh(lista)
    return lista


@router.delete("/{lista_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
def eliminar_lista(
    request: Request,
    lista_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    lista = db.query(Lista).filter(Lista.id == lista_id, Lista.usuario_id == usuario.id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    db.query(Tarea).filter(Tarea.lista_id == lista_id).delete()
    db.delete(lista)
    db.commit()