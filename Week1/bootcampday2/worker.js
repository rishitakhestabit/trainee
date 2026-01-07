const { parentPort, workerData } = require("worker_threads")

const text = workerData.text
const minlen = workerData.minlen

const words = text
  .toLowerCase()
  .split(/\W+/)
  .filter(w => w.length >= minlen)

const freq = {}
let longest = ""
let shortest = words[0] || ""

for (const word of words) {
  freq[word] = (freq[word] || 0) + 1
  if (word.length > longest.length) longest = word
  if (word.length < shortest.length) shortest = word
}

parentPort.postMessage({
  freq,
  longest,
  shortest,
  count: words.length
})
