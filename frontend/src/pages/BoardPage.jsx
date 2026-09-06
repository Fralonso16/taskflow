import { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { getBoard, getLists, createList, deleteList, createCard, updateCard } from "../api/client";

function BoardPage() {
    const { boardId } = useParams();

    const [board, setBoard] = useState(null);
    const [lists, setLists] = useState([]);
    const [newListName, setNewListName] = useState("");
    const [newCardTitle, setNewCardTitle] = useState({});

    const wsRef = useRef(null);

    async function loadBoardData() {
        const boardData = await getBoard(boardId);
        setBoard(boardData);
        const listsData = await getLists(boardId);
        setLists(listsData);
    }

    useEffect(() => {
        loadBoardData();

        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/boards/${boardId}`);
        wsRef.current = ws;

        ws.onmessage = () => {
            loadBoardData();
        };

        return () => {
            ws.close();
        };
    }, [boardId]);

    async function handleCreateList(event) {
        event.preventDefault();
        if (!newListName.trim()) return;
        await createList(boardId, newListName, lists.length);
        setNewListName("");
        loadBoardData();
    }

    async function handleCreateCard(event, listId) {
        event.preventDefault();
        const title = newCardTitle[listId];
        if (!title || !title.trim()) return;
        await createCard(boardId, listId, title, "");
        setNewCardTitle({ ...newCardTitle, [listId]: "" });
        loadBoardData();
    }

    async function handleMoveCard(cardId, newListId) {
        await updateCard(boardId, cardId, { list_id: newListId });
    }

    async function handleDeleteList(listId) {
        // confirm() muestra un dialogo nativo del navegador para confirmar
        // la accion - util para acciones destructivas como esta, que no
        // se pueden deshacer
        const confirmado = window.confirm(
            "¿Seguro que quieres eliminar esta lista? Se borraran tambien todas sus tarjetas."
        );
        if (!confirmado) return;

        await deleteList(boardId, listId);
        loadBoardData();
    }

    if (!board) return <p className="page-container-wide">Cargando...</p>;

    return (
        <div className="page-container-wide">
            <Link to="/boards" className="back-link">← Volver a mis tableros</Link>

            <div className="topbar">
                <h1>{board.name}</h1>
            </div>

            <form onSubmit={handleCreateList} className="inline-form">
                <input
                    type="text"
                    placeholder="Nombre de la lista nueva"
                    value={newListName}
                    onChange={(event) => setNewListName(event.target.value)}
                    className="input"
                    style={{ maxWidth: "260px" }}
                />
                <button type="submit" className="btn btn-primary" style={{ width: "auto" }}>
                    Añadir lista
                </button>
            </form>

            {/* board-columns: fila horizontal con scroll si hay muchas listas */}
            <div className="board-columns">
                {lists.map((list) => (
                    <div key={list.id} className="board-column">
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                            <h3 style={{ marginBottom: 0 }}>{list.name}</h3>
                            <button
                                onClick={() => handleDeleteList(list.id)}
                                className="btn-small"
                                title="Eliminar lista"
                            >
                                ✕
                            </button>
                        </div>

                        {list.cards?.map((card) => (
                            <div key={card.id} className="task-card">
                                <p>{card.title}</p>
                                <div className="task-card-actions">
                                    {lists
                                        .filter((otherList) => otherList.id !== list.id)
                                        .map((otherList) => (
                                            <button
                                                key={otherList.id}
                                                onClick={() => handleMoveCard(card.id, otherList.id)}
                                                className="btn-small"
                                            >
                                                → {otherList.name}
                                            </button>
                                        ))}
                                </div>
                            </div>
                        ))}

                        <form onSubmit={(event) => handleCreateCard(event, list.id)}>
                            <input
                                type="text"
                                placeholder="+ Nueva tarjeta"
                                value={newCardTitle[list.id] || ""}
                                onChange={(event) =>
                                    setNewCardTitle({ ...newCardTitle, [list.id]: event.target.value })
                                }
                                className="new-card-input"
                            />
                        </form>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default BoardPage;