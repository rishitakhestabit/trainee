# Bootcamp Day 1 — System Reverse Engineering & Node Runtime Inspection

## Objective
Inspect the system and Node runtime using only the terminal. Focus was on understanding the execution environment and measuring behavior, not building features.

---

## Work Done

### 1. System Inspection
Collected system-level details directly from the terminal.

Captured:
- OS version
- Active shell
- Node binary location
- Global npm installation path
- PATH entries related to Node and npm

Deliverable:
- `system-report.md`

---

### 2. Node Version Management
Set up Node version control using NVM.

Actions:
- Installed NVM
- Switched between LTS and latest Node versions
- Verified active versions via CLI

---

### 3. System Introspection Script
Created a Node script to extract runtime and system information programmatically.

Script outputs:
- OS and architecture
- CPU core count
- Total memory
- System uptime
- Logged-in user
- Node binary path

Deliverable:
- `introspect.js`

---

### 4. Stream vs Buffer Benchmark
Compared memory and execution behavior of two file-reading approaches.

Steps:
- Generated a large test file
- Read the file using:
  - `fs.readFile` (buffer-based)
  - `fs.createReadStream` (stream-based)
- Measured execution time and memory usage

Deliverables:
- `large-file.txt`
- `perf-test.js`
- `logs/day1-perf.json`

---

## Notes
All tasks were executed without using a GUI.  
Work was committed incrementally with meaningful commit messages.
