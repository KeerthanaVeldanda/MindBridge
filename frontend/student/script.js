const API = "http://127.0.0.1:7072/api";
const studentId = localStorage.getItem("studentId");
document.getElementById("studentName")?.innerText =
  localStorage.getItem("studentName");

function sendMessage() {
  const msg = textInput.value;
  textInput.value = "";
  chatBox.innerHTML += `<div class="message user">${msg}</div>`;

  fetch(`${API}/chat`, {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body:JSON.stringify({ studentId, message: msg })
  }).then(r=>r.json()).then(d=>{
    chatBox.innerHTML += `<div class="message bot">${d.reply}</div>`;
  });
}

function saveMood(mood) {
  fetch(`${API}/mood`, {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body:JSON.stringify({ studentId, mood })
  }).then(()=>alert("Mood saved 💜"));
}
