#!/bin/sh
# Startup hook: spawn the icon reporter loop (deduped via pidfile), then exit.
set -u
cd "$(dirname "$0")"

PIDFILE="${HERDR_PLUGIN_STATE_DIR:-/tmp}/agent-icons.pid"
SOCK="${HERDR_SOCKET_PATH:-}"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  exit 0
fi

nohup sh -c '
  cd "'"$PWD"'"
  HERDR_BIN_PATH="'"${HERDR_BIN_PATH:-herdr}"'"
  export HERDR_BIN_PATH
  while :; do
    HERDR_SOCKET_PATH="'"$SOCK"'" sh report-once.sh
    sleep 15
  done
' >/dev/null 2>&1 &
echo $! > "$PIDFILE"
