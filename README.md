# palworld-bleed

A [Claude Code](https://claude.com/claude-code) plugin that computes **Palworld breeding-combination paths** from a bundled dataset (88,213 combinations across 299 pals, scraped from [palworldbreed.com](https://www.palworldbreed.com)).

Ask things like "shortest path from Nitewing to Anubis", "move this passive onto Anubis using pals I own", or "what's the easiest combo for Anubis" — the plugin runs a deterministic graph search and answers with a step-by-step breeding chain.

## What it does

- **Shortest path** — fewest breeding steps from a start pal to a target pal.
- **Easy-partner path** — a path that prefers easy-to-obtain partner pals (avoids variants and late-game pals).
- **Passive-transfer path** — a relay chain that carries a passive skill from a pal you own down to a target species, preferring partners you already have.
- **Reverse lookup** — combinations that produce a target, the easiest such combo, and `A × B = ?`.

Pal names are accepted in Korean or English. Results show Korean names with English keys.

## Repository layout

```
palworld-breed/           # the plugin (install this)
├── skills/               # the palworld-breed skill (natural-language entry point)
├── commands/             # /breed-path, /breed-refresh slash commands
├── scripts/              # stdlib-only Python engine, CLI, scraper + tests
├── data/                 # bundled dataset (combos, pals, meta)
└── README.md             # plugin-level usage
docs/superpowers/         # design spec + implementation plan
```

## Installation

This repo is a Claude Code plugin marketplace ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)) hosting the `palworld-breed` plugin.

1. Add this repo as a marketplace:
   ```
   /plugin marketplace add jongmyung/palworld-bleed
   ```
2. Install the plugin:
   ```
   /plugin install palworld-breed@palworld-bleed
   ```
3. Verify it loaded (skill + `breed-path`, `breed-refresh` commands):
   ```
   /plugin
   ```

Now ask in natural language ("나이트윙에서 아누비스까지 경로") or run the slash commands (`/breed-path`, `/breed-refresh`).

**Local development** (test a cloned copy without publishing):
```
/plugin marketplace add /path/to/palworld-bleed      # local repo path
/plugin install palworld-breed@palworld-bleed
```
Or sideload for a single session: `claude --plugin-dir /path/to/palworld-bleed/palworld-breed`.

Python 3 must be on `PATH` (the engine is standard-library only — no `pip install`). Bundled scripts and data resolve via `${CLAUDE_PLUGIN_ROOT}`, so they are found automatically once installed.

## Quick start (CLI)

You can also drive the engine directly without installing the plugin:

```bash
python3 palworld-breed/scripts/palbreed.py path 나이트윙 아누비스 --json
python3 palworld-breed/scripts/palbreed.py transfer 나이트윙 아누비스 --own 큐룰리스 --easy-partners --json
python3 palworld-breed/scripts/palbreed.py make 아누비스 --easiest --limit 3 --json
python3 palworld-breed/scripts/palbreed.py whatis 불무사 펭킹 --json
```

See [palworld-breed/README.md](palworld-breed/README.md) for the full command reference.

## Data

The dataset is bundled, so all queries work offline. Regenerate it with `/breed-refresh` (or `palbreed.py refresh`), which needs outbound network access to palworldbreed.com. On an environment without egress, refresh locally and redistribute the updated `data/`.

## Tests

```bash
python3 -m unittest discover -s palworld-breed/scripts/tests -v
```

## Notes

- `--easy-partners` avoids hard *partners* but a path may still route through a variant *intermediate* pal — check the intermediates.
- Zero third-party dependencies (Python 3 standard library only).
