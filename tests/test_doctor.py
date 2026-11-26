"""Testy diagnozy FlowKit (doctor) i pliku zgód.
Uruchom: python -m unittest tests/test_doctor.py
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(ROOT / "scripts"))

import build_agents  # noqa: E402
import flowkit_doctor as doctor  # noqa: E402
import flowkit_exec as fx  # noqa: E402
import guard_bash as guard  # noqa: E402

DOCTOR = str(RUNTIME / "flowkit_doctor.py")


class TempHome(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.allow = self.dir / ".flowkit" / "allow.json"
        patcher = mock.patch.dict(os.environ, {fx.ALLOW_FILE_ENV: str(self.allow),
                                               fx.AUDIT_FILE_ENV: str(self.dir / ".flowkit" / "audit.log")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_allow(self, text):
        self.allow.parent.mkdir(parents=True, exist_ok=True)
        self.allow.write_text(text, encoding="utf-8")

    def statuses(self, checks):
        return [(c.status, c.detail) for c in checks]


class TestAllowFile(TempHome):

    def test_missing_file_is_optional_and_points_to_init(self):
        (check,) = doctor.inspect_allow_file(self.allow)
        self.assertEqual(check.status, doctor.INFO)
        self.assertIn("init", check.fix)

    def test_broken_json_reports_line_and_disables_all_rules(self):
        self.write_allow('{\n  "commands": {\n    "*": ["make lint",]\n  }\n}\n')
        (check,) = doctor.inspect_allow_file(self.allow)
        self.assertEqual(check.status, doctor.ERROR)
        self.assertIn("linii 3", check.detail)
        allowed, ignored = fx.user_allowed("orchestrator")
        self.assertEqual((allowed, len(ignored)), ([], 1))

    def test_missing_commands_object_is_an_error(self):
        self.write_allow('{"orchestrator": ["dotnet build"]}')
        (check,) = doctor.inspect_allow_file(self.allow)
        self.assertEqual(check.status, doctor.ERROR)
        self.assertIn("commands", check.detail)

    def test_unknown_role_ignored_entries_and_active_rules(self):
        self.write_allow(json.dumps({"commands": {
            "*": ["make lint"], "orchestator": ["dotnet build"], "validator": ["bash", "checkov -d"],
            "analyst": "pytest"}}))
        checks = doctor.inspect_allow_file(self.allow)
        first = checks[0]
        self.assertEqual(first.status, doctor.OK)
        self.assertIn("*: make lint", first.detail)
        self.assertIn("validator: checkov -d", first.detail)
        details = " | ".join(c.detail for c in checks)
        self.assertIn('nieznana rola "orchestator"', details)
        self.assertIn('chodziło o "orchestrator"', details)
        self.assertIn('pominięto wpis "bash"', details)
        self.assertIn('"analyst" musi być listą', details)

    @unittest.skipIf(os.name == "nt", "uprawnienia POSIX")
    def test_group_writable_file_is_an_error(self):
        self.write_allow('{"commands": {}}')
        self.allow.chmod(0o664)
        self.assertIn(doctor.ERROR, [c.status for c in doctor.inspect_allow_file(self.allow)])


class TestInit(TempHome):

    def test_init_creates_empty_file_with_every_role_and_never_overwrites(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(doctor.init_allow_file(self.allow), 0)
        self.assertIn("Utworzono pusty plik zgód", out.getvalue())
        data = json.loads(self.allow.read_text(encoding="utf-8"))
        self.assertEqual(set(data["commands"]), {"*", *fx.ROLE_COMMANDS})
        self.assertTrue(all(value == [] for value in data["commands"].values()))
        self.assertEqual(fx.user_allowed("orchestrator"), ([], []))
        if os.name != "nt":
            self.assertEqual(self.allow.stat().st_mode & 0o777, 0o600)

        self.write_allow('{"commands": {"*": ["make lint"]}}')
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(doctor.init_allow_file(self.allow), 0)
        self.assertIn("już istnieje", out.getvalue())
        self.assertIn("make lint", self.allow.read_text(encoding="utf-8"))

    def test_agents_cannot_run_init(self):
        for prefixes in fx.ROLE_COMMANDS.values():
            self.assertFalse(any("init" in p or "flowkit_doctor" in p for p in prefixes))
        self.assertIsNotNone(fx.check("orchestrator", ["python", DOCTOR, "init"]))
        self.assertIsNotNone(guard.problem_with(f'python "{DOCTOR}" init', "orchestrator"))


class TestDoctorReport(TempHome):

    def run_doctor(self, *args):
        return subprocess.run([sys.executable, DOCTOR, *args], capture_output=True, text=True, encoding="utf-8",
                              env=os.environ.copy(), check=False)

    def test_broken_allow_file_fails_with_exit_code_1(self):
        self.write_allow("{nie json")
        result = self.run_doctor()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("BŁĄD", result.stdout)
        self.assertIn("Podsumowanie: błędy", result.stdout)

    def test_json_output_has_sections_and_fixes(self):
        result = self.run_doctor("--json", "--role", "analyst")
        data = json.loads(result.stdout)
        self.assertEqual(data["version"], fx.VERSION)
        sections = {c["section"] for c in data["checks"]}
        self.assertEqual(sections, {"Instalacja", "Bezpieczeństwo", "Konfiguracja", "Narzędzia"})
        allow = next(c for c in data["checks"] if c["name"] == "Plik zgód")
        self.assertIn("init", allow["fix"])
        self.assertTrue(any(c["name"] == "Zgody dla roli analyst" for c in data["checks"]))

    def test_bad_usage_returns_2(self):
        self.assertEqual(self.run_doctor("--role", "nieznana").returncode, 2)

    def test_executor_doctor_uses_new_report(self):
        result = subprocess.run([sys.executable, str(RUNTIME / "flowkit_exec.py"), "--role", "analyst", "--", "doctor"],
                                capture_output=True, text=True, encoding="utf-8", env=os.environ.copy(), check=False)
        self.assertIn(f"FlowKit doctor {fx.VERSION} (rola: analyst)", result.stdout)
        self.assertIn("== Bezpieczeństwo ==", result.stdout)

    def test_missing_extra_path_is_reported(self):
        with mock.patch.dict(os.environ, {fx.EXTRA_PATHS_ENV: str(self.dir / "nie-ma")}):
            checks = doctor.check_configuration()
        self.assertIn(doctor.WARN, [c.status for c in checks])

    def test_stale_agents_and_legacy_agents_are_reported(self):
        agents = self.dir / "agents"
        agents.mkdir()
        (agents / "flowkit-analyst.md").write_text("---\n---\n<!-- FlowKit 1.0.0 · Plik -->\n", encoding="utf-8")
        (agents / "agent-3x3.md").write_text("stary", encoding="utf-8")
        with mock.patch.object(doctor, "agent_dirs", return_value=[agents]):
            checks = doctor.check_installation()
        names = {(c.name, c.status) for c in checks}
        self.assertIn(("Agenci", doctor.WARN), names)
        self.assertIn(("Starzy agenci", doctor.WARN), names)

    def test_python_missing_for_hooks_is_an_error(self):
        with mock.patch.object(doctor, "hook_python", return_value=(None, None)):
            checks = doctor.check_installation()
        self.assertIn(("Python dla hooków", doctor.ERROR), {(c.name, c.status) for c in checks})


class TestVersionAndFiles(unittest.TestCase):

    def test_runtime_version_matches_plugin_and_agents(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertEqual(fx.VERSION, plugin)
        for name in build_agents.AGENTS:
            for platform in ("claude", "vscode"):
                text = build_agents.target(name, platform).read_text(encoding="utf-8")
                self.assertEqual(doctor.AGENT_MARKER.search(text).group(1), fx.VERSION, name)

    def test_repository_install_kind(self):
        self.assertIn("repozytorium", doctor.install_kind(RUNTIME))

    def test_schema_and_example_match_roles_and_rules(self):
        schema = json.loads((ROOT / "docs" / "allow.schema.json").read_text(encoding="utf-8"))
        roles = schema["properties"]["commands"]["propertyNames"]["enum"]
        self.assertEqual(roles, list(doctor.ROLE_KEYS))
        self.assertEqual(schema["$id"], doctor.SCHEMA_URL)
        example = json.loads((ROOT / "docs" / "allow.example.json").read_text(encoding="utf-8"))
        for role, entries in example["commands"].items():
            self.assertIn(role, roles)
            for entry in entries:
                self.assertIsNone(fx.allow_entry_problem(entry), entry)

    def test_doctor_entry_points_exist(self):
        command = (ROOT / "commands" / "doctor.md").read_text(encoding="utf-8")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/runtime/flowkit_doctor.py", command)
        self.assertIn("Nie uruchamiaj go sam", command)
        prompt = (ROOT / ".github" / "prompts" / "flowkit-doctor.prompt.md").read_text(encoding="utf-8")
        self.assertIn(".github/flowkit/runtime/flowkit_doctor.py", prompt)
        for installer in ("install.sh", "install.ps1"):
            self.assertIn("flowkit_doctor.py", (ROOT / "scripts" / installer).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
