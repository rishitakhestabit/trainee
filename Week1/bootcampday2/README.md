# Bootcamp Day 2 — Node CLI, Concurrency, and Large File Processing

## Objective
Process large text data using Node.js, build a CLI tool, and measure the impact of concurrency on performance.

---

## Work Done

### 1. Corpus Generation
Generated a large text corpus for processing and benchmarking.

Files:
- `corpus.txt`
- `generate-corpus.js`

The corpus contains over 200,000 words and is used as input for all further tasks.

---

### 2. CLI Tool — `wordstat.js`
Built a Node-based CLI tool to analyze word statistics from a large text file.

Command format:
```bash
node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique
```

Computed metrics:

    Total word count

    Unique word count

    Longest and shortest words

    Top N most frequent words

Output:

    Printed to terminal

    Persisted to output/stats.json

3. Concurrent Processing

Improved processing speed by parallelizing work.

Implementation:

    Split the corpus into chunks

    Process chunks concurrently using:

        Promise.all

        worker_threads (worker.js)

This allowed scaling computation with CPU cores instead of sequential execution.
4. Performance Benchmarking

Measured execution time across different concurrency levels.

Tested concurrency:

    1 (single-threaded)

    4

    8

Results recorded in:

    logs/perf-summary.json
