// BrowserRouter: habilita el sistema de rutas en toda la aplicacion
// Routes: contiene todas las rutas posibles
// Route: define UNA ruta concreta (url -> componente a mostrar)
// Navigate: sirve para redirigir automaticamente de una ruta a otra
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import BoardsPage from "./pages/BoardsPage";
import BoardPage from "./pages/BoardPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Si entras a la raiz "/", te redirige automaticamente a /login */}
        <Route path="/" element={<Navigate to="/login" />} />

        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/boards" element={<BoardsPage />} />

        {/* :boardId es un "parametro" - captura cualquier valor en esa
            posicion de la URL (ej. /boards/1, /boards/2...) */}
        <Route path="/boards/:boardId" element={<BoardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;