import { useState } from "react";
import { AuthApi } from "../api/AuthApi";
import { useAuth } from "../context/AuthContext";
import "../styles/LoginView.css";

function LoginView({ openRegisterPage, openTouristPage }) {
  const { login } = useAuth();
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  async function onLoginSubmit(event) {
    event.preventDefault();
    setErrorMessage("");

    try {
      const response = await AuthApi.login({ usernameOrEmail, password });
      login(response);
      openTouristPage();
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onLoginSubmit}>
        <h1>Login</h1>

        {errorMessage && <p className="error">{errorMessage}</p>}

        <label>Username or Email</label>
        <input
          type="text"
          value={usernameOrEmail}
          onChange={(event) => setUsernameOrEmail(event.target.value)}
          required
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        <button type="submit" className="login-submit-btn">Login</button>

        <p className="login-switch-text">
          Do not have an account?{" "}
          <button type="button" className="login-link-btn" onClick={openRegisterPage}>
            Register
          </button>
        </p>
      </form>
    </div>
  );
}

export default LoginView;