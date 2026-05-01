import { useState } from "react";

export default function AuthPage({ onSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!email || !password) {
      alert("Please fill all fields");
      return;
    }

    setLoading(true);

    try {
      const endpoint = isLogin ? "login" : "signup";

      const res = await fetch(
        `http://localhost:8000/api/auth/${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password }),
        }
      );

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || "Something went wrong");
        setLoading(false);
        return;
      }

      // ✅ STORE TOKEN
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user_id", data.user_id);
      }

      alert(data.message || "Success");

      onSuccess && onSuccess();

    } catch (err) {
      console.error(err);
      alert("Server error");
    }

    setLoading(false);
  };

  return (
    <div style={containerStyle}>
      {/* Background */}
      <div style={bgGradient}></div>

      {/* LEFT SIDE */}
      <div style={leftStyle}>
        <div style={brandingWrapper}>
          <h1 style={logoStyle}>Padh.AI</h1>

          <p style={taglineStyle}>
            Transform your study workflow with AI-powered summaries, quizzes,
            and intelligent assistance — all in one place.
          </p>

          <div style={featureList}>
            <span>⚡ Smart Summaries</span>
            <span>🧠 AI Assistant</span>
            <span>📊 Interactive Quizzes</span>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE */}
      <div style={rightStyle}>
        <div style={cardStyle}>
          <h2 style={headingStyle}>
            {isLogin ? "Welcome Back 👋" : "Create Your Account"}
          </h2>

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={inputStyle}
          />

          <button
            style={buttonStyle}
            onClick={handleAuth}
          >
            {loading ? "Please wait..." : isLogin ? "Login" : "Signup"}
          </button>

          <p style={switchText}>
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <span onClick={() => setIsLogin(!isLogin)} style={switchLink}>
              {isLogin ? " Sign up" : " Login"}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const containerStyle = {
  display: "flex",
  height: "100vh",
  background: "#0a0a0a",
  color: "white",
  fontFamily: "Inter, sans-serif",
  position: "relative",
  overflow: "hidden"
};

const bgGradient = {
  position: "absolute",
  width: "150%",
  height: "150%",
  background:
    "radial-gradient(circle at 20% 30%, rgba(250,204,21,0.08), transparent 40%), radial-gradient(circle at 80% 70%, rgba(99,102,241,0.08), transparent 40%)",
  zIndex: 0
};

const leftStyle = {
  flex: 1,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1
};

const brandingWrapper = {
  maxWidth: "420px",
  textAlign: "center"
};

const logoStyle = {
  fontSize: "56px",
  fontWeight: "bold",
  color: "#facc15",
  marginBottom: "20px"
};

const taglineStyle = {
  fontSize: "16px",
  color: "#9ca3af",
  lineHeight: "1.7",
  marginBottom: "25px"
};

const featureList = {
  display: "flex",
  flexDirection: "column",
  gap: "10px",
  color: "#d1d5db",
  fontSize: "14px"
};

const rightStyle = {
  flex: 1,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1
};

const cardStyle = {
  width: "360px",
  padding: "35px",
  borderRadius: "16px",
  background: "rgba(255,255,255,0.05)",
  border: "1px solid rgba(255,255,255,0.08)",
  backdropFilter: "blur(18px)"
};

const headingStyle = {
  marginBottom: "25px",
  textAlign: "center",
  fontSize: "22px"
};

const inputStyle = {
  width: "100%",
  padding: "12px",
  marginBottom: "15px",
  borderRadius: "8px",
  border: "1px solid rgba(255,255,255,0.1)",
  background: "rgba(255,255,255,0.06)",
  color: "white"
};

const buttonStyle = {
  width: "100%",
  padding: "12px",
  borderRadius: "8px",
  border: "none",
  background: "#facc15",
  color: "black",
  fontWeight: "bold",
  cursor: "pointer"
};

const switchText = {
  textAlign: "center",
  marginTop: "15px",
  fontSize: "14px",
  color: "#9ca3af"
};

const switchLink = {
  color: "#facc15",
  cursor: "pointer",
  marginLeft: "5px"
};