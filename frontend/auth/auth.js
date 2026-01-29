function showLogin(){
  loginBox.classList.remove("hidden");
  registerBox.classList.add("hidden");
}
function showRegister(){
  registerBox.classList.remove("hidden");
  loginBox.classList.add("hidden");
}
function login(){
  const role="student"; 
  if(role==="counsellor") location.href="../counsellor/dashboard.html";
  else location.href="../student/dashboard.html";
}
