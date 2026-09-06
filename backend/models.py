import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class RolMiembro(str, enum.Enum):
    """Los dos roles posibles dentro de un tablero."""
    PROPIETARIO = "propietario"
    MIEMBRO = "miembro"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Un usuario puede ser miembro de varios tableros
    memberships = relationship("BoardMember", back_populates="user")


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Un tablero tiene varios miembros y varias listas
    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    lists = relationship("List", back_populates="board", cascade="all, delete-orphan")


class BoardMember(Base):
    """
    Tabla intermedia entre User y Board: representa la pertenencia de
    un usuario a un tablero concreto, junto con su rol en ese tablero.
    Es lo que permite que un mismo usuario sea propietario en un tablero
    y simple miembro en otro.
    """
    __tablename__ = "board_members"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(RolMiembro), nullable=False, default=RolMiembro.MIEMBRO)

    board = relationship("Board", back_populates="members")
    user = relationship("User", back_populates="memberships")


class List(Base):
    """Una columna del tablero (ej. 'Por hacer', 'En progreso', 'Hecho')."""
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False, default=0)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)

    board = relationship("Board", back_populates="lists")
    cards = relationship("Card", back_populates="list", cascade="all, delete-orphan")


class Card(Base):
    """Una tarjeta individual dentro de una lista."""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    list = relationship("List", back_populates="cards")