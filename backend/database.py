import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga el archivo .env si existe (para cuando ejecutas la API directamente
# con Python, fuera de Docker). Dentro de Docker, las variables ya vienen
# inyectadas por docker-compose.yml, asi que esto simplemente no encuentra
# nada que cargar y no pasa nada.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()