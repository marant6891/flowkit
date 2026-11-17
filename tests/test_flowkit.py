"""Automated test suite verifying contracts, adapters, and integrity of FlowKit.
Run: python -m unittest tests/test_flowkit.py
"""
import json
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


class TestFlowKitContracts(unittest.TestCase):

    def test_all_agents_have_valid_yaml(self):
        agent_files = list((ROOT / "agents").rglob("*.md"))
        self.assertGreater(len(agent_files), 10, "Should have discovered agent files across core and adapters")

        for f in agent_files:
            if "core" in f.parts:
                # Pliki core to czyste kontrakty architektoniczne
                content = f.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("# Core Contract:"), f"{f.name} in core/ must start with title")
                continue

            content = f.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"), f"{f} must start with frontmatter")
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"{f} invalid frontmatter structure")
            data = yaml.safe_load(parts[1])
            self.assertIsInstance(data, dict, f"{f} frontmatter must be a dict")
            self.assertIn("name", data, f"{f} must have 'name'")
            self.assertIn("description", data, f"{f} must have 'description'")

    def test_orchestrator_has_no_yaml_syntax_error(self):
        f = ROOT / "agents" / "agent-3x3_agent.md"
        content = f.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        data = yaml.safe_load(parts[1])
        self.assertEqual(data["name"], "agent-3x3")
        self.assertIn("description", data)

    def test_verifier_includes_not_verified_status(self):
        verifier_file = ROOT / "agents" / "agent-3x3-verifier_agent.md"
        content = verifier_file.read_text(encoding="utf-8")
        self.assertIn("[NOT VERIFIED]", content, "Verifier must support NOT VERIFIED status")

    def test_analyzer_includes_scanned_and_not_checked(self):
        analyzer_file = ROOT / "agents" / "agent-3x3-analyzer_agent.md"
        content = analyzer_file.read_text(encoding="utf-8")
        self.assertIn("Scanned:", content)
        self.assertIn("Not checked:", content)

    def test_manifest_declares_existing_files(self):
        manifest_file = ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(manifest_file.exists())
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

        for s in manifest.get("skills", []):
            p = ROOT / s["path"]
            self.assertTrue(p.exists(), f"Skill path must exist: {p}")

        for a in manifest.get("agents", []):
            p = ROOT / a["path"]
            self.assertTrue(p.exists(), f"Agent path must exist: {p}")

    def test_docx_engine_reference_exists(self):
        ref1 = ROOT / "skills" / "client-pt-prd-writer" / "references" / "docx-engine.md"
        ref2 = ROOT / "skills" / "client-meeting-recap" / "references" / "docx-engine.md"
        self.assertTrue(ref1.exists(), "docx-engine.md must exist in client-pt-prd-writer")
        self.assertTrue(ref2.exists(), "docx-engine.md must exist in client-meeting-recap")
        content = ref1.read_text(encoding="utf-8")
        self.assertIn("python-docx", content)


if __name__ == "__main__":
    unittest.main()
