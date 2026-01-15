const todoinput = document.getElementById("todoinput");
const addbtn = document.getElementById("addbtn");
const todolist = document.getElementById("todolist");

let todos = [];

function savetodos() {
  localStorage.setItem("todos", JSON.stringify(todos));
}

function loadtodos() {
  const data = localStorage.getItem("todos");
  if (data) {
    todos = JSON.parse(data);
  }
}

function rendertodos() {
  todolist.innerHTML = "";

  for (let i = 0; i < todos.length; i++) {
    const li = document.createElement("li");
    li.className = "todoitem";

    const text = document.createElement("span");
    text.textContent = todos[i];

    const actions = document.createElement("div");
    actions.className = "todoactions";

    const editbtn = document.createElement("button");
    editbtn.textContent = "edit";

    const deletebtn = document.createElement("button");
    deletebtn.textContent = "delete";

    editbtn.addEventListener("click", () => {
      const updated = prompt("edit task", todos[i]);
      if (updated) {
        todos[i] = updated;
        savetodos();
        rendertodos();
      }
    });

    deletebtn.addEventListener("click", () => {
      todos.splice(i, 1);
      savetodos();
      rendertodos();
    });

    actions.appendChild(editbtn);
    actions.appendChild(deletebtn);

    li.appendChild(text);
    li.appendChild(actions);

    todolist.appendChild(li);
  }
}

addbtn.addEventListener("click", () => {
  const value = todoinput.value.trim();
  if (!value) return;

  todos.push(value);
  todoinput.value = "";
  savetodos();
  rendertodos();
});

try {
  loadtodos();
  rendertodos();
} catch (error) {
  console.error("can't fetch todo");
  console.error(error);
}
