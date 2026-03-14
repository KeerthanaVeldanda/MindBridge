const API = "http://localhost:7071/api";

function showLogin() {
  document.getElementById("loginBox").classList.remove("hidden");
  document.getElementById("registerBox").classList.add("hidden");
  document.getElementById("lTab").classList.add("active");
  document.getElementById("rTab").classList.remove("active");
}

function showRegister() {
  document.getElementById("registerBox").classList.remove("hidden");
  document.getElementById("loginBox").classList.add("hidden");
  document.getElementById("rTab").classList.add("active");
  document.getElementById("lTab").classList.remove("active");
}

async function login() {
  const email    = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  if (!email || !password) return alert("Please fill in all fields.");
  try {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) return alert("Invalid email or password.");
    const user = await res.json();
    localStorage.setItem("user", JSON.stringify(user));
    location.href = user.role === "counsellor"
      ? "../counsellor/dashboard.html"
      : "../student/index.html";
  } catch {
    alert("Could not connect to server. Is the backend running?");
  }
}

async function register() {
  const name     = document.getElementById("regName").value.trim();
  const email    = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const role     = document.getElementById("regRole").value;
  if (!name || !email || !password) return alert("Please fill in all fields.");
  try {
    const res = await fetch(`${API}/enter`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ studentName: name, email, password, role })
    });
    if (!res.ok) return alert("Registration failed.");
    alert("Account created! Please sign in.");
    showLogin();
  } catch {
    alert("Could not connect to server. Is the backend running?");
  }
}
