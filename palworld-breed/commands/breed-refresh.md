---
description: Refresh the Palworld breeding dataset from palworldbreed.com (needs network).
---

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/palbreed.py" refresh`. This makes ~299
network requests and takes about a minute. On success, report the new
`combo_count` and `build_id`. On network failure, tell the user this environment
has no outbound access to palworldbreed.com and they should run refresh on a
machine that does, then copy the updated `data/` into the plugin.
