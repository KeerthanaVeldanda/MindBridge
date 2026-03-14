const API = "http://localhost:7071/api";
const user = JSON.parse(localStorage.getItem("user") || "{}");

function logout() {
  localStorage.clear();
  location.href = "../auth/index.html";
}

window.addEventListener("DOMContentLoaded", () => {
  const greet = document.getElementById("greet");
  if (greet) {
    const hour = new Date().getHours();
    const tod  = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
    greet.textContent = `Good ${tod}, ${user.name || "there"} \u{1F44B}`;
  }
  const label = document.getElementById("userLabel");
  if (label) label.innerHTML = `SIGNED IN AS<br><span>${user.name || user.email || ""}</span>`;
  if (document.getElementById("moodList")) loadMoods();
  if (document.querySelector(".chatbox")) initChat();
});

// ── MOOD CHECK-IN ──────────────────────────────────────
function logMood(mood, btn) {
  document.querySelectorAll(".moods button").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");
  window._selectedMood = mood;
}

async function saveMood() {
  if (!window._selectedMood) return alert("Please select a mood first.");
  const note = document.getElementById("note").value.trim();
  const res = await fetch(`${API}/mood`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ studentId: user.id || user.email, mood: window._selectedMood, note })
  });
  if (res.ok) {
    alert("Mood logged! \u2B50");
    document.getElementById("note").value = "";
    window._selectedMood = null;
    document.querySelectorAll(".moods button").forEach(b => b.classList.remove("selected"));
  }
}

// ── MOOD HISTORY ──────────────────────────────────────
async function loadMoods() {
  const list = document.getElementById("moodList");
  list.innerHTML = "<p>Loading...</p>";
  const res    = await fetch(`${API}/moods?studentId=${user.id || user.email}`);
  const items  = await res.json();
  const sorted = items.sort((a, b) => b.date.localeCompare(a.date));
  list.innerHTML = sorted.length
    ? sorted.map(m =>
        `<div class="mood-entry">
          <strong>${m.mood}</strong> &mdash; ${m.date}
          ${m.note ? `<p>${m.note}</p>` : ""}
        </div>`).join("")
    : "<p>No mood entries yet. Start logging on the Dashboard!</p>";
}

// ── AI CHAT ──────────────────────────────────────────
const messages = [];

function initChat() {
  renderChat();
  const input = document.querySelector(".input input");
  if (input) input.addEventListener("keydown", e => { if (e.key === "Enter") sendChat(); });
}

function renderChat() {
  const box = document.querySelector(".chatbox");
  if (!box) return;
  if (messages.length === 0) {
    box.innerHTML = `<div class="bot-msg">Hi! I'm MindBridge. How are you feeling today? \u{1F499}</div>`;
    return;
  }
  box.innerHTML = messages.map(m =>
    `<div class="${m.role === "user" ? "user-msg" : "bot-msg"}">${m.content}</div>`
  ).join("");
  box.scrollTop = box.scrollHeight;
}

async function sendChat() {
  const input = document.querySelector(".input input");
  const msg   = input.value.trim();
  if (!msg) return;
  input.value = "";
  messages.push({ role: "user", content: msg });
  renderChat();
  const res  = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg, studentId: user.id || user.email || "guest" })
  });
  const data = await res.json();
  messages.push({ role: "bot", content: data.reply });
  renderChat();
}
