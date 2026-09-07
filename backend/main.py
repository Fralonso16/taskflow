from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import auth, boards, lists, cards, ws

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Todo lo de ANTES del "yield" se ejecuta al arrancar la aplicacion
    # (equivalente a lo que antes hacia @app.on_event("startup")).
    # Igual que antes, esto solo ocurre si la app arranca de verdad,
    # no simplemente al importar el archivo - por eso los tests, que
    # sustituyen la conexion por una de prueba, nunca llegan a intentar
    # conectarse a la base de datos real
    Base.metadata.create_all(bind=engine)
    yield
    # Todo lo de DESPUES del "yield" se ejecutaria al apagar la
    # aplicacion (no necesitamos nada aqui por ahora)


app = FastAPI(title="TaskFlow API", lifespan=lifespan)

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