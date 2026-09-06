from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import RolMiembro


# --- Usuario ---

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Tablero ---

class BoardCreate(BaseModel):
    name: str
    description: Optional[str] = None


class BoardOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Miembro de tablero ---

class BoardMemberOut(BaseModel):
    id: int
    user_id: int
    role: RolMiembro

    model_config = {"from_attributes": True}


class BoardMemberInvite(BaseModel):
    username: str  # invitar a alguien por su nombre de usuario


# --- Tarjeta ---

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    position: Optional[int] = 0


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None
    list_id: Optional[int] = None


class CardOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    position: int
    list_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Lista (columna) ---

class ListCreate(BaseModel):
    name: str
    position: Optional[int] = 0


class ListOut(BaseModel):
    id: int
    name: str
    position: int
    board_id: int
    # Al incluir esto, cada lista devuelve tambien sus tarjetas -
    # es lo que necesita el frontend para dibujar el tablero completo
    # de una sola llamada, en vez de pedir las tarjetas por separado
    cards: list[CardOut] = []

    model_config = {"from_attributes": True}