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
