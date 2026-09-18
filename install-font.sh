#!/bin/sh
# Install the prebuilt AgentIcons font for the current OS, then rebuild caches.
set -eu
cd "$(dirname "$0")"
SRC="build/AgentIcons.otf"
[ -f "$SRC" ] || SRC="$(find . -name 'AgentIcons.otf' | head -1)"
[ -n "$SRC" ] && [ -f "$SRC" ] || { echo "AgentIcons.otf not found; run: uv run tools/build-font.py"; exit 1; }

case "$(uname -s)" in
  Darwin)
    cp "$SRC" ~/Library/Fonts/AgentIcons.otf
    atsutil databases -remove 2>/dev/null || true
    echo "installed to ~/Library/Fonts — fully quit the terminal app (Cmd+Q) and reopen it"
    ;;
  Linux)
    mkdir -p ~/.local/share/fonts
    cp "$SRC" ~/.local/share/fonts/AgentIcons.otf
    fc-cache -f >/dev/null 2>&1 || true
    echo "installed to ~/.local/share/fonts — fully quit the terminal app and reopen it"
    ;;
  *)
    echo "unsupported OS — copy $SRC into your font directory manually"; exit 1 ;;
esac
