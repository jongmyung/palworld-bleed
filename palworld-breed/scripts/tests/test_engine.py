import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import breed_engine as be  # noqa: E402

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


class LoadAndResolveTest(unittest.TestCase):
    def setUp(self):
        self.combos, self.pals = be.load_data(FIX)

    def test_load_data_counts(self):
        self.assertEqual(len(self.combos), 4)
        self.assertEqual(self.pals["Start"]["ko"], "시작")

    def test_resolve_exact_key(self):
        self.assertEqual(be.resolve_name("Start", self.pals), ("Start", ["Start"]))

    def test_resolve_korean_name(self):
        self.assertEqual(be.resolve_name("변종", self.pals), ("Var", ["Var"]))

    def test_resolve_english_case_insensitive(self):
        self.assertEqual(be.resolve_name("target", self.pals), ("Tgt", ["Tgt"]))

    def test_resolve_ambiguous_returns_candidates(self):
        key, cands = be.resolve_name("파트너", self.pals)
        self.assertIsNone(key)
        self.assertEqual(sorted(cands), ["P1", "P2"])

    def test_resolve_no_match(self):
        self.assertEqual(be.resolve_name("없는팰", self.pals), (None, []))


if __name__ == "__main__":
    unittest.main()
