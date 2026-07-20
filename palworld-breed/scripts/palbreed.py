#!/usr/bin/env python3
"""palbreed CLI. Standard library only."""
import argparse
import json
import os
import sys

import breed_engine as be


def _data_dir(args):
    # Test/override hook, then standard resolution.
    return be.resolve_data_dir(os.environ.get("PALBREED_DATA") or getattr(args, "data", None))


def _resolve_or_exit(name, pals, as_json):
    key, cands = be.resolve_name(name, pals)
    if key:
        return key
    payload = {"error": "name not resolved: %s" % name, "candidates": cands}
    print(json.dumps(payload, ensure_ascii=False) if as_json else payload)
    sys.exit(2)


def _emit(obj, as_json):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False))
    else:
        print(obj)


def _names(keys, pals):
    """Map each referenced pal key to its display names, so the formatter can
    render `한글(English)` without re-reading the full pal table."""
    out = {}
    for k in keys:
        if k is None or k in out:
            continue
        info = pals.get(k, {})
        out[k] = {"ko": info.get("ko", k), "en": info.get("en", k)}
    return out


def _path_keys(path):
    return [k for step in path
            for k in (step["parent_carrier"], step["partner"], step["child"])]


def main(argv=None):
    # Shared parent applied ONLY to subparsers. --json/--data are only
    # supported AFTER the subcommand (and its positionals): if this parent
    # were also applied to the top-level parser, argparse's subparser action
    # would silently reset --json/--data back to their defaults whenever they
    # were placed before the subcommand, discarding a leading --data value.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true")
    common.add_argument("--data", default=None)

    parser = argparse.ArgumentParser(prog="palbreed")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("path", parents=[common])
    p.add_argument("start"); p.add_argument("target")
    p.add_argument("--easy-partners", action="store_true")

    t = sub.add_parser("transfer", parents=[common])
    t.add_argument("holder"); t.add_argument("target")
    t.add_argument("--own", default="")
    t.add_argument("--easy-partners", action="store_true")

    m = sub.add_parser("make", parents=[common])
    m.add_argument("target")
    m.add_argument("--easiest", action="store_true")
    m.add_argument("--limit", type=int, default=None)

    w = sub.add_parser("whatis", parents=[common])
    w.add_argument("a"); w.add_argument("b")

    r = sub.add_parser("resolve", parents=[common])
    r.add_argument("name")

    sub.add_parser("refresh", parents=[common]).add_argument("--lang", default="ko")

    args = parser.parse_args(argv)
    data_dir = _data_dir(args)

    if args.cmd == "refresh":
        import scrape
        meta = scrape.refresh(data_dir, lang=args.lang)
        _emit(meta, args.json)
        return

    combos, pals = be.load_data(data_dir)
    idx = be.build_index(combos)

    if args.cmd == "resolve":
        key = _resolve_or_exit(args.name, pals, args.json)
        _emit({"key": key, "pal": pals[key]}, args.json)
    elif args.cmd == "whatis":
        a = _resolve_or_exit(args.a, pals, args.json)
        b = _resolve_or_exit(args.b, pals, args.json)
        child = be.whatis(idx, a, b)
        _emit({"a": a, "b": b, "child": child,
               "names": _names([a, b, child], pals)}, args.json)
    elif args.cmd == "path":
        s = _resolve_or_exit(args.start, pals, args.json)
        tg = _resolve_or_exit(args.target, pals, args.json)
        result = be.find_path(idx, pals, s, tg, easy_partners=args.easy_partners)
        if result is not None:
            result = {"start": s, "target": tg, **result,
                      "names": _names([s, tg] + _path_keys(result["path"]), pals)}
        _emit(result, args.json)
    elif args.cmd == "transfer":
        h = _resolve_or_exit(args.holder, pals, args.json)
        tg = _resolve_or_exit(args.target, pals, args.json)
        own = {be._resolve_own(o, pals) for o in args.own.split(",") if o.strip()} \
            if args.own else set()
        result = be.find_transfer(idx, pals, h, tg,
                                  easy_partners=args.easy_partners, own=own)
        result["names"] = _names(
            [result["start"], result["target"]] + result["partners_needed"]
            + _path_keys(result["path"]), pals)
        _emit(result, args.json)
    elif args.cmd == "make":
        tg = _resolve_or_exit(args.target, pals, args.json)
        rows = be.make(idx, pals, tg, easiest=args.easiest, limit=args.limit)
        keys = [tg] + [k for row in rows for k in (row["parent1"], row["parent2"])]
        _emit({"target": tg, "combos": rows, "names": _names(keys, pals)}, args.json)


if __name__ == "__main__":
    main()
