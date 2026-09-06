import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db

# Base de datos de PRUEBA en memoria - totalmente separada de PostgreSQL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def registrar_y_loguear(username: str, password: str) -> str:
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": password},
    )
    login_response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    return login_response.json()["access_token"]


# --- Tests de autenticacion ---

def test_registro_usuario_nuevo():
    response = client.post(
        "/auth/register",
        json={"username": "fran", "email": "fran@test.com", "password": "clave12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "hashed_password" not in data


def test_registro_username_duplicado():
    client.post(
        "/auth/register",
        json={"username": "fran", "email": "fran1@test.com", "password": "clave12345"},
    )
    response = client.post(
        "/auth/register",
        json={"username": "fran", "email": "fran2@test.com", "password": "otraClave"},
    )
    assert response.status_code == 400


# --- Tests de tableros y roles ---

def test_crear_tablero_y_ser_propietario():
    token = registrar_y_loguear("ana", "clave12345")
    response = client.post(
        "/boards", json={"name": "Tablero de Ana"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Tablero de Ana"


def test_usuario_no_miembro_no_puede_ver_tablero():
    """El test mas importante: aislamiento entre usuarios distintos."""
    token_a = registrar_y_loguear("usuario_a", "claveA12345")
    token_b = registrar_y_loguear("usuario_b", "claveB12345")

    crear = client.post(
        "/boards", json={"name": "Tablero privado de A"}, headers={"Authorization": f"Bearer {token_a}"}
    )
    board_id = crear.json()["id"]

    response = client.get(f"/boards/{board_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 403


def test_invitar_miembro_da_acceso():
    token_a = registrar_y_loguear("usuario_c", "claveC12345")
    token_b = registrar_y_loguear("usuario_d", "claveD12345")

    crear = client.post(
        "/boards", json={"name": "Tablero compartido"}, headers={"Authorization": f"Bearer {token_a}"}
    )
    board_id = crear.json()["id"]

    client.post(
        f"/boards/{board_id}/members",
        json={"username": "usuario_d"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    response = client.get(f"/boards/{board_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200


def test_solo_propietario_puede_invitar():
    token_a = registrar_y_loguear("usuario_e", "claveE12345")
    token_b = registrar_y_loguear("usuario_f", "claveF12345")
    token_c = registrar_y_loguear("usuario_g", "claveG12345")

    crear = client.post(
        "/boards", json={"name": "Otro tablero"}, headers={"Authorization": f"Bearer {token_a}"}
    )
    board_id = crear.json()["id"]

    # Invitamos a B como simple miembro
    client.post(
        f"/boards/{board_id}/members",
        json={"username": "usuario_f"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # B (simple miembro, no propietario) intenta invitar a C - debe fallar
    response = client.post(
        f"/boards/{board_id}/members",
        json={"username": "usuario_g"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 403


# --- Tests de listas y tarjetas ---

def test_crear_lista_y_tarjeta():
    token = registrar_y_loguear("usuario_h", "claveH12345")
    crear_board = client.post(
        "/boards", json={"name": "Tablero con tareas"}, headers={"Authorization": f"Bearer {token}"}
    )
    board_id = crear_board.json()["id"]

    crear_lista = client.post(
        f"/boards/{board_id}/lists",
        json={"name": "Por hacer", "position": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert crear_lista.status_code == 200
    list_id = crear_lista.json()["id"]

    crear_tarjeta = client.post(
        f"/boards/{board_id}/cards?list_id={list_id}",
        json={"title": "Mi primera tarea"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert crear_tarjeta.status_code == 200
    assert crear_tarjeta.json()["list_id"] == list_id


def test_mover_tarjeta_entre_listas():
    token = registrar_y_loguear("usuario_i", "claveI12345")
    crear_board = client.post(
        "/boards", json={"name": "Tablero movimiento"}, headers={"Authorization": f"Bearer {token}"}
    )
    board_id = crear_board.json()["id"]

    lista1 = client.post(
        f"/boards/{board_id}/lists", json={"name": "Lista 1"}, headers={"Authorization": f"Bearer {token}"}
    ).json()
    lista2 = client.post(
        f"/boards/{board_id}/lists", json={"name": "Lista 2"}, headers={"Authorization": f"Bearer {token}"}
    ).json()

    tarjeta = client.post(
        f"/boards/{board_id}/cards?list_id={lista1['id']}",
        json={"title": "Tarea movible"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    mover = client.patch(
        f"/boards/{board_id}/cards/{tarjeta['id']}",
        json={"list_id": lista2["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert mover.status_code == 200
    assert mover.json()["list_id"] == lista2["id"]


def test_no_se_puede_mover_tarjeta_a_lista_de_otro_tablero():
    """Verifica la comprobacion de seguridad que añadimos en cards.py."""
    token = registrar_y_loguear("usuario_j", "claveJ12345")

    board1 = client.post(
        "/boards", json={"name": "Tablero 1"}, headers={"Authorization": f"Bearer {token}"}
    ).json()
    board2 = client.post(
        "/boards", json={"name": "Tablero 2"}, headers={"Authorization": f"Bearer {token}"}
    ).json()

    lista_board1 = client.post(
        f"/boards/{board1['id']}/lists", json={"name": "Lista"}, headers={"Authorization": f"Bearer {token}"}
    ).json()
    lista_board2 = client.post(
        f"/boards/{board2['id']}/lists", json={"name": "Lista"}, headers={"Authorization": f"Bearer {token}"}
    ).json()

    tarjeta = client.post(
        f"/boards/{board1['id']}/cards?list_id={lista_board1['id']}",
        json={"title": "Tarea"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    # Intentamos mover la tarjeta del tablero 1 a una lista del tablero 2
    response = client.patch(
        f"/boards/{board1['id']}/cards/{tarjeta['id']}",
        json={"list_id": lista_board2["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404