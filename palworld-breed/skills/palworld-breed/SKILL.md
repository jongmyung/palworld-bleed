---
name: palworld-breed
description: Use for Palworld breeding questions — shortest breeding path between two pals, easy-to-obtain-partner paths, moving a passive skill onto a target pal, and reverse lookups (what makes X, easiest combo, A×B=?). Triggers on Palworld pal names, 교배, 조합식, 경로, 패시브 이식.
---

# Palworld Breeding Paths

Run the engine at `${CLAUDE_PLUGIN_ROOT}/scripts/palbreed.py` with Python 3 and
format its `--json` output for the user. The engine is read-only except
`refresh`.

## Intent → command

- "path from A to B" → `path A B --json` (add `--easy-partners` for "easy"/"쉬운")
- "move this passive to B, I own X,Y" → `transfer A B --own X,Y --easy-partners --json`
- "combos that make X" / "easiest combo for X" → `make X [--easiest] --json`
- "A × B = ?" → `whatis A B --json`
- "refresh" → `refresh --json`

Always call with `--json`, then render the result yourself.

## Running

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/palbreed.py" <args>`

## Name resolution

Pass Korean or English names straight through. If the CLI exits non-zero with
`{"candidates": [...]}`, the name was ambiguous or unknown — ask the user which
pal they meant (show the candidates' Korean names via `resolve`). Never guess.

## Output formatting

- Korean tables, English keys in parentheses.
- For `transfer`, present each step as `[초절기교] {carrier} × {partner} = {child}`,
  bold the carrier, and remind: keep only offspring that inherited the passive as
  the next parent.
- Mark any step where `partner_hard` is true with ⚠️ (후반/변종 팰).
- List `partners_needed` as "미리 잡아둘 파트너".
- `--easy-partners` only avoids hard PARTNERS, so an intermediate child pal on
  the path may still be a variant/late-game pal — tell the user to check the
  intermediates.
- Footer: `데이터 빌드 ID` from `data/meta.json` (`build_id`); if it looks stale,
  suggest `/breed-refresh`.
- If the target is self-breedable (its own combo produces itself — check with
  `whatis <target> <target>`), append the tip: breed target × target afterward
  to lock/stack passives.

## refresh

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/palbreed.py" refresh --json` needs outbound network to palworldbreed.com. On success, parse the returned JSON with keys `build_id` and `combo_count` to report the new values. If it fails on a VM (e.g. Cowork sandbox without egress), tell the user to run it locally and redistribute the updated `data/` with the plugin.
