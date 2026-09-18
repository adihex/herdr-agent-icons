# Changelog

## 0.2.0 — 2026-09-17

**Added**
- Antigravity (`agy`) logo — official arch mark, monochrome.
- `install-font` plugin action: installs AgentIcons.otf per-OS and rebuilds
  the font cache.
- Prebuilt `build/AgentIcons.otf` + `build/codepoints.tsv` ship in the repo,
  so `herdr plugin install` needs no font build.

**Fixed — BREAKING for anyone who built the font locally between the agy
commit and this release**
- Codepoint assignments are now pinned in `build/codepoints.map`; adding a
  logo appends the next free slot instead of renumbering alphabetically.
  An earlier build silently renumbered every glyph, which desynced installed
  fonts from reported tokens (icons showed the wrong logo). If you built
  locally, rebuild and reinstall the font — reported codepoints are back to
  the original assignments.
- Reporter loop polls every 5s (was 15s) so new agents get icons faster.

## 0.1.0 — 2026-09-17

Initial release: `$icon` sidebar token, PUA font from official logo SVGs,
21 logos, emoji fallbacks, reporter loop via plugin startup hook.
