const API = "http://localhost:7071/api";
let resolvedToday = 0;

function logout() {
  localStorage.clear();
  location.href = "../auth/index.html";
}

async function loadAlerts() {
  try {
    const res    = await fetch(`${API}/counsellor/alerts`);
    const alerts = await res.json();
    const high   = alerts.filter(a => a.level === "HIGH").length;
    document.getElementById("pendingCount").textContent  = high;
    document.getElementById("totalCount").textContent    = alerts.length;
    document.getElementById("resolvedCount").textContent = resolvedToday;
    const container = document.getElementById("alertsContainer");
    container.innerHTML = alerts.length === 0
      ? "<p>No active alerts. \u2705</p>"
      : alerts.map(a => `
          <div class="alert" id="alert-${a.id}">
            <span class="badge">HIGH RISK</span>
            <p>Student: <strong>${a.studentId}</strong> &bull; ${new Date(a.time).toLocaleString()}</p>
            <p>"${a.message}"</p>
            <button onclick="resolveAlert('${a.id}')">Mark Resolved</button>
          </div>`).join("");
  } catch {
    document.getElementById("alertsContainer").innerHTML =
      "<p>Could not load alerts. Is the backend running?</p>";
  }
}

async function resolveAlert(id) {
  const res = await fetch(`${API}/counsellor/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id })
  });
  if (!res.ok) return alert("Failed to resolve alert.");
  const el = document.getElementById(`alert-${id}`);
  if (el) el.remove();
  resolvedToday++;
  document.getElementById("resolvedCount").textContent = resolvedToday;
  const remaining = document.querySelectorAll("#alertsContainer .alert").length;
  document.getElementById("totalCount").textContent   = remaining;
  document.getElementById("pendingCount").textContent = remaining;
  if (remaining === 0)
    document.getElementById("alertsContainer").innerHTML = "<p>No active alerts. \u2705</p>";
}

window.addEventListener("DOMContentLoaded", () => {
  const u     = JSON.parse(localStorage.getItem("user") || "{}");
  const label = document.getElementById("userLabel");
  if (label) label.innerHTML = `SIGNED IN AS<br><span>${u.name || u.email || ""}</span>`;
  loadAlerts();
});
