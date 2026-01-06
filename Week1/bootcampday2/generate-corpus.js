const fs = require("fs");

const lorem = `lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua`;

const TARGET_WORDS = 200000;
let words = [];

while (words.length < TARGET_WORDS) {
  words.push(...lorem.split(" "));
}

const finalText = words.slice(0, TARGET_WORDS).join(" ");

fs.writeFileSync("corpus.txt", finalText);

console.log("corpus.txt created with", TARGET_WORDS, "words");
