# palworld-breed

Claude Code plugin for Palworld breeding paths. Also packageable for Claude Cowork.

## Install

From the marketplace in this repo:

```
/plugin marketplace add jongmyung/palworld-bleed
/plugin install palworld-breed@palworld-bleed
```

Then use natural language, `/breed-path`, or `/breed-refresh`. See the [repo README](../README.md#installation) for local-dev and Cowork options. Python 3 stdlib only — no dependencies.

## Commands (engine, `scripts/palbreed.py`)
- `path <start> <target> [--easy-partners]`
- `transfer <holder> <target> [--own a,b,c] [--easy-partners]`
- `make <target> [--easiest] [--limit N]`
- `whatis <A> <B>`
- `refresh` (network; regenerates `data/`)
- `resolve <name>`

Add `--json` to any query command for machine output.

## Data
`data/` is bundled. Regenerate with `/breed-refresh` (needs network access to
palworldbreed.com). On a VM without outbound access, run `refresh` locally and
redistribute the updated `data/`.

## Tests
`python3 -m unittest discover -s scripts/tests -v`
