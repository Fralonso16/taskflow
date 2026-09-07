# TaskFlow

[![Backend Tests](https://github.com/Fralonso16/taskflow/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/Fralonso16/taskflow/actions/workflows/backend-tests.yml)

Gestor de proyectos estilo Trello/Kanban con autenticación, roles por tablero y actualizaciones en tiempo real.

## 🔗 Demo en vivo

- **Frontend**: https://taskflow-frontend-zev6.onrender.com
- **API (Swagger)**: https://taskflow-api-8wia.onrender.com/docs

> Nota: al usar el plan gratuito de Render, el backend puede "dormir" tras un rato de inactividad (la primera petición tarda unos segundos en responder). La base de datos (Neon) es gratuita y permanente, sin esa limitación.

## Funcionalidades

- Registro y login con autenticación JWT
- Creación de tableros, con roles (propietario / miembro)
- Invitación de usuarios a un tablero
- Listas (columnas) y tarjetas, con creación y eliminación
- Mover tarjetas entre listas
- **Actualizaciones en tiempo real** vía WebSockets: los cambios de un usuario se ven al instante en la pantalla de los demás miembros del tablero
- Aislamiento de datos verificado: un usuario no puede ver ni modificar tableros de los que no es miembro

## Arquitectura

┌─────────────┐ HTTP/WS ┌──────────────┐
│ Frontend │ ────────────────► │ Backend │
│ (React) │ ◄──────────────── │ (FastAPI) │
└─────────────┘ └──────┬───────┘
│
┌─────────────────┼─────────────────┐
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐
│ PostgreSQL │ │ Redis │
│ (Neon) │ │ (pub/sub) │
└─────────────┘ └─────────────┘


- El **backend** expone una API REST y un endpoint WebSocket por tablero
- Cuando alguien modifica una tarjeta, el backend publica un evento en un canal de **Redis** específico de ese tablero
- Todos los usuarios conectados por WebSocket a ese tablero reciben el evento y actualizan su vista, sin recargar la página

## Tecnologías

**Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, JWT (python-jose), bcrypt, WebSockets, pytest

**Frontend**: React, React Router, Vite

**Infraestructura**: Docker, Docker Compose (desarrollo local), GitHub Actions (CI), Render (despliegue), Neon (PostgreSQL gestionado)

## Cómo ejecutarlo en local

Requiere Docker Desktop y Node.js instalados.

1. Clona el repositorio:

git clone https://github.com/Fralonso16/taskflow.git
cd taskflow


2. Crea el archivo `backend/.env`:

DATABASE_URL=postgresql://taskflow:taskflow_dev_password@localhost:5432/taskflow
REDIS_URL=redis://localhost:6379
SECRET_KEY=una-clave-secreta-cualquiera-para-desarrollo


3. Levanta el backend, PostgreSQL y Redis con Docker Compose:

docker compose up --build


4. En otra terminal, levanta el frontend:

cd frontend
npm install
npm run dev


5. Abre `http://localhost:5173`

## Estructura del proyecto

taskflow/
├── docker-compose.yml # Orquesta API + PostgreSQL + Redis
├── backend/
│ ├── main.py # Punto de entrada de la API
│ ├── models.py # Modelos de base de datos (5 tablas)
│ ├── schemas.py # Validación de datos (Pydantic)
│ ├── auth.py # Hasheo de contraseñas y JWT
│ ├── dependencies.py # Autenticación y autorización por tablero
│ ├── routers/ # Rutas organizadas por dominio
│ │ ├── auth.py
│ │ ├── boards.py
│ │ ├── lists.py
│ │ ├── cards.py
│ │ └── ws.py # WebSockets
│ └── test_main.py # Tests automatizados
└── frontend/
└── src/
├── api/client.js # Todas las llamadas a la API
├── pages/ # Login, Registro, Tableros, Tablero
└── App.jsx # Rutas de la aplicación


## Modelo de datos

- **User**: usuarios registrados
- **Board**: tableros
- **BoardMember**: relación usuario↔tablero, con rol (propietario/miembro)
- **List**: columnas dentro de un tablero
- **Card**: tarjetas dentro de una lista