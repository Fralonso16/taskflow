from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import auth, boards, lists, cards, ws

# Crea todas las tablas definidas en models.py si no existen aun
# (User, Board, BoardMember, List, Card - las 5 a la vez)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta las rutas de auth.py a la aplicacion principal
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(lists.router)
app.include_router(cards.router)
app.include_router(ws.router)


@app.get("/")
def root():
    return {"status": "TaskFlow API funcionando"}