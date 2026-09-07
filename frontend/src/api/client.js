// URL base de nuestra API backend. La cambiaremos por la URL real
// cuando despleguemos en Render, igual que hicimos en los proyectos anteriores
const API_URL = "https://taskflow-api-8wia.onrender.com";

// Funcion auxiliar: guarda el token JWT en el almacenamiento del navegador,
// para que sobreviva aunque recargues la pagina
export function saveToken(token) {
    localStorage.setItem("token", token);
}

// Funcion auxiliar: recupera el token guardado (o null si no hay ninguno)
export function getToken() {
    return localStorage.getItem("token");
}

// Funcion auxiliar: borra el token (para el logout)
export function clearToken() {
    localStorage.removeItem("token");
}

// Funcion central que hace TODAS las peticiones a la API.
// Recibe la ruta (ej. "/boards"), el metodo HTTP, y opcionalmente un body.
// Añade automaticamente el token de autenticacion si existe.
async function request(path, { method = "GET", body } = {}) {
    const token = getToken();

    const headers = { "Content-Type": "application/json" };
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${path}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });

    // Si la API devuelve un error (400, 401, 403, 404...), lo convertimos
    // en un error de JavaScript que podremos "atrapar" mas adelante
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Error en la peticion");
    }

    return response.json();
}

// --- Funciones especificas para cada endpoint de la API ---
// Cada una de estas es lo que usaremos desde las paginas de React

export function register(username, email, password) {
    return request("/auth/register", {
        method: "POST",
        body: { username, email, password },
    });
}

export async function login(username, password) {
    // El login es distinto: la API espera form-data, no JSON,
    // asi que no podemos usar la funcion "request" generica de arriba
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
    });
    if (!response.ok) {
        throw new Error("Usuario o contraseña incorrectos");
    }
    const data = await response.json();
    saveToken(data.access_token);
    return data;
}

export function getBoards() {
    return request("/boards");
}

export function createBoard(name, description) {
    return request("/boards", {
        method: "POST",
        body: { name, description },
    });
}

export function getBoard(boardId) {
    return request(`/boards/${boardId}`);
}

export function inviteMember(boardId, username) {
    return request(`/boards/${boardId}/members`, {
        method: "POST",
        body: { username },
    });
}

export function getLists(boardId) {
    return request(`/boards/${boardId}/lists`);
}

export function createList(boardId, name, position = 0) {
    return request(`/boards/${boardId}/lists`, {
        method: "POST",
        body: { name, position },
    });
}

export function deleteList(boardId, listId) {
    return request(`/boards/${boardId}/lists/${listId}`, {
        method: "DELETE",
    });
}

export function createCard(boardId, listId, title, description) {
    return request(`/boards/${boardId}/cards?list_id=${listId}`, {
        method: "POST",
        body: { title, description },
    });
}

export function updateCard(boardId, cardId, changes) {
    return request(`/boards/${boardId}/cards/${cardId}`, {
        method: "PATCH",
        body: changes,
    });
}

export function deleteCard(boardId, cardId) {
    return request(`/boards/${boardId}/cards/${cardId}`, {
        method: "DELETE",
    });
}