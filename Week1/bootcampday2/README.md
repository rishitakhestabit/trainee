# Bootcamp Day 2 – Node.js CLI & Concurrency

## Overview
This task focuses on building a Node.js CLI tool to process large text data,
apply concurrency, and benchmark performance.

## Features
- Generates 200k+ word corpus
- CLI-based word statistics
- Concurrent processing (1, 4, 8)
- Performance benchmarking

## Run Command
```bash
node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique
