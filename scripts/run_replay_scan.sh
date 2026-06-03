#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/osori/workbench/sc2-replay-slack-bot"
ENV_FILE="$PROJECT_DIR/.env"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/launchd.log"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
SCAN_INTERVAL_SEC="${SCAN_INTERVAL_SEC:-60}"

mkdir -p "$LOG_DIR" "$PROJECT_DIR/state"
cd "$PROJECT_DIR"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

unset VIRTUAL_ENV
export PYTHONPATH="$PROJECT_DIR/src"

shutdown_requested=0
on_term() {
  shutdown_requested=1
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Received termination signal; stopping replay worker" >> "$LOG_FILE"
}
trap on_term TERM INT

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

if [ ! -x "$PYTHON_BIN" ]; then
  log "Missing python interpreter at $PYTHON_BIN"
  exit 1
fi

log "Replay worker booted (interval=${SCAN_INTERVAL_SEC}s)"

while true; do
  scan_output=$("$PYTHON_BIN" -m sc2_replay_slack_bot.app --max-files 20 2>&1) || {
    printf '%s\n' "$scan_output" >> "$LOG_FILE"
    log "Replay scan exited non-zero"
  }

  if [ -n "${scan_output:-}" ] && [ "$scan_output" != "[]" ]; then
    printf '%s\n' "$scan_output" >> "$LOG_FILE"
  fi

  if [ "$shutdown_requested" -eq 1 ]; then
    log "Replay worker stopped"
    exit 0
  fi

  sleep "$SCAN_INTERVAL_SEC" &
  wait $! || true

  if [ "$shutdown_requested" -eq 1 ]; then
    log "Replay worker stopped"
    exit 0
  fi
done
