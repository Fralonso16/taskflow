import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/client";

function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");

        try {
            await login(username, password);
            navigate("/boards");
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        // page-container centra el contenido y limita su ancho
        <div className="page-container">
            {/* auth-card: la tarjeta blanca con sombra que contiene el formulario */}
            <div className="auth-card">
                <h1>Iniciar sesión</h1>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <input
                            type="text"
                            placeholder="Usuario"
                            value={username}
                            onChange={(event) => setUsername(event.target.value)}
                            className="input"
                        />
                    </div>

                    <div className="form-group">
                        <input
                            type="password"
                            placeholder="Contraseña"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            className="input"
                        />
                    </div>

                    {error && <p className="error-text">{error}</p>}

                    <button type="submit" className="btn btn-primary">
                        Entrar
                    </button>
                </form>

                <span className="link-muted">
                    ¿No tienes cuenta? <Link to="/register">Registrate aquí</Link>
                </span>
            </div>
        </div>
    );
}

export default LoginPage;