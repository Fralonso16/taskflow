import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, login } from "../api/client";

function RegisterPage() {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");

        try {
            await register(username, email, password);
            await login(username, password);
            navigate("/boards");
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <div className="page-container">
            <div className="auth-card">
                <h1>Crear cuenta</h1>

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
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
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
                        Registrarse
                    </button>
                </form>

                <span className="link-muted">
                    ¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link>
                </span>
            </div>
        </div>
    );
}

export default RegisterPage;