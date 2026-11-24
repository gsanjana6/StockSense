
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { getErrorMessage } from "../utils/errorHelpers";

function Signup() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      await api.post("/users/register", {
        name: name,
        email: email,
        password: password,
      });

      alert("Registration successful! Please log in.");
      navigate("/login");
    } catch (err) {
      console.error(err);

      setError(
        getErrorMessage(
          err,
          "Registration failed. Please try a different email."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>StockSense</h1>
        <p>Create your account</p>

        <form onSubmit={handleSignup}>
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <p style={{ marginTop: "15px", fontSize: "0.9rem" }}>
          Already have an account?{" "}
          <span
            style={{
              color: "var(--ss-primary)",
              cursor: "pointer",
              fontWeight: "bold",
            }}
            onClick={() => navigate("/login")}
          >
            Log in here
          </span>
        </p>
      </div>
    </div>
  );
}

export default Signup;
