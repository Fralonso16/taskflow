from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o caducado",
        )
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return user

from fastapi import Path
from sqlalchemy.orm import Session as SessionType
from models import BoardMember


def get_membership(
    board_id: int = Path(...),
    current_user=Depends(get_current_user),
    db: SessionType = Depends(get_db),
) -> BoardMember:
    """
    Comprueba que el usuario actual pertenece al tablero solicitado.
    Si no es miembro, corta la peticion con 403 (prohibido) antes de
    que llegue a ejecutarse la logica de la ruta.
    """
    membership = (
        db.query(BoardMember)
        .filter(BoardMember.board_id == board_id, BoardMember.user_id == current_user.id)
        .first()
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este tablero",
        )
    return membership