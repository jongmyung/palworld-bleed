"""Palworld breeding engine: data loading, name resolution, graph search.

Standard library only. No third-party dependencies.
"""
import json
import os


def resolve_data_dir(explicit=None):
    """Return the data directory path.

    Order: explicit arg, $CLAUDE_PLUGIN_ROOT/data, ../data relative to scripts/.
    """
    if explicit:
        return explicit
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root:
        return os.path.join(root, "data")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def load_data(data_dir):
    """Load (combos, pals) from data_dir.

    combos: list of [p1_key, p2_key, child_key].
    pals: {key: {"ko": str, "en": str, "number": str}}.
    """
    with open(os.path.join(data_dir, "combos.json"), encoding="utf-8") as f:
        combos = json.load(f)
    with open(os.path.join(data_dir, "pals.json"), encoding="utf-8") as f:
        pals = json.load(f)
    return combos, pals


def resolve_name(query, pals):
    """Resolve a Korean/English name or key to a pal key.

    Returns (key_or_None, candidate_keys). One match -> (key, [key]);
    multiple -> (None, candidates); none -> (None, []).
    """
    q = query.strip()
    ql = q.lower()
    # 1. exact key
    if q in pals:
        return q, [q]
    # 2. exact ko / en (case-insensitive for en)
    exact = [
        k for k, v in pals.items()
        if v.get("ko") == q or v.get("en", "").lower() == ql
    ]
    if len(exact) == 1:
        return exact[0], exact
    if len(exact) > 1:
        return None, exact
    # 3. substring on ko / en
    sub = [
        k for k, v in pals.items()
        if q in v.get("ko", "") or ql in v.get("en", "").lower()
    ]
    if len(sub) == 1:
        return sub[0], sub
    return None, sub


import re
from collections import defaultdict


def build_index(combos):
    child_of = defaultdict(set)
    partner_for = defaultdict(lambda: defaultdict(list))
    pair_child = {}
    producers = defaultdict(list)
    for p1, p2, child in combos:
        child_of[p1].add(child)
        child_of[p2].add(child)
        partner_for[p1][child].append(p2)
        partner_for[p2][child].append(p1)
        pair_child[tuple(sorted((p1, p2)))] = child
        producers[child].append((p1, p2))
    return {
        "child_of": child_of,
        "partner_for": partner_for,
        "pair_child": pair_child,
        "producers": producers,
    }


def _dex_num(number):
    m = re.match(r"(\d+)", number or "")
    return int(m.group(1)) if m else 999


def is_hard(key, pals, target=None):
    if target == "Anubis" and key == "Anubis":
        return True
    number = pals.get(key, {}).get("number", "999")
    if not re.fullmatch(r"\d+", number):   # variant suffix like 054B
        return True
    return _dex_num(number) > 140


def whatis(index, a_key, b_key):
    return index["pair_child"].get(tuple(sorted((a_key, b_key))))


def make(index, pals, target_key, easiest=False, limit=None):
    seen = set()
    rows = []
    for p1, p2 in index["producers"].get(target_key, []):
        key = tuple(sorted((p1, p2)))
        if key in seen:
            continue
        seen.add(key)
        if easiest and (p1 == p2 == target_key or target_key in (p1, p2)):
            continue
        rows.append({
            "parent1": p1, "parent2": p2,
            "hard1": is_hard(p1, pals, target_key),
            "hard2": is_hard(p2, pals, target_key),
        })
    if easiest:
        rows.sort(key=lambda r: (
            r["hard1"] + r["hard2"],
            _dex_num(pals.get(r["parent1"], {}).get("number")) +
            _dex_num(pals.get(r["parent2"], {}).get("number")),
        ))
    if limit is not None:
        rows = rows[:limit]
    return rows
