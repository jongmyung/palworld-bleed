"""Network scraper / data refresh for palworld-breed. Standard library only."""
import json
import os
import re
import time
import urllib.request

BASE = "https://www.palworldbreed.com"


def _default_fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_build_id(html):
    m = re.search(r'"buildId":"([^"]+)"', html)
    if not m:
        raise ValueError("buildId not found in homepage HTML")
    return m.group(1)


def parse_pals(page_obj):
    out = {}
    for p in page_obj["pageProps"]["pals"]:
        out[p["key"]] = {"name": p["name"], "number": p["number"]}
    return out


def parse_combos(page_obj):
    return [
        [row["parent1_pal"]["key"], row["parent2_pal"]["key"], row["child_pal"]["key"]]
        for row in page_obj["pageProps"]["data"]
    ]


def write_data_atomic(data_dir, combos, pals, meta):
    os.makedirs(data_dir, exist_ok=True)
    payloads = {
        "combos.json": combos,
        "pals.json": pals,
        "meta.json": meta,
    }
    for name, obj in payloads.items():
        final = os.path.join(data_dir, name)
        tmp = final + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        os.replace(tmp, final)


def refresh(data_dir, lang="ko", fetch=None):
    """Re-scrape the full dataset and rewrite data_dir atomically.

    On any error, data_dir is left untouched and the error propagates.
    `scraped_at` is intentionally not stamped here (no clock dependency in the
    engine); callers may add it. We store the build_id and combo_count.
    """
    fetch = fetch or _default_fetch

    def data_url(child):
        return "%s/_next/data/%s/%s/all/all/%s.json" % (BASE, build_id, lang, child)

    build_id = get_build_id(fetch("%s/%s/all/all/all" % (BASE, lang)))
    seed = json.loads(fetch(data_url("all")))
    pals_ko = parse_pals(seed)                       # {key: {name, number}}
    pals_en = parse_pals(json.loads(fetch("%s/_next/data/%s/en-US/all/all/all.json" % (BASE, build_id))))

    combos = []
    for key in pals_ko:
        page = json.loads(fetch(data_url(key)))
        combos.extend(parse_combos(page))
        time.sleep(0.15)

    # dedupe (child-partitioned, so already disjoint, but guard anyway)
    seen = set()
    uniq = []
    for c in combos:
        t = tuple(c)
        if t not in seen:
            seen.add(t)
            uniq.append(c)

    pals = {
        k: {
            "ko": pals_ko[k]["name"],
            "en": pals_en.get(k, {}).get("name", k),
            "number": pals_ko[k]["number"],
        }
        for k in pals_ko
    }
    meta = {"build_id": build_id, "combo_count": len(uniq)}
    write_data_atomic(data_dir, uniq, pals, meta)
    return meta
