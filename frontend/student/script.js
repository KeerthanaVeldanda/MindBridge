const API = "http://127.0.0.1:7072/api";
const studentId = localStorage.studentId;

/* CHAT */
async function send(){
  chat.innerHTML += `<p><b>You:</b> ${msg.value}</p>`;
  const r = await fetch(API+"/chat",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({studentId,message:msg.value})
  });
  const d = await r.json();
  chat.innerHTML += `<p><b>MindBridge:</b> ${d.reply}</p>`;
  msg.value="";
}

/* MOOD */
async function setMood(mood){
  await fetch(API+"/mood",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({studentId,mood})
  });
  if(status) status.innerText="Mood saved 💜";
}

/* CALENDAR */
async function loadCalendar(){
  const r = await fetch(API+"/moods?studentId="+studentId);
  const d = await r.json();
  calendar.innerHTML = d.map(m =>
    `<p>${m.date} – ${m.mood}</p>`
  ).join("");
}
if(typeof calendar!=="undefined") loadCalendar();
