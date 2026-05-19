#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/osori/workbench/sc2-replay-slack-bot"
ENV_FILE="$PROJECT_DIR/.env"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/launchd.log"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

mkdir -p "$LOG_DIR" "$PROJECT_DIR/state"
cd "$PROJECT_DIR"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

unset VIRTUAL_ENV
export PYTHONPATH="$PROJECT_DIR/src"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting replay scan"
  "$PYTHON_BIN" -m sc2_replay_slack_bot.app --max-files 20
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished replay scan"
} >> "$LOG_FILE" 2>&1
