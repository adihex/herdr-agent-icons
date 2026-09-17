# herdr-agent-icons

Per-agent logo icons in the [Herdr](https://herdr.dev) sidebar — real vector
logos, not emoji stand-ins.

Herdr's Agents sidebar renders text only, so this project takes the honest
route: the official logo SVGs are compiled into a tiny OpenType font
(`AgentIcons`) that maps each logo to a Unicode Private Use Area codepoint.
A Herdr plugin then reports that glyph as the `$icon` metadata token for each
agent pane, which shows up in the sidebar via Herdr's token-row layout.

Emoji fallbacks keep working on machines without the font installed.

## Install

```bash
# 1. Install the plugin (prebuilt font ships in the repo — no build needed)
herdr plugin install adihex/herdr-agent-icons

# 2. Install the logo font for your OS, then restart your terminal
herdr plugin action invoke local.agent-icons.install-font

# 3. Add the $icon token to your sidebar layout (~/.config/herdr/config.toml)
```

For local development, use `herdr plugin link /path/to/checkout` instead.
To rebuild the font yourself: `uv run tools/build-font.py` (or `pip install
fonttools` + `python3 tools/build-font.py`).

```toml
[ui.sidebar.agents]
rows = [
  ["state_icon", "machine", "workspace", "tab"],
  ["$icon", "agent"],
]
```

```bash
herdr server reload-config
```

The plugin's startup hook spawns a reporter loop that reports each pane's icon
every 15s. Trigger manually anytime:

```bash
herdr plugin action invoke local.agent-icons.refresh
```

## Extending

Everything is data-driven — `icons.conf` maps a Herdr agent id to an icon:

```text
devin   @devin      # @name = glyph from logos/name.svg via the font
letta   🧠          # literal fallback (emoji, nerd-font glyph, letter)
```

### Add your agent's logo (local, no font rebuild)

Put any literal glyph — emoji, nerd-font char, letter — on the right side of
`icons.conf`:

```text
myagent   🔥
```

Find the canonical agent id with `herdr agent list` (the `agent` field), then
run `herdr plugin action invoke local.agent-icons.refresh`.

### Add a real vector logo

1. Get the agent's canonical id (`herdr agent list`).
2. Drop the official SVG into `logos/<name>.svg` — monochrome/single-color
   sources render best at one terminal cell. Good sources: the vendor's
   `favicon.svg`, [Simple Icons](https://simpleicons.org),
   [LobeHub Icons](https://github.com/lobehub/lobe-icons).
3. Rebuild the font: `uv run tools/build-font.py`. This assigns the next free
   private-use codepoint (`U+100000+`, above the Nerd Font range) and updates
   `build/AgentIcons.otf` + `build/codepoints.tsv`.
4. Reference it in `icons.conf`: `<agent-id>  @<name>` (the `@name` matches
   the SVG filename).
5. Reinstall the font (`sh install-font.sh`), restart your terminal, refresh.

### Contributing a logo upstream

PRs welcome — include **all four** so installs stay zero-build for users:

- `logos/<name>.svg` (official vector; note the source in the PR)
- the `icons.conf` line
- regenerated `build/AgentIcons.otf`
- regenerated `build/codepoints.tsv`

Codepoints are assigned in sorted filename order, so rebuild rather than
hand-editing `codepoints.tsv`.

## Marketplace

This plugin is listed in the Herdr marketplace automatically: the index
discovers public GitHub repos tagged `herdr-plugin` that contain a parseable
`herdr-plugin.toml`. Listing refreshes roughly every 30 minutes — no
submission step.

## Files

| path                  | purpose                                        |
|-----------------------|------------------------------------------------|
| `herdr-plugin.toml`   | plugin manifest (startup hook + refresh action)|
| `icons.conf`          | agent id → icon mapping (edit this)            |
| `icons.sh`            | conf → glyph resolver                          |
| `report-once.sh`      | reports `$icon` for every agent pane           |
| `run.sh`              | startup hook: spawns the reporter loop         |
| `install-font.sh`     | installs AgentIcons.otf + rebuilds font cache  |
| `logos/*.svg`         | source vector logos                            |
| `tools/build-font.py` | SVGs → `build/AgentIcons.otf` + codepoints.tsv |

## How it works

- Herdr sidebar rows are token lists (`state_icon`, `agent`, `$custom`, …).
- `$icon` is a custom token fed by `herdr pane report-metadata <pane> --token icon=<char>`.
- `<char>` is a PUA codepoint; the installed AgentIcons font draws the logo.
- Without the font, the codepoint renders as a blank/□ — set an emoji in
  `icons.conf` instead if you don't want the font.

## Logo sources

Vendor/mark sources: Devin (devin.ai favicon), Droid (factory.ai favicon),
others via [Simple Icons](https://simpleicons.org) and
[LobeHub Icons](https://github.com/lobehub/lobe-icons). Trademarks belong to
their owners; logos are used here for identification only.

## License

MIT (code). Logos remain the property of their respective owners.
