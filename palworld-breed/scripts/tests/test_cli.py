import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(__file__)
CLI = os.path.join(HERE, "..", "palbreed.py")
FIX = os.path.join(HERE, "fixtures")


def run(*args):
    env = dict(os.environ, PALBREED_DATA=FIX)
    return subprocess.run(
        [sys.executable, CLI, *args],
        capture_output=True, text=True, env=env,
    )


class CliTest(unittest.TestCase):
    def test_whatis_json(self):
        r = run("whatis", "시작", "P1", "--json")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["child"], "Mid")

    def test_path_json(self):
        r = run("path", "Start", "Target", "--json")
        self.assertEqual(json.loads(r.stdout)["steps"], 1)

    def test_transfer_json(self):
        r = run("transfer", "Start", "Tgt", "--easy-partners", "--json")
        data = json.loads(r.stdout)
        self.assertEqual(data["partners_needed"], ["P1", "P2"])

    def test_ambiguous_name_errors(self):
        r = run("resolve", "파트너", "--json")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(sorted(json.loads(r.stdout)["candidates"]), ["P1", "P2"])

    def test_path_includes_names_map(self):
        # Output carries display names so the skill can render 한글(English).
        data = json.loads(run("path", "Start", "Tgt", "--json").stdout)
        self.assertEqual(data["names"]["Var"], {"ko": "변종", "en": "Variant"})
        self.assertEqual(data["names"]["Tgt"], {"ko": "목표", "en": "Target"})

    def test_whatis_includes_names_map(self):
        data = json.loads(run("whatis", "시작", "P1", "--json").stdout)
        self.assertEqual(data["names"]["Start"]["ko"], "시작")
        self.assertEqual(data["names"]["Mid"]["ko"], "중간")

    def test_make_returns_object_with_names(self):
        data = json.loads(run("make", "Tgt", "--easiest", "--json").stdout)
        self.assertEqual(data["target"], "Tgt")
        self.assertIsInstance(data["combos"], list)
        self.assertIn("변종", [v["ko"] for v in data["names"].values()])

    def test_data_flag_after_subcommand(self):
        # --data must be honored when passed AFTER the subcommand and its
        # positionals, without relying on the PALBREED_DATA env var.
        env = {k: v for k, v in os.environ.items() if k != "PALBREED_DATA"}
        r = subprocess.run(
            [sys.executable, CLI, "whatis", "시작", "P1", "--data", FIX, "--json"],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["child"], "Mid")
