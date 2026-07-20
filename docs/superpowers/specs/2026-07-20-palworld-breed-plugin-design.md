# Palworld Breeding Path Plugin — Design

**Date:** 2026-07-20
**Status:** Approved (design)
**Type:** Claude Code plugin (also packageable for Claude Cowork)

## 1. Purpose

A Claude Code plugin that answers Palworld breeding questions by computing
breeding-combination paths over the full combination dataset scraped from
palworldbreed.com (88,213 unique combinations across 299 pals).

The plugin resolves four kinds of questions:

1. **Shortest path** — fewest breeding steps from a start pal to a target pal.
2. **Easy-partner path** — shortest path that prefers easy-to-obtain partner
   pals (avoids variants and late-game pals).
3. **Passive-transfer path** — a relay path that carries a passive skill from a
   pal the user owns down to a target species, preferring partners the user
   already owns.
4. **Reverse lookup** — combinations that produce a target, the easiest such
   combination, and "A × B = ?" queries.

## 2. Approach

**Deterministic Python engine + thin skill wrapper** (approach A of three
considered; B = pure LLM reasoning over data, rejected as error-prone/expensive
for multi-step graph search; C = MCP server, rejected as overkill for personal
use).

- The engine performs all graph search (BFS / weighted Dijkstra) in code, so
  results are correct, fast, and reproducible.
- The skill maps natural language to engine commands, resolves pal names
  (Korean/English), and formats output.

## 3. Architecture

### 3.1 Plugin layout

```
palworld-breed/
├── .claude-plugin/
│   └── plugin.json                 # plugin manifest
├── skills/
│   └── palworld-breed/
│       └── SKILL.md                # NL -> command mapping + output formatting
├── commands/
│   ├── breed-path.md               # /breed-path slash command
│   └── breed-refresh.md            # /breed-refresh slash command
├── scripts/
│   └── palbreed.py                 # deterministic engine (stdlib only)
└── data/
    ├── combos.json                 # [[p1_key, p2_key, child_key], ...]
    ├── pals.json                   # {key: {ko, en, number}}
    └── meta.json                   # {build_id, scraped_at, combo_count}
```

### 3.2 Runtime flow

```
User: "Move Nitewing's passive to Anubis; I also own Lifmunk and Rooby"
  -> SKILL.md parses intent, resolves names, builds command
  -> Bash: python palbreed.py transfer 나이트윙 아누비스 --own 큐룰리스,불꽃밤비 --easy-partners --json
  -> engine runs graph search, returns JSON
  -> Claude formats JSON as a Korean table with English keys
```

### 3.3 Separation of concerns

- **Engine = pure calculator.** JSON in/out, standard library only, stateless.
  Independently testable.
- **Skill = translator/formatter.** Name matching, intent parsing, presentation.
  Trusts the engine for correctness.

## 4. Engine command specification (`palbreed.py`)

Default output is human-readable text; `--json` emits structured output for the
skill to format. Pal names accepted in Korean or English (auto-detected).

| Command | Function | Key options |
|---|---|---|
| `path <start> <target>` | shortest breeding path (BFS) | `--easy-partners`, `--json` |
| `transfer <holder> <target>` | passive-transfer relay path; marks the passive-carrying pal each step | `--own a,b,c`, `--easy-partners`, `--json` |
| `make <target>` | reverse lookup: all combos producing target | `--easiest`, `--limit N`, `--json` |
| `whatis <A> <B>` | A × B = ? | `--json` |
| `refresh` | re-scrape site, rebuild `data/` | `--lang ko` |
| `resolve <name>` | name -> key (debug / disambiguation) | `--json` |

### 4.1 Easy-partner weighting (`--easy-partners`)

Weighted Dijkstra where partner cost is:

- **High** if partner is a variant (non-numeric dex suffix, e.g. `054B`), a
  late-game pal (dex > 140), or Anubis itself when the target is Anubis
  (avoids the circular "need an Anubis to breed an Anubis" path).
- **Lowest** if the partner is in the `--own` list (already owned).
- **Normal** otherwise.

Result: paths that use easy-to-obtain partners are preferred over pure step-count.

### 4.2 Name ambiguity

If a name matches multiple pals (e.g. "무사" -> 불무사 / 어둠무사), the engine
returns the candidate list instead of guessing. The skill then asks the user.

### 4.3 `transfer` JSON output schema

```json
{
  "start": "Nitewing", "target": "Anubis", "steps": 3,
  "path": [
    {"parent_carrier": "Nitewing", "partner": "Frostdeer",
     "child": "Thundercon", "partner_owned": false, "partner_hard": false},
    {"parent_carrier": "Thundercon", "partner": "Frostella",
     "child": "Raycon", "partner_owned": false, "partner_hard": false},
    {"parent_carrier": "Raycon", "partner": "Blazamut",
     "child": "Anubis", "partner_owned": false, "partner_hard": false}
  ],
  "partners_needed": ["Frostdeer", "Frostella", "Blazamut"],
  "notes": ["passive rides on parent_carrier each step"]
}
```

Keys are English; the skill adds Korean names from `pals.json`.

## 5. Data & refresh

### 5.1 Bundled snapshot

Generated from the current scrape.

- `combos.json` — key-only array `[["Nitewing","Frostdeer","Thundercon"], ...]`,
  88,213 rows. Dropping names reduces ~14 MB to ~2–3 MB.
- `pals.json` — `{"Nitewing": {"ko":"나이트윙","en":"Nitewing","number":"..."}}`,
  299 pals. Korean and English names together for language-agnostic matching.
- `meta.json` — `{"build_id":"...","scraped_at":"2026-07-20","combo_count":88213}`.

### 5.2 `refresh` sequence

1. Extract `buildId` dynamically from the homepage (never hardcode — it changes
   on every site deploy).
2. Fetch `/ko/all/all/all.json` for the pal list, then iterate per child key
   `/ko/all/all/{key}.json` (~299 requests). Partitioning by child gives full,
   duplicate-free coverage.
3. Fetch `/en/all/all/all.json` once to map English display names.
4. Rebuild all three data files.

### 5.3 Safety

- Network/partial failure -> **preserve existing `data/`**, report the failure
  (no partial overwrite).
- Missing expected fields (`pageProps.data`) -> treat as site structure change,
  abort with a message.
- 0.15 s delay between requests to avoid hammering the site.
- `refresh` is the **only command that writes files**; all others are read-only.

### 5.4 Freshness

- The skill prints `데이터 기준일: {scraped_at}` under results, prompting
  `/breed-refresh` when stale.
- buildId auto-comparison hint is **excluded from v1** (YAGNI); manual refresh
  only.

## 6. Skill behavior (`SKILL.md` + slash commands)

**Trigger:** Palworld breeding/combination/path requests, pal names, or
passive-transfer requests. Description lists keywords (palworld, 교배, 조합식,
경로, 패시브 이식, etc.).

### 6.1 Intent -> command mapping

| User phrasing | Command |
|---|---|
| "path from A to B" | `path A B --json` |
| "easy / easy partners" | add `--easy-partners` |
| "move this passive to B" (+ owned pals) | `transfer A B --own ... --json` |
| "combos that make X" / "easiest combo" | `make X [--easiest] --json` |
| "A × B = ?" | `whatis A B --json` |
| "refresh" / `/breed-refresh` | `refresh` |

### 6.2 Name resolution flow

1. Pass Korean/English name straight to the engine for matching.
2. On ambiguity, engine returns candidates -> skill asks the user (no arbitrary
   pick).
3. On no match, suggest similar names.

### 6.3 Output rules

- Korean tables with English keys; step form `[passive] pal × partner = child`.
- `transfer` **bolds the passive-carrying pal** each step and notes "keep only
  offspring that inherited the passive as the next parent".
- `--easy-partners` results mark late-game/variant partners with ⚠️.
- Footer shows `데이터 기준일: {scraped_at}`.
- For self-breedable targets (e.g. Anubis), auto-append the
  "self-breed to lock/stack passives afterward" tip.

### 6.4 Slash commands

- `/breed-path <start> <target> [easy]` — quick path only; no args -> usage help.
- `/breed-refresh` — refresh data (needs network; on failure, print workaround).
- All other natural-language requests handled by the skill; only the two most
  common actions get slash shortcuts.

### 6.5 Errors

Engine non-zero exit / empty result -> distinguish cause (no path / name match
failure / corrupt data) and explain; never fabricate a result.

## 7. Claude Cowork / VM compatibility

Cross-environment support is a design requirement.

| Feature | Claude Code (local) | Claude Cowork (VM) |
|---|---|---|
| path / transfer / make / whatis (read-only) | yes | yes — offline via bundled data |
| refresh (re-scrape) | yes | only if VM allows outbound egress to palworldbreed.com |

Implications:

1. Reference scripts/data via `${CLAUDE_PLUGIN_ROOT}` so paths resolve in both a
   Claude Code directory install and a Cowork package.
2. Zero external dependencies (stdlib only) — no pip install on the VM.
3. Package two ways: Claude Code plugin directory + Cowork `.plugin` file
   (packaged via the `create-cowork-plugin` skill).
4. If `refresh` network access is blocked on the VM, print a workaround: refresh
   locally and redistribute the updated `data/` with the plugin.

Note: the Cowork VM's exact outbound egress policy cannot be guaranteed here;
read-only features are unaffected because the data is bundled.

## 8. Out of scope (v1)

- buildId auto-comparison / staleness auto-detection.
- Non-Anubis-specific tuning; the engine is general (any start/target).
- Web UI / CLI-outside-plugin distribution.
- Passive inheritance probability modelling (the plugin finds species paths;
  passive inheritance remains probabilistic and is handled by user guidance).
```

