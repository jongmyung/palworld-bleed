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
