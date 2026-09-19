"""Offline tests for navigation extraction and stale-source handling."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "indexes", Path(__file__).with_name("build-source-indexes.py"))
indexes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexes)


class IndexTests(unittest.TestCase):
    def test_headings_keep_source_lines_and_number_hint(self):
        text = "Title\nSource\nFetched\n\n\nTitle\nPreamble\n\nPart 1\nOverview\n\n\nExample heading\n\n12A.\n  (1) Body text\n"
        self.assertEqual(list(indexes.headings(text)),
                         [(9, "Part 1: Overview"), (13, "12A. Example heading")])

    def test_short_source_has_no_invented_headings(self):
        self.assertEqual(list(indexes.headings("Title\nSource\nFetched\n\nTitle\nPreamble")), [])

    def test_manifest_gaps_missing_files_and_unlisted_leftovers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manual = root / "docs/guidance/example"
            manual.mkdir(parents=True)
            (manual / "good.txt").write_text("A title | with pipe\nBody", encoding="utf-8")
            (manual / "old.txt").write_text("Stale title", encoding="utf-8")
            (manual / "unlisted.txt").write_text("Unlisted title", encoding="utf-8")
            state = {"status": "partial", "pages": {
                "/good": {"file": "good.txt"}, "/old": {"file": "old.txt"},
                "/missing": {"file": "missing.txt"}},
                "gaps": {"/old": {"reason": "redirect"}}, "errors": {}}
            (manual / "manifest.json").write_text(json.dumps(state), encoding="utf-8")
            indexes.guidance(root)
            result = (manual / "INDEX.md").read_text(encoding="utf-8")
            self.assertIn("A title &#124; with pipe", result)
            self.assertNotIn("Stale title", result)
            self.assertNotIn("Unlisted title", result)
            self.assertIn("missing local file", result)
            self.assertIn("redirect", result)
            indexes.guidance(root, check=True)
            (manual / "good.txt").write_text("Changed title", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                indexes.guidance(root, check=True)


if __name__ == "__main__":
    unittest.main()
