"""Testy sprawdzenia aktualności dokumentacji (scripts/validate_docs.py)."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_docs as vd  # noqa: E402


class TestDocsUpToDate(unittest.TestCase):

    def test_repository_docs_are_current(self):
        self.assertEqual(vd.check(), [])

    def test_prefixes_come_from_orchestrator_table(self):
        prefixes = vd.orchestrator_prefixes()
        for prefix in ("TEST:", "UAT:", "GRILL:", "PRZEPYTAJ:", "SQL:", "AUTO:"):
            self.assertIn(prefix, prefixes)

    def broken(self, name: str, old: str, new: str) -> list[str]:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        copy = tmp / Path(name).name
        text = vd.DOCS[name].read_text(encoding="utf-8")
        self.assertIn(old, text)
        copy.write_text(text.replace(old, new), encoding="utf-8")
        with mock.patch.dict(vd.DOCS, {name: copy}):
            return vd.check()

    def test_missing_prefix_is_reported(self):
        errors = self.broken(".github/copilot-instructions.md", "`GRILL:`", "`X`")
        self.assertTrue(any("GRILL:" in e for e in errors), errors)

    def test_missing_subagent_is_reported(self):
        errors = self.broken("README.md", "**flowkit-validator**", "**validator**")
        self.assertTrue(any("flowkit-validator" in e for e in errors), errors)

    def test_wrong_version_is_reported(self):
        errors = self.broken("README.md", "Wersja: **", "Wersja: **0.0.")
        self.assertTrue(any("wersja" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
