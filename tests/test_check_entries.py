# SPDX-License-Identifier: MPL-2.0
import importlib.util
import json
import sys
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("check_entries", Path(__file__).resolve().parent.parent / "tools/check_entries.py")
check = importlib.util.module_from_spec(spec)
sys.modules["check_entries"] = check
spec.loader.exec_module(check)

GOOD = {
    "repository": "someone/nf-clock",
    "commit": "a" * 40,
    "version": "1.2.3",
    "sdk": "b" * 40,
    "build": 'make -j"$(nproc)" module',
    "payload": "build/nbt-clock.so",
    "name": "Clock",
    "summary": "A clock on the iDrive screen.",
    "license": "MPL-2.0",
    "category": "tool",
}


def reasons(app="clock", reserved=None, **changes):
    entry = {**GOOD, **changes}
    for key, value in changes.items():
        if value is None:
            del entry[key]
    return list(check.problems(app, entry, reserved or {}))


class EntryTests(unittest.TestCase):
    def test_a_good_entry(self):
        self.assertEqual(reasons(), [])
        self.assertEqual(reasons(**{"package-args": "release/package.args", "lfs": True}), [])
        item = check.matrix_item("clock", GOOD)
        self.assertEqual((item["package-args"], item["lfs"]), ("release/package.args", False))

    def test_the_examples_are_the_one_nbtfoundry_source(self):
        self.assertEqual(reasons(repository="NBTFoundry/examples"), [])
        self.assertTrue(reasons(repository="NBTFoundry/nf-doom"))

    def test_ids_of_other_repositories_and_the_manager_are_refused(self):
        self.assertTrue(reasons("doom", {"doom": "NBTFoundry/nf-doom"}))
        self.assertTrue(reasons("manager"))
        self.assertTrue(reasons("Clock"))

    def test_fields(self):
        for changes in ({"repository": "NBTFoundry/nf-doom"}, {"repository": "bad"},
                        {"commit": "A" * 40}, {"commit": "a" * 39}, {"sdk": "main"},
                        {"version": "1.2"}, {"version": "0.0.0"}, {"version": "1000.0.0"},
                        {"build": "make\nrm -rf /"}, {"build": "x" * 201},
                        {"payload": "../outside"}, {"payload": "/abs"}, {"package-args": "a/../b"},
                        {"lfs": "yes"}, {"name": ""}, {"summary": " padded"}, {"category": "other"},
                        {"name": None}, {"extra": 1}):
            with self.subTest(changes=changes):
                self.assertTrue(reasons(**changes))


if __name__ == "__main__":
    unittest.main()
