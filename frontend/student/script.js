/* ============================
   CONFIG & GLOBAL STATE
============================ */

const API = "http://127.0.0.1:7071/api";

let studentId = "";
let moodHistory = {}; // { "YYYY-MM-DD": "happy" }

let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();

/* ============================
   SECTION NAVIGATION
============================ */

function showSection(section) {
  const sections = [
    "dashboardSection",
    "chatSection",
    "moodsSection",
    "calendarSection"
  ];

  sections.forEach(id => {
    document.getElementById(id).classList.add("hidden");
  });

  document.getElementById(section + "Section").classList.remove("hidden");

  // Highlight active sidebar item
  document.querySelectorAll(".sidebar nav a").forEach(a => {
    a.classList.remove("active");
  });

  event.target.classList.add("active");
}

/* ============================
   LOGIN
============================ */

async function login() {
  const name = studentName.value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!name || !email || !password) {
    loginError.innerText = "All fields are required";
    return;
  }

  const res = await fetch(`${API}/enter`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      studentName: name,
      email,
      password
    })
  });

  const data = await res.json();

  if (!data.success) {
    loginError.innerText = "Login failed";
    return;
  }

  studentId = email;

  loginOverlay.classList.add("hidden");
  app.classList.remove("hidden");

  welcomeText.innerText = `Welcome, ${name} 🤍`;

  loadCalendar();
}

/* ============================
   CHAT
============================ */

function addMessage(text, type) {
  const msg = document.createElement("div");
  msg.className = `msg ${type}`;
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const text = textInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  textInput.value = "";

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        studentId
      })
    });

    const data = await res.json();
    addMessage(data.reply, "bot");
  } catch (err) {
    addMessage("I'm here with you 🤍 Please try again.", "bot");
  }
}

/* ============================
   MOOD SELECTION
============================ */

async function selectMood(mood) {
  const today = new Date().toISOString().split("T")[0];
  moodHistory[today] = mood;

  try {
    await fetch(`${API}/mood`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        studentId,
        mood
      })
    });
  } catch (err) {
    console.error("Mood save failed");
  }

  loadCalendar();
  showSection("calendar");
}

/* ============================
   CALENDAR (FULL MONTH)
============================ */

function loadCalendar() {
  const calendar = document.getElementById("calendar");
  const label = document.getElementById("monthLabel");

  calendar.innerHTML = "";
  selectedDateMood.innerText = "";

  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  const monthNames = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
  ];

  label.innerText = `${monthNames[currentMonth]} ${currentYear}`;

  // Empty slots before first day
  for (let i = 0; i < firstDay; i++) {
    const empty = document.createElement("div");
    empty.className = "day empty";
    calendar.appendChild(empty);
  }

  // Actual days
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    const cell = document.createElement("div");
    cell.className = "day";
    cell.innerText = day;

    // Today highlight
    const today = new Date();
    if (
      day === today.getDate() &&
      currentMonth === today.getMonth() &&
      currentYear === today.getFullYear()
    ) {
      cell.classList.add("today");
    }

    // Mood color
    if (moodHistory[dateStr]) {
      cell.classList.add(moodHistory[dateStr]);
    }

    // Click event
    cell.onclick = () => {
      selectedDateMood.innerText = moodHistory[dateStr]
        ? `Mood on ${dateStr}: ${moodHistory[dateStr]}`
        : `No mood recorded on ${dateStr}`;
    };

    calendar.appendChild(cell);
  }
}

/* ============================
   MONTH NAVIGATION
============================ */

function changeMonth(direction) {
  currentMonth += direction;

  if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  } else if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  }

  loadCalendar();
}
