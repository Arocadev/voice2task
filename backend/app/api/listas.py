from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.lista import Lista
from app.models.tarea import Tarea
from app.models.usuario import Usuario
from app.schemas.lista import ListaCreate, ListaResponse, ListaUpdate

router = APIRouter(prefix="/listas", tags=["listas"])


@router.get("/", response_model=List[ListaResponse])
def listar_listas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return db.query(Lista).filter(Lista.usuario_id == usuario.id).order_by(Lista.created_at).all()


@router.post("/", response_model=ListaResponse, status_code=status.HTTP_201_CREATED)
def crear_lista(
    datos: ListaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
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
def editar_lista(
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
def eliminar_lista(
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