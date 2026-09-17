#!/bin/sh
# Report the $icon token for every known agent pane. Idempotent.
set -u
cd "$(dirname "$0")"
ICONS_DIR="$PWD"
. ./icons.sh

HERDR="${HERDR_BIN_PATH:-herdr}"

"$HERDR" agent list | jq -r '.result.agents[] | [.pane_id, .agent] | @tsv' |
while IFS="$(printf '\t')" read -r pane_id agent; do
  icon="$(icon_for_agent "$agent")"
  [ -n "$icon" ] || continue
  "$HERDR" pane report-metadata "$pane_id" \
    --source agent-icons \
    --token "icon=$icon" >/dev/null 2>&1 || true
done
