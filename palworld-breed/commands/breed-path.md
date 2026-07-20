---
description: "Shortest Palworld breeding path between two pals. Usage: /breed-path <start> <target> [easy]"
---

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/palbreed.py" path "$1" "$2" --json`
(append `--easy-partners` if the third argument is "easy" or "쉽게"). If any name
is ambiguous, the CLI returns candidates — ask which pal was meant. Format the
result as a Korean step table with English keys, per the palworld-breed skill.

If no arguments are given, show usage: `/breed-path <시작팰> <목표팰> [쉽게]`.
