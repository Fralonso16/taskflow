from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import List as ListModel, BoardMember
from schemas import ListCreate, ListOut
from dependencies import get_membership

# Las rutas de listas cuelgan de un tablero concreto: /boards/{board_id}/lists
router = APIRouter(prefix="/boards/{board_id}/lists", tags=["Listas"])


@router.post("", response_model=ListOut)
def create_list(
    board_id: int,
    list_data: ListCreate,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    """Crea una lista nueva en el tablero. Cualquier miembro puede
    crear listas, no solo el propietario."""
    new_list = ListModel(
        name=list_data.name,
        position=list_data.position,
        board_id=board_id,
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


@router.get("", response_model=list[ListOut])
def get_lists(
    board_id: int,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    """Lista todas las columnas de un tablero, ordenadas por posicion."""
    return (
        db.query(ListModel)
        .filter(ListModel.board_id == board_id)
        .order_by(ListModel.position)
        .all()
    )


@router.delete("/{list_id}")
def delete_list(
    board_id: int,
    list_id: int,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    list_obj = (
        db.query(ListModel)
        .filter(ListModel.id == list_id, ListModel.board_id == board_id)
        .first()
    )
    if list_obj is None:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    db.delete(list_obj)
    db.commit()
    return {"detail": "Lista eliminada correctamente"}