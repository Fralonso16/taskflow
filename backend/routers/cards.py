from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Card, List as ListModel, BoardMember
from schemas import CardCreate, CardUpdate, CardOut
from dependencies import get_membership
from routers.ws import publish_board_update

router = APIRouter(prefix="/boards/{board_id}/cards", tags=["Tarjetas"])


def _verificar_lista_pertenece_al_tablero(db: Session, list_id: int, board_id: int) -> ListModel:
    """Funcion auxiliar (no es una ruta): comprueba que una lista
    concreta pertenece de verdad al tablero indicado, para que nadie
    pueda crear una tarjeta en una lista de OTRO tablero distinto."""
    list_obj = (
        db.query(ListModel)
        .filter(ListModel.id == list_id, ListModel.board_id == board_id)
        .first()
    )
    if list_obj is None:
        raise HTTPException(status_code=404, detail="Lista no encontrada en este tablero")
    return list_obj


@router.post("", response_model=CardOut)
async def create_card(
    board_id: int,
    list_id: int,
    card: CardCreate,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    _verificar_lista_pertenece_al_tablero(db, list_id, board_id)

    new_card = Card(
        title=card.title,
        description=card.description,
        position=card.position,
        list_id=list_id,
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    await publish_board_update(
        board_id, "card_created", {"id": new_card.id, "title": new_card.title, "list_id": list_id}
    )

    return new_card


@router.patch("/{card_id}", response_model=CardOut)
async def update_card(
    board_id: int,
    card_id: int,
    card_update: CardUpdate,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    """Actualiza una tarjeta - incluyendo moverla a otra lista,
    si se envia un list_id distinto."""
    card = db.query(Card).join(ListModel).filter(
        Card.id == card_id, ListModel.board_id == board_id
    ).first()
    if card is None:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    update_data = card_update.model_dump(exclude_unset=True)

    # Si se esta moviendo a otra lista, comprobamos que esa lista
    # tambien pertenece a este mismo tablero (evita mover tarjetas
    # a listas de tableros ajenos)
    if "list_id" in update_data:
        _verificar_lista_pertenece_al_tablero(db, update_data["list_id"], board_id)

    for key, value in update_data.items():
        setattr(card, key, value)

    db.commit()
    db.refresh(card)

    await publish_board_update(
        board_id, "card_updated", {"id": card.id, "list_id": card.list_id, "position": card.position}
    )

    return card


@router.delete("/{card_id}")
def delete_card(
    board_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    card = db.query(Card).join(ListModel).filter(
        Card.id == card_id, ListModel.board_id == board_id
    ).first()
    if card is None:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    db.delete(card)
    db.commit()
    return {"detail": "Tarjeta eliminada correctamente"}