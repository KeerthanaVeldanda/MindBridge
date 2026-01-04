const API = "http://127.0.0.1:7072/api";

async function loadAlerts() {
  const res = await fetch(`${API}/counsellor/alerts`);
  const alerts = await res.json();

  const table = document.getElementById("alertTable");
  table.innerHTML = "";

  let high = 0, medium = 0, low = 0;

  alerts.forEach(a => {
    if (a.riskLevel === "HIGH") high++;
    else if (a.riskLevel === "MEDIUM") medium++;
    else low++;

    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${a.studentId}</td>
      <td class="risk-${a.riskLevel.toLowerCase()}">${a.riskLevel}</td>
      <td>${a.reason}</td>
      <td>${new Date(a.detectedAt).toLocaleString()}</td>
      <td><span class="status-new">${a.status}</span></td>
    `;

    table.appendChild(tr);
  });

  document.getElementById("highCount").innerText = high;
  document.getElementById("mediumCount").innerText = medium;
  document.getElementById("lowCount").innerText = low;
}

/* AUTO REFRESH EVERY 10s */
loadAlerts();
setInterval(loadAlerts, 10000);
