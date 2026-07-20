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


class IndexTest(unittest.TestCase):
    def setUp(self):
        self.combos, self.pals = be.load_data(FIX)
        self.idx = be.build_index(self.combos)

    def test_whatis_symmetric(self):
        self.assertEqual(be.whatis(self.idx, "Start", "P1"), "Mid")
        self.assertEqual(be.whatis(self.idx, "P1", "Start"), "Mid")

    def test_whatis_none(self):
        self.assertIsNone(be.whatis(self.idx, "Start", "P2"))

    def test_is_hard(self):
        self.assertTrue(be.is_hard("Var", self.pals))    # variant suffix
        self.assertTrue(be.is_hard("Late", self.pals))   # dex > 140
        self.assertFalse(be.is_hard("P1", self.pals))

    def test_is_hard_anubis_special_case(self):
        self.assertTrue(be.is_hard("Anubis", self.pals, target="Anubis"))
        self.assertFalse(be.is_hard("Anubis", self.pals))

    def test_make_lists_all_producers(self):
        rows = be.make(self.idx, self.pals, "Tgt")
        pairs = {tuple(sorted((r["parent1"], r["parent2"]))) for r in rows}
        self.assertIn(("Mid", "P2"), pairs)
        self.assertIn(("Start", "Var"), pairs)
        self.assertIn(("Tgt", "Tgt"), pairs)

    def test_make_easiest_excludes_self_and_ranks(self):
        rows = be.make(self.idx, self.pals, "Tgt", easiest=True)
        pairs = [tuple(sorted((r["parent1"], r["parent2"]))) for r in rows]
        self.assertNotIn(("Tgt", "Tgt"), pairs)      # self-breed excluded
        self.assertEqual(pairs[0], ("Mid", "P2"))    # all-easy ranked first


if __name__ == "__main__":
    unittest.main()
