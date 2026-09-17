# Icon lookup: resolves icons.conf entries against build/codepoints.tsv.
# Sourced by report-once.sh. Requires ICONS_DIR to be set by the caller.

icon_for_agent() {
  # $1 = agent id -> prints glyph (may be empty)
  entry="$(awk -v id="$1" 'BEGIN{FS="[ \t]+"} $1==id{print $2}' "$ICONS_DIR/icons.conf")"
  case "$entry" in
    @*) logo="${entry#@}"
        awk -v l="$logo" 'BEGIN{FS="\t"} $1==l{printf "%s",$2}' "$ICONS_DIR/build/codepoints.tsv" 2>/dev/null ;;
    *)  printf '%s' "$entry" ;;
  esac
}
