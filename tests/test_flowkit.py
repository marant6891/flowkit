"""Automated test suite verifying contracts, adapters, and integrity of FlowKit.
Run: python -m unittest tests/test_flowkit.py
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import grade_eval  # noqa: E402
import validate_agents  # noqa: E402


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

        self.assertEqual(len(manifest["agents"]), 10)
        for a in manifest["agents"]:
            self.assertTrue(a.startswith("./agents/adapters/claude-code/"), a)
            self.assertTrue((ROOT / a).exists(), f"Agent path must exist: {a}")

    def test_manifest_uses_supported_plugin_format(self):
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("skills", manifest, "Skills are discovered from the default skills/ directory")
        self.assertTrue(all(isinstance(a, str) and a.endswith(".md") for a in manifest["agents"]))
        self.assertFalse((ROOT / "skills" / "_template" / "SKILL.md").exists())

    def test_powershell_installer_has_utf8_bom(self):
        self.assertTrue((ROOT / "scripts" / "install.ps1").read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_vscode_install_targets_current_project(self):
        self.assertNotIn('$RepoRoot ".github', (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8-sig"))
        self.assertNotIn('$REPO_ROOT/.github', (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8"))

    def _agents_copy(self, directory):
        target = Path(directory)
        shutil.copytree(ROOT / "agents", target / "agents")
        return target

    def test_agent_validator_passes_on_repository(self):
        self.assertEqual(validate_agents.validate(ROOT), [])

    def test_agent_validator_detects_unknown_tool(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._agents_copy(tmp)
            path = root / "agents" / "adapters" / "claude-code" / "agent-3x3-analyzer.md"
            path.write_text(path.read_text(encoding="utf-8").replace("- Read", "- NieMa"), encoding="utf-8")
            self.assertTrue(any("Unknown tool" in e for e in validate_agents.validate(root)))

    def test_agent_validator_detects_missing_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._agents_copy(tmp)
            (root / "agents" / "adapters" / "vscode" / "agent-3x3-pm.agent.md").unlink()
            self.assertTrue(any("Missing vscode adapter" in e for e in validate_agents.validate(root)))

    def test_agent_validator_detects_stale_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._agents_copy(tmp)
            path = root / "agents" / "adapters" / "claude-code" / "agent-3x3-pm.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nRęczna zmiana\n", encoding="utf-8")
            self.assertTrue(any("out of sync" in e for e in validate_agents.validate(root)))

    def test_installed_agents_keep_full_behaviour(self):
        orchestrator = (ROOT / "agents" / "adapters" / "claude-code" / "agent-3x3.md").read_text(encoding="utf-8")
        for section in ("Correction loop", "Reconciliation", "Task profiles", "Risk labels", "Delivery", "FlowKit skills"):
            self.assertIn(section, orchestrator)

    def test_tools_match_agent_responsibilities(self):
        def tools(name):
            text = (ROOT / "agents" / "adapters" / "claude-code" / f"{name}.md").read_text(encoding="utf-8")
            return yaml.safe_load(text.split("---", 2)[1])["tools"]
        self.assertNotIn("Bash", tools("agent-3x3-devops"))
        for name in ("agent-3x3", "agent-3x3-implementer", "agent-3x3-devops"):
            self.assertIn("Write", tools(name), name)
        for name in ("agent-3x3-analyzer", "agent-3x3-verifier", "agent-3x3-planner", "agent-3x3-pm"):
            self.assertFalse({"Edit", "Write"} & set(tools(name)), name)

    def test_vscode_orchestrator_opens_question_window(self):
        text = (ROOT / "agents" / "adapters" / "vscode" / "agent-3x3.agent.md").read_text(encoding="utf-8")
        tools = yaml.safe_load(text.split("---", 2)[1])["tools"]
        self.assertIn("vscode/askQuestions", tools)
        self.assertNotIn("vscode", tools)
        self.assertIn("## VS Code checkpoint (mandatory)", text)
        self.assertNotIn("vscode_askQuestions", text)

    def test_verifier_can_run_common_test_stacks(self):
        verifier = (ROOT / "agents" / "agent-3x3-verifier_agent.md").read_text(encoding="utf-8")
        for command in ("python -m unittest", "dotnet test", "mvn -q test", "gradle test"):
            self.assertIn(command, verifier)

    def test_eval_cases_are_grounded_in_fixtures(self):
        cases = grade_eval.load_cases()
        self.assertGreaterEqual(len(cases), 3)
        for case in cases.values():
            source = (ROOT / "tests" / "fixtures" / case["fixture"]).read_text(encoding="utf-8")
            for fact in case["evidence"]:
                self.assertIn(fact, source, case["id"])

    def test_eval_grader_separates_good_and_bad_answers(self):
        case = grade_eval.load_cases()["analyzer-sql-injection"]
        good = "ANALYZER: auth\nNot checked: none\n[CRITICAL] sample_auth.py:5 — SQL injection (Fact)"
        self.assertEqual(grade_eval.grade(case, good), [])
        self.assertTrue(grade_eval.grade(case, "ANALYZER: auth — clean"))

    def test_docx_engine_reference_exists(self):
        ref1 = ROOT / "skills" / "flowkit-client-pt-prd-writer" / "references" / "docx-engine.md"
        ref2 = ROOT / "skills" / "flowkit-client-meeting-recap" / "references" / "docx-engine.md"
        self.assertTrue(ref1.exists(), "docx-engine.md must exist in flowkit-client-pt-prd-writer")
        self.assertTrue(ref2.exists(), "docx-engine.md must exist in flowkit-client-meeting-recap")
        content = ref1.read_text(encoding="utf-8")
        self.assertIn("python-docx", content)


if __name__ == "__main__":
    unittest.main()
