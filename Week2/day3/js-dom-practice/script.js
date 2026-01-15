const menubtn = document.getElementById("menubtn");
const menulist = document.getElementById("menulist");

menubtn.addEventListener("click", () => {
  menulist.classList.toggle("hidden");
});

const faqitems = document.querySelectorAll(".faqitem");

for (let i = 0; i < faqitems.length; i++) {
  const question = faqitems[i].querySelector(".faqques");
  const icon = faqitems[i].querySelector(".icon");

  question.addEventListener("click", () => {
    for (let j = 0; j < faqitems.length; j++) {
      if (j !== i) {
        faqitems[j].classList.remove("active");
        faqitems[j].querySelector(".icon").textContent = "+";
      }
    }

    faqitems[i].classList.toggle("active");
    icon.textContent = faqitems[i].classList.contains("active") ? "-" : "+";
  });
}

let level = 1;
const difficultylabel = document.getElementById("difficultylabel");

function updatedifficulty() {
  if (level === 1) difficultylabel.textContent = "easy";
  if (level === 2) difficultylabel.textContent = "moderate";
  if (level === 3) difficultylabel.textContent = "difficult";
}

document.addEventListener("keydown", e => {
  if (e.key === "ArrowUp" && level < 3) level++;
  if (e.key === "ArrowDown" && level > 1) level--;
  if (e.key === "1") level = 1;
  if (e.key === "2") level = 2;
  if (e.key === "3") level = 3;
  updatedifficulty();
});

updatedifficulty();
