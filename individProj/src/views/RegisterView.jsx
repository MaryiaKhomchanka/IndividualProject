import { useState } from "react";
import { AuthApi } from "../api/AuthApi";
import "../styles/RegisterView.css";

function RegisterView({ openLoginPage }) {
  const [formData, setFormData] = useState({
    name: "",
    lastName: "",
    username: "",
    email: "",
    password: "",
  });

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  function updateField(field, value) {
    setFormData((currentData) => ({ ...currentData, [field]: value }));
  }

  async function onRegisterSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    try {
      await AuthApi.register(formData);
      setSuccessMessage("Registration successful. You can now log in.");
      setTimeout(() => openLoginPage(), 1200);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  return (
    <div className="register-page">
      <form className="register-card" onSubmit={onRegisterSubmit}>
        <h1>Register</h1>

        {errorMessage && <p className="error">{errorMessage}</p>}
        {successMessage && <p className="success">{successMessage}</p>}

        <label>Name</label>
        <input type="text" value={formData.name} onChange={(e) => updateField("name", e.target.value)} required />

        <label>Last Name</label>
        <input type="text" value={formData.lastName} onChange={(e) => updateField("lastName", e.target.value)} required />

        <label>Username</label>
        <input type="text" value={formData.username} onChange={(e) => updateField("username", e.target.value)} required />

        <label>Email</label>
        <input type="email" value={formData.email} onChange={(e) => updateField("email", e.target.value)} required />

        <label>Password</label>
        <input type="password" value={formData.password} onChange={(e) => updateField("password", e.target.value)} required />

        <button type="submit" className="register-submit-btn">Register</button>

        <p className="register-switch-text">
          Already have an account?{" "}
          <button type="button" className="register-link-btn" onClick={openLoginPage}>
            Login
          </button>
        </p>
      </form>
    </div>
  );
}

export default RegisterView;