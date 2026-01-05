const API = "http://127.0.0.1:7072/api";

/* ================= AUTH GUARD (FIXED) ================= */

// ⛔ Run this FIRST — before anything renders
const studentId = localStorage.getItem("studentId");
const studentName = localStorage.getItem("studentName");

// Hide UI immediately to prevent flash
if (!studentId && !location.pathname.includes("login.html")) {
  document.body.style.display = "none";
  window.location.replace("login.html");
}

/* ================= CHAT ================= */

async function sendMessage() {
  const msgInput = document.getElementById("msg");
  const chatBox = document.getElementById("chat");

  if (!msgInput || !chatBox) return;

  const text = msgInput.value.trim();
  if (!text) return;

  chatBox.innerHTML += `<p><b>You:</b> ${text}</p>`;
  msgInput.value = "";

  try {
    const r = await fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ studentId, message: text })
    });

    const d = await r.json();
    chatBox.innerHTML += `<p><b>MindBridge:</b> ${d.reply}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch {
    chatBox.innerHTML += `<p><b>MindBridge:</b> ⚠️ Network error</p>`;
  }
}

/* ================= MOOD (FIXED UX) ================= */
function setMoodUI(card, mood) {
  const cards = document.querySelectorAll(".mood-card");
  const status = document.getElementById("status");

  // Remove active state from all cards
  cards.forEach(c => c.classList.remove("active"));

  // Activate selected card
  card.classList.add("active");

  // Immediate UI feedback
  if (status) {
    status.className = "status-card show";
    status.innerText = "Saving your mood…";
  }

  // Call backend saver
  setMood(mood);
}

async function setMood(mood) {
  const status = document.getElementById("status");
  const cards = document.querySelectorAll(".mood-card");

  // Reset active state
  cards.forEach(c => c.classList.remove("active"));

  // Highlight clicked card safely
  cards.forEach(card => {
    if (card.dataset.mood === mood) {
      card.classList.add("active");
    }
  });

  // Show saving state
  if (status) {
    status.className = "status-card show";
    status.innerText = "Saving your mood…";
  }

  try {
    const r = await fetch(API + "/mood", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ studentId, mood })
    });

    if (!r.ok) throw new Error();

    if (status) {
      status.className = "status-card show success";
      status.innerText = "✅ Mood saved successfully 💜";
    }

    // Refresh calendar if present
    if (typeof loadMoods === "function") loadMoods();

    setTimeout(() => {
      if (status) status.classList.remove("show");
    }, 3000);

  } catch {
    if (status) {
      status.className = "status-card show error";
      status.innerText = "❌ Could not save mood. Try again.";
    }
  }
}

/* ================= CALENDAR ================= */

let currentDate = new Date();
let moodMap = {};

async function loadMoods() {
  try {
    const r = await fetch(`${API}/moods?studentId=${studentId}`);
    const d = await r.json();

    moodMap = {};
    d.forEach(m => moodMap[m.date] = m.mood);

    renderCalendar();
  } catch {
    console.warn("Could not load moods");
  }
}

function renderCalendar() {
  const grid = document.getElementById("calendarGrid");
  const label = document.getElementById("monthYear");
  if (!grid || !label) return;

  grid.innerHTML = "";

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  label.innerText = currentDate.toLocaleString("default", {
    month: "long",
    year: "numeric"
  });

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Empty slots
  for (let i = 0; i < firstDay; i++) {
    grid.appendChild(Object.assign(document.createElement("div"), {
      className: "day empty"
    }));
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr =
      `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;

    const cell = document.createElement("div");
    cell.className = "day";
    cell.innerHTML = `<div class="day-number">${d}</div>`;

    const today = new Date();
    if (
      d === today.getDate() &&
      month === today.getMonth() &&
      year === today.getFullYear()
    ) {
      cell.classList.add("today");
    }

    if (moodMap[dateStr]) {
      const emoji =
        moodMap[dateStr] === "happy" ? "😊" :
        moodMap[dateStr] === "okay" ? "😐" :
        moodMap[dateStr] === "low" ? "😔" : "🤯";

      cell.innerHTML += `<div class="mood-dot">${emoji}</div>`;
    }

    grid.appendChild(cell);
  }
}

function changeMonth(step) {
  currentDate.setMonth(currentDate.getMonth() + step);
  renderCalendar();
}

// Load calendar only when present
if (document.getElementById("calendarGrid")) {
  loadMoods();
}
