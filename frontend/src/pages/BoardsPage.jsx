import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getBoards, createBoard, clearToken } from "../api/client";

function BoardsPage() {
    const [boards, setBoards] = useState([]);
    const [newBoardName, setNewBoardName] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();

    async function loadBoards() {
        try {
            const data = await getBoards();
            setBoards(data);
        } catch (err) {
            setError(err.message);
        }
    }

    useEffect(() => {
        loadBoards();
    }, []);

    async function handleCreateBoard(event) {
        event.preventDefault();
        if (!newBoardName.trim()) return;

        try {
            await createBoard(newBoardName, "");
            setNewBoardName("");
            loadBoards();
        } catch (err) {
            setError(err.message);
        }
    }

    function handleLogout() {
        clearToken();
        navigate("/login");
    }

    return (
        // page-container-wide: mas ancho que el de login, para que quepan
        // varias tarjetas de tablero en fila
        <div className="page-container-wide">
            <div className="topbar">
                <h1>Mis tableros</h1>
                <button onClick={handleLogout} className="btn btn-secondary">
                    Cerrar sesion
                </button>
            </div>

            <form onSubmit={handleCreateBoard} className="inline-form">
                <input
                    type="text"
                    placeholder="Nombre del tablero nuevo"
                    value={newBoardName}
                    onChange={(event) => setNewBoardName(event.target.value)}
                    className="input"
                />
                <button type="submit" className="btn btn-primary" style={{ width: "auto" }}>
                    Crear
                </button>
            </form>

            {error && <p className="error-text">{error}</p>}

            {/* board-list: usa CSS grid (definido en index.css) para acomodar
          varias tarjetas por fila automaticamente segun el ancho disponible */}
            <ul className="board-list">
                {boards.map((board) => (
                    <li key={board.id} className="board-list-item">
                        <Link to={`/boards/${board.id}`}>{board.name}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default BoardsPage;