const API = "http://127.0.0.1:7071/api";

/* =============================
   LOAD DASHBOARD DATA
============================= */

async function loadDashboard() {
  await loadAlerts();

  /* These can later come from backend APIs */
  totalStudents.innerText = "–";
  stressedToday.innerText = "–";
  criticalAlerts.innerText = alertTable.children.length;
  avgMood.innerText = "–";
}

/* =============================
   LOAD RISK ALERTS (REAL DATA)
============================= */

async function loadAlerts() {
  try {
    const res = await fetch(`${API}/counsellor/alerts`);
    const alerts = await res.json();

    alertTable.innerHTML = "";

    alerts.forEach(alert => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${alert.studentId}</td>
        <td>${alert.riskLevel}</td>
        <td>${alert.reason}</td>
        <td>${new Date(alert.detectedAt).toLocaleString()}</td>
      `;
      alertTable.appendChild(row);
    });

  } catch (err) {
    console.error("Failed to load alerts", err);
  }
}

/* =============================
   MOCK STUDENT & TREND DATA
   (Replace later with APIs)
============================= */

function loadMockStats() {
  happyCount.innerText = 42;
  okayCount.innerText = 55;
  sadCount.innerText = 28;
  stressedCount.innerText = 19;

  studentTable.innerHTML = `
    <tr>
      <td>S102</td>
      <td>Stressed</td>
      <td>High</td>
      <td>2026-01-04</td>
    </tr>
    <tr>
      <td>S087</td>
      <td>Low</td>
      <td>Medium</td>
      <td>2026-01-04</td>
    </tr>
  `;
}

/* =============================
   INIT
============================= */

loadDashboard();
loadMockStats();
