# Bootcamp Day 5 — Automation & Mini CI Pipeline

## Objective
The purpose of this day was to understand why automation is required in real projects and how small automated checks can prevent broken code from entering a repository. The work focused on building a lightweight, local CI-style setup using shell scripts, linters, Git hooks, and scheduled jobs.

---

## Project Structure
The project was structured to clearly separate concerns and make automation easier to manage.

- `src/`  
  This directory contains the application source code. All validation and linting checks are run against this folder to ensure only correct and clean code is committed.

- `scripts/`  
  This directory holds automation scripts. Keeping scripts separate allows them to be reused in hooks, cron jobs, and manual runs.

- `logs/`  
  This directory stores execution logs from validation scripts and scheduled runs. Logs provide traceability and help debug failures without rerunning commands.

- `artifacts/`  
  This directory contains packaged build outputs. Artifacts represent a snapshot of the project at a specific point in time and can be shared or archived.

---

## Validation Script (`validate.sh`)
The validation script acts as the first line of defense before code is accepted.

**Purpose:**  
To verify that the project is in a valid state before commits or scheduled runs.

**What it checks:**
- Confirms the `src/` directory exists to ensure source code is present
- Validates `config.json` to prevent malformed configuration from breaking the application
- Appends timestamped entries to a log file for auditability

**Why it matters:**  
Failing fast during validation avoids broken builds and saves debugging time later. The script exits with a non-zero status on failure so it can be reliably used in automation.

---

## Linting and Formatting (ESLint & Prettier)
Static analysis and formatting tools were added to enforce consistent and correct code.

**ESLint**
- **Purpose:** Detect logical errors, bad patterns, and potential bugs
- **Why:** Catches issues early that may not fail at runtime but cause long-term maintenance problems

**Prettier**
- **Purpose:** Enforce consistent code formatting
- **Why:** Eliminates style discussions and ensures readable, uniform code across the project

Both tools are run automatically and can block commits if rules are violated.

---

## Pre-Commit Hook with Husky
Husky was used to integrate automation directly into the Git workflow.

**Purpose:**  
To prevent invalid or poorly formatted code from ever being committed.

**What runs on every commit:**
1. ESLint checks on source files
2. Prettier formatting validation
3. Execution of `validate.sh`

**Why this matters:**  
Developers get immediate feedback before a commit is created, which keeps the repository history clean and reduces future rollbacks.

---

## Build Artifact Creation
A build artifact was generated using a timestamp-based naming convention.

**Purpose:**  
To package the project state into a single, reproducible archive.

**What is included:**
- Source code
- Automation scripts
- Logs
- Configuration and linting files

A SHA-256 checksum is generated alongside the archive to verify integrity.

**Why it matters:**  
Artifacts allow teams to reproduce builds, verify contents, and ensure the package has not been modified after creation.

---

## Scheduled Execution Using Cron
The validation script was scheduled using `cron`.

**Purpose:**  
To ensure validation runs automatically at regular intervals without manual intervention.

**Why scheduling is useful:**
- Detects issues even when no commits are being made
- Generates continuous logs for monitoring
- Simulates how CI systems run checks on a schedule or trigger

---

## Issues Encountered and Resolutions
- Script execution failed due to an incorrect filename caused by a trailing space, which was fixed by renaming
- Invalid `config.json` correctly blocked commits, validating the effectiveness of the safeguards
- File permissions were updated to ensure scripts were executable
- Hook paths were corrected to ensure commands resolved correctly in non-interactive environments

---
