const fs = require("fs")
const path = require("path")

const args = process.argv.slice(2)

function get_arg(key) {
  const index = args.indexOf(key)
  return index !== -1 ? args[index + 1] : null
}

const file = get_arg("--file")
const top = Number(get_arg("--top")) || 10
const minlen = Number(get_arg("--minLen")) || 1
const unique = args.includes("--unique")

function process_chunk(text, minlen) {
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

  return {
    freq,
    longest,
    shortest,
    count: words.length
  }
}

async function process_file_concurrent(filepath, minlen, concurrency) {
  const data = fs.readFileSync(filepath, "utf8")
  const size = Math.ceil(data.length / concurrency)
  const chunks = []

  for (let i = 0; i < concurrency; i++) {
    chunks.push(data.slice(i * size, (i + 1) * size))
  }

  const results = await Promise.all(
    chunks.map(chunk =>
      Promise.resolve(process_chunk(chunk, minlen))
    )
  )

  return results
}

function merge_results(results) {
  const final_freq = {}
  let total_words = 0
  let longest = ""
  let shortest = ""

  for (const res of results) {
    total_words += res.count

    if (res.longest.length > longest.length) longest = res.longest
    if (!shortest || res.shortest.length < shortest.length) shortest = res.shortest

    for (const word in res.freq) {
      final_freq[word] = (final_freq[word] || 0) + res.freq[word]
    }
  }

  return { final_freq, total_words, longest, shortest }
}

async function run(concurrency) {
  const start = Date.now()

  const results = await process_file_concurrent(file, minlen, concurrency)
  const merged = merge_results(results)

  const top_words = Object.entries(merged.final_freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, top)

  const result = {
    total_words: merged.total_words,
    unique_words: unique ? Object.keys(merged.final_freq).length : undefined,
    longest_word: merged.longest,
    shortest_word: merged.shortest,
    top_words
  }

  const duration = Date.now() - start
  return { result, duration }
}

async function main() {
  if (!file) {
    console.error("file is required")
    process.exit(1)
  }

  if (!fs.existsSync("output")) fs.mkdirSync("output")
  if (!fs.existsSync("logs")) fs.mkdirSync("logs")

  const summary = {}

  for (const concurrency of [1, 4, 8]) {
    const { result, duration } = await run(concurrency)

    summary[`concurrency_${concurrency}`] = {
      duration_ms: duration
    }

    if (concurrency === 1) {
      fs.writeFileSync(
        "output/stats.json",
        JSON.stringify(result, null, 2)
      )

      console.log(JSON.stringify(result, null, 2))
    }
  }

  fs.writeFileSync(
    "logs/perf-summary.json",
    JSON.stringify(summary, null, 2)
  )
}

main()

