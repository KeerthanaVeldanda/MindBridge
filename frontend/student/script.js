const API_BASE = "http://localhost:7071/api";

// ENTER / LOGIN
function enterApp() {
  const studentName = document.getElementById("studentName").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  fetch(`${API_BASE}/enter`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      studentname: studentName,
      email: email,
      password: password
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        document.getElementById("loginBox").classList.add("hidden");
        document.getElementById("dashboard").classList.remove("hidden");
      } else {
        alert(data.error || "Login failed");
      }
    })
    .catch(err => {
      console.error(err);
      alert("Backend not responding. Is func running?");
    });
}

// CHAT
function sendMessage() {
  const input = document.getElementById("textInput");
  const message = input.value;
  if (!message) return;

  fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      const chatBox = document.getElementById("chatBox");
      chatBox.innerHTML += `<p><b>You:</b> ${message}</p>`;
      chatBox.innerHTML += `<p><b>MindBridge:</b> ${data.reply}</p>`;
      input.value = "";
    })
    .catch(err => {
      console.error(err);
      alert("Chat service not responding");
    });
}
