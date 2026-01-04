// Load today's mood on dashboard
async function loadTodayMood() {
  const studentId = localStorage.studentId;
  if (!studentId) return;

  const res = await fetch(
    `http://127.0.0.1:7072/api/moods?studentId=${studentId}`
  );
  const moods = await res.json();

  const today = new Date().toISOString().split("T")[0];
  const todayEntry = moods.find(m => m.date === today);

  const moodText = todayEntry ? todayEntry.mood : "Not set";
  const el = document.getElementById("todayMood");
  if (el) el.innerText = moodText;
}

loadTodayMood();
