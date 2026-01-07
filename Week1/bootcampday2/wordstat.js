const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);

const get_arg = (key) => {
  const index = args.indexOf(key);
  return index !== -1 ? args[index + 1] : null;
};

const file = get_arg("--file");
const top = Number(get_arg("--top")) || 10;
const min_len = Number(get_arg("--minLen")) || 0;
const unique_flag = args.includes("--unique");

if (!file) {
  console.error("file not provided");
  process.exit(1);
}

const file_path = path.resolve(file);
const data = fs.readFileSync(file_path, "utf-8");

const words = data
  .toLowerCase()
  .split(/\s+/)
  .filter(w => w.length >= min_len);

const total_words = words.length;

const freq = {};
for (const w of words) {
  freq[w] = (freq[w] || 0) + 1;
}

const unique_words = Object.keys(freq).length;

const sorted_words = Object.entries(freq).sort((a, b) => b[1] - a[1]);
const top_words = sorted_words.slice(0, top);

let longest_word = "";
let shortest_word = words[0] || "";

for (const w of words) {
  if (w.length > longest_word.length) longest_word = w;
  if (w.length < shortest_word.length) shortest_word = w;
}

const result = {
  total_words,
  unique_words: unique_flag ? unique_words : undefined,
  longest_word,
  shortest_word,
  top_words
};

fs.writeFileSync(
  "output/stats.json",
  JSON.stringify(result, null, 2)
)

console.log(JSON.stringify(result, null, 2));

