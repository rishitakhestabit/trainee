#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/validate.log"

mkdir -p "$LOG_DIR"

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log() {
  echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

log "Running validation..."

if [ ! -d "$ROOT_DIR/src" ]; then
  log "ERROR: src/ directory missing"
  exit 1
fi

if [ ! -f "$ROOT_DIR/config.json" ]; then
  log "ERROR: config.json missing"
  exit 1
fi

if ! jq empty "$ROOT_DIR/config.json" >/dev/null 2>&1; then
  log "ERROR: Invalid JSON in config.json"
  exit 1
fi

log "Validation successful"
