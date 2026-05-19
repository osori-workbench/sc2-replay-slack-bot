#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/osori/workbench/sc2-replay-slack-bot"
AGENT_DIR="$HOME/Library/LaunchAgents"
LABEL="com.osori.sc2-replay-slack-bot"
SRC_PLIST="$PROJECT_DIR/deploy/launchd/$LABEL.plist"
DST_PLIST="$AGENT_DIR/$LABEL.plist"

mkdir -p "$AGENT_DIR" "$PROJECT_DIR/logs" "$PROJECT_DIR/state"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$DST_PLIST"
cp "$SRC_PLIST" "$DST_PLIST"
launchctl bootstrap "gui/$(id -u)" "$DST_PLIST"
launchctl enable "gui/$(id -u)/$LABEL"
launchctl print "gui/$(id -u)/$LABEL" >/dev/null

echo "Installed $LABEL"
