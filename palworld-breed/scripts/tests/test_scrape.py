import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import scrape  # noqa: E402


class ScrapeUnitTest(unittest.TestCase):
    def test_get_build_id(self):
        html = 'x{"buildId":"ABC123","other":1}y'
        self.assertEqual(scrape.get_build_id(html), "ABC123")

    def test_get_build_id_missing(self):
        with self.assertRaises(ValueError):
            scrape.get_build_id("no build id here")

    def test_parse_pals_and_combos(self):
        page = {"pageProps": {
            "pals": [{"key": "A", "name": "에이", "number": "001"}],
            "data": [{"parent1_pal": {"key": "A"},
                      "parent2_pal": {"key": "B"},
                      "child_pal": {"key": "C"}}],
        }}
        self.assertEqual(scrape.parse_pals(page), {"A": {"name": "에이", "number": "001"}})
        self.assertEqual(scrape.parse_combos(page), [["A", "B", "C"]])

    def test_write_atomic_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            scrape.write_data_atomic(
                d, [["A", "B", "C"]],
                {"A": {"ko": "에이", "en": "A", "number": "001"}},
                {"build_id": "X", "scraped_at": "2026-07-20", "combo_count": 1},
            )
            with open(os.path.join(d, "combos.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f), [["A", "B", "C"]])

    def test_refresh_preserves_on_failure(self):
        with tempfile.TemporaryDirectory() as d:
            # seed existing data
            scrape.write_data_atomic(
                d, [["OLD", "OLD", "OLD"]], {"OLD": {"ko": "구", "en": "OLD", "number": "001"}},
                {"build_id": "old"})

            def boom(url):
                raise RuntimeError("network down")

            with self.assertRaises(RuntimeError):
                scrape.refresh(d, fetch=boom)
            with open(os.path.join(d, "combos.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f), [["OLD", "OLD", "OLD"]])

    def test_refresh_preserves_on_empty_scrape(self):
        with tempfile.TemporaryDirectory() as d:
            # seed existing data
            scrape.write_data_atomic(
                d, [["OLD", "OLD", "OLD"]], {"OLD": {"ko": "구", "en": "OLD", "number": "001"}},
                {"build_id": "old"})

            def empty_fetch(url):
                if not url.endswith(".json"):
                    return 'x{"buildId":"X","other":1}y'
                return '{"pageProps": {"pals": [], "data": []}}'

            with self.assertRaises(ValueError):
                scrape.refresh(d, fetch=empty_fetch)
            with open(os.path.join(d, "combos.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f), [["OLD", "OLD", "OLD"]])
