from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Board, BoardMember, User, RolMiembro
from schemas import BoardCreate, BoardOut, BoardMemberOut, BoardMemberInvite
from dependencies import get_current_user, get_membership

router = APIRouter(prefix="/boards", tags=["Tableros"])


@router.post("", response_model=BoardOut)
def create_board(
    board: BoardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un tablero nuevo. El creador se convierte automaticamente
    en su propietario (PROPIETARIO), no un simple miembro."""
    new_board = Board(name=board.name, description=board.description)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    membership = BoardMember(
        board_id=new_board.id,
        user_id=current_user.id,
        role=RolMiembro.PROPIETARIO,
    )
    db.add(membership)
    db.commit()

    return new_board


@router.get("", response_model=list[BoardOut])
def list_my_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista solo los tableros de los que el usuario actual es miembro."""
    return (
        db.query(Board)
        .join(BoardMember)
        .filter(BoardMember.user_id == current_user.id)
        .all()
    )


@router.get("/{board_id}", response_model=BoardOut)
def get_board(
    board_id: int,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    """Obtiene un tablero. get_membership ya comprueba que eres miembro
    antes de que esta funcion se ejecute siquiera."""
    board = db.query(Board).filter(Board.id == board_id).first()
    if board is None:
        raise HTTPException(status_code=404, detail="Tablero no encontrado")
    return board


@router.post("/{board_id}/members", response_model=BoardMemberOut)
def invite_member(
    board_id: int,
    invite: BoardMemberInvite,
    db: Session = Depends(get_db),
    membership: BoardMember = Depends(get_membership),
):
    """Invita a un usuario existente al tablero.
    Solo el PROPIETARIO puede invitar."""
    if membership.role != RolMiembro.PROPIETARIO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el propietario puede invitar miembros",
        )

    user_to_invite = db.query(User).filter(User.username == invite.username).first()
    if user_to_invite is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    existing = (
        db.query(BoardMember)
        .filter(BoardMember.board_id == board_id, BoardMember.user_id == user_to_invite.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ese usuario ya es miembro del tablero")

    new_member = BoardMember(
        board_id=board_id,
        user_id=user_to_invite.id,
        role=RolMiembro.MIEMBRO,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member