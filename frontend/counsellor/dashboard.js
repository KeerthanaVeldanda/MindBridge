let studentsData = [
  {
    name: "Student A",
    mood: "😔",
    note: "Feeling low for the past few days"
  },
  {
    name: "Student B",
    mood: "🤯",
    note: "Academic stress and deadlines"
  },
  {
    name: "Student C",
    mood: "😠",
    note: "Frustration and burnout signs"
  }
];

// load student list dynamically
function loadStudents() {
  let list = document.getElementById("studentList");
  list.innerHTML = "";

  studentsData.forEach((student, index) => {
    let li = document.createElement("li");
    li.innerText = student.name + " – " + student.mood;
    li.onclick = function () {
      showDetails(index);
    };
    list.appendChild(li);
  });
}

// show selected student details
function showDetails(index) {
  let student = studentsData[index];
  document.getElementById("studentDetails").innerText =
    student.name + ": " + student.note;
}

// load data when page opens
loadStudents();