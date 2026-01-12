# WEEK1-RETRO.md

## Week 1 Retrospective — Engineering Bootcamp

This document summarizes the work I completed during Week 1, what I learned from each day, what broke during execution, and how I resolved those issues.

---

## Day 1 — System Reverse Engineering & Terminal Usage

### What I Did
- Inspected system details using terminal only (OS, shell, PATH, Node, npm)
- Installed and used NVM to switch Node versions
- Wrote `introspect.js` to extract system-level information
- Benchmarked file reading using buffer vs stream on large files

### What Broke
- Initial assumptions about memory usage were incorrect
- Buffer-based file reads consumed excessive memory on large files

### How I Fixed It
- Re-ran benchmarks with proper logging
- Compared memory and execution time outputs
- Validated results using multiple runs

### Outcome
- Understood why streams are preferable for large file operations
- Gained clarity on how Node interacts with system resources

---

## Day 2 — Node CLI, Concurrency, Large File Processing

### What I Did
- Built a CLI tool to process a large text corpus (200k+ words)
- Implemented word statistics (total, unique, frequency, min/max length)
- Added concurrency using chunk-based processing
- Benchmarked execution with different concurrency levels

### What Broke
- Early versions were slow and inefficient
- Logic errors appeared when filtering words and counting uniqueness

### How I Fixed It
- Refactored logic into smaller, testable units
- Logged performance results instead of relying on assumptions
- Tuned concurrency after measuring actual runtime

### Outcome
- Learned how concurrency affects performance in practice
- Understood trade-offs between speed, memory, and complexity

---

## Day 3 — Git Recovery & Advanced Workflows

### What I Did
- Created a repository with intentional bugs
- Used `git bisect` to locate the faulty commit
- Fixed the bug using `git revert`
- Practiced stash workflows and conflict resolution across two clones

### What Broke
- Conflicts occurred when modifying the same lines across branches
- Early instinct was to use reset instead of revert

### How I Fixed It
- Used revert to preserve history
- Resolved merge conflicts manually while keeping both changes
- Documented bisect and stash sessions

### Outcome
- Improved ability to recover from mistakes safely
- Gained confidence using Git as a debugging tool

---

## Day 4 — HTTP and API Investigation

### What I Did
- Performed DNS lookup and traceroute
- Used curl to inspect HTTP requests and responses
- Tested header manipulation and authorization behavior
- Verified caching behavior using ETag and conditional requests
- Built a Node server with echo, delay, and cache endpoints

### What Broke
- Some header behaviors were unclear initially
- Required multiple iterations to observe correct caching behavior

### How I Fixed It
- Compared raw curl outputs
- Re-tested with controlled header changes
- Documented observations clearly

### Outcome
- Better understanding of HTTP headers, caching, and request flow

---

## Day 5 — Automation and Mini CI Pipeline

### What I Did
- Wrote `validate.sh` to enforce project structure and config validity
- Added ESLint and Prettier to block bad commits
- Integrated Husky pre-commit hooks
- Created timestamped build artifacts with checksums
- Scheduled validation using cron

### What Broke
- Script execution failed due to a trailing space in filename
- Invalid JSON blocked commits (expected behavior)
- Encountered nested Git repository issues

### How I Fixed It
- Renamed files correctly
- Validated both failing and passing commit paths
- Removed inner `.git` and followed clean repo structure

### Outcome
- Established automated safeguards against bad commits
- Improved reliability and reproducibility of the workflow

---

## Overall Learnings
- Measure before optimizing
- Automate checks instead of relying on manual discipline
- Use Git recovery tools instead of rewriting history
- Validate assumptions with logs and evidence

