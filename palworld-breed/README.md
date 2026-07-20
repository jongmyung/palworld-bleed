# palworld-breed

Claude Code plugin for Palworld breeding paths. Also packageable for Claude Cowork.

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
