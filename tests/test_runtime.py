"""Testy lokalnej warstwy bezpieczeństwa FlowKit.
Uruchom: python -m unittest tests/test_runtime.py
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "scripts"))

import flowkit_exec as fx  # noqa: E402
import guard_bash as guard  # noqa: E402
import run_evals  # noqa: E402

EXEC = fx.__file__.replace("\\", "/")


class TestCommandPolicy(unittest.TestCase):

    def test_allowed_commands(self):
        allowed = {
            "diagnostics": ["kubectl get pods -n app", "kubectl logs pod-1", "docker ps", "terraform validate",
                            "kubectl apply --dry-run=client -f app.yaml", "helm status api"],
            "verifier": ["pytest -q", "python -m unittest tests/test_a.py", "dotnet test", "go test ./...", "git diff"],
            "analyzer": ["rg TODO src", "tsc --noEmit", "git log -5"],
            "implementer": ["pytest -x tests/test_a.py", "eslint src/a.js"],
            "orchestrator": ["git status", "git add src/a.py", "git commit -m opis", "git push -u origin feat/a",
                             "gh pr create --fill", "python C:/x/client-pt-prd-writer/scripts/generate_diagram.py m.yaml"],
            "analyst": ["read-document brief.docx --outline", "python /x/client-pt-prd-writer/scripts/check_status_labels.py d.md"],
        }
        for role, commands in allowed.items():
            for command in commands:
                self.assertIsNone(fx.check(role, command.split()), f"{role}: {command}")

    def test_denied_commands(self):
        denied = {
            "diagnostics": ["kubectl delete pod a", "kubectl apply -f a.yaml", "kubectl exec -it a sh", "kubectl get secrets",
                            "kubectl get secret/db -o yaml", "terraform apply", "terraform destroy", "helm upgrade a b",
                            "docker push a", "docker exec a sh", "aws s3 ls", "curl https://example.com",
                            "kubectl apply --dry-run=client --dry-run=none -f a.yaml", "pytest -q"],
            "verifier": ["npm install", "pip install x", "git commit -m x", "rm -rf build", "eslint --fix src",
                         "find . -delete", "find . -exec rm {} ;", "bash -c ls", "git diff --output=x.patch"],
            "analyzer": ["pytest -q", "npm test"],
            "implementer": ["git commit -m x", "npm install", "docker build ."],
            "orchestrator": ["git add -A", "git add .", "git commit --amend -m x", "git commit --no-verify -m x",
                             "git push -u origin main", "git push -u origin master", "git push --force origin a",
                             "git push -u origin +a", "git reset --hard", "git clean -fd", "gh pr merge 1",
                             "python evil.py", "python -c print(1)"],
            "analyst": ["python /tmp/generate_diagram.py", "git push -u origin a"],
        }
        for role, commands in denied.items():
            for command in commands:
                self.assertIsNotNone(fx.check(role, command.split()), f"{role}: {command}")

    def test_sensitive_files_are_protected(self):
        for path in (".env", "config/.env.production", "id_rsa", "server.pem", "credentials.json", "secrets.yaml"):
            self.assertIsNotNone(fx.check("analyzer", ["rg", "x", path]), path)
        self.assertIsNone(fx.check("analyzer", ["rg", "x", ".env.example"]))

    def test_log_commands_are_limited(self):
        self.assertIn("--tail=200", fx.with_limits(["kubectl", "logs", "a"]))
        self.assertEqual(fx.with_limits(["kubectl", "logs", "a", "--tail=5"]), ["kubectl", "logs", "a", "--tail=5"])

    def test_output_is_redacted_and_shortened(self):
        text = fx.redact('password=abc123 token: "xyz987" Authorization: Bearer abcdefghijklmnop postgres://u:tajne@db/x AKIAABCDEFGHIJKLMNOP')
        for secret in ("abc123", "xyz987", "abcdefghijklmnop", "tajne", "AKIAABCDEFGHIJKLMNOP"):
            self.assertNotIn(secret, text)
        lines = fx.limit_output("\n".join(str(i) for i in range(1000))).splitlines()
        self.assertEqual(len(lines), fx.MAX_LINES + 1)
        self.assertEqual(lines[-1], "999")


class TestGuardHook(unittest.TestCase):

    def run_guard(self, agent, command):
        payload = {"tool_name": "Bash", "tool_input": {"command": command}}
        if agent:
            payload["agent_type"] = agent
        return subprocess.run([sys.executable, str(ROOT / "runtime" / "guard_bash.py")], input=json.dumps(payload),
                              capture_output=True, text=True, encoding="utf-8", check=False)

    def test_normal_sessions_are_not_affected(self):
        self.assertEqual(self.run_guard(None, "rm -rf build").returncode, 0)
        self.assertEqual(self.run_guard("Explore", "rm -rf build").returncode, 0)

    def test_direct_commands_are_blocked_with_guidance(self):
        result = self.run_guard("agent-3x3-diagnostics", "kubectl get pods")
        self.assertEqual(result.returncode, 2)
        self.assertIn("flowkit_exec.py", result.stderr)

    def test_plugin_scoped_agent_name_is_recognised(self):
        self.assertEqual(self.run_guard("flowkit:agent-3x3-verifier", "rm -rf build").returncode, 2)

    def test_executor_with_allowed_command_passes(self):
        command = f'python "{EXEC}" --role diagnostics -- kubectl get pods'
        self.assertEqual(self.run_guard("flowkit:agent-3x3-diagnostics", command).returncode, 0)

    def test_bypass_attempts_are_blocked(self):
        attempts = [
            f'python "{EXEC}" --role diagnostics -- kubectl get pods; rm -rf build',
            f'python "{EXEC}" --role diagnostics -- kubectl get pods && rm -rf build',
            f'python "{EXEC}" --role diagnostics -- kubectl get pods | sh',
            f'python "{EXEC}" --role diagnostics -- kubectl get pods > out.txt',
            f'python "{EXEC}" --role diagnostics -- kubectl get $(rm -rf x)',
            f'python "{EXEC}" --role diagnostics -- kubectl delete pod a',
            f'python "{EXEC}" --role orchestrator -- git status',
            'python ./flowkit_exec.py --role diagnostics -- kubectl get pods',
            'FOO=1 python x.py',
        ]
        for command in attempts:
            self.assertEqual(self.run_guard("agent-3x3-diagnostics", command).returncode, 2, command)

    def test_agents_without_execution_role_are_blocked(self):
        self.assertEqual(self.run_guard("agent-3x3-devops", "ls").returncode, 2)

    def test_invalid_hook_input_fails_closed(self):
        result = subprocess.run([sys.executable, str(ROOT / "runtime" / "guard_bash.py")], input="nie-json",
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)


class TestLocalDocuments(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def word(self):
        ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        xml = (f'<w:document {ns}><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Zakres</w:t></w:r></w:p>'
               '<w:p><w:r><w:t>password=tajne123</w:t></w:r></w:p>'
               '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>FR-001</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Wymagane</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
               '</w:body></w:document>')
        path = self.dir / "a.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", xml)
        return path

    def test_word_document_is_read_locally(self):
        self.assertEqual(fx.word_lines(self.word()), ["# Zakres", "password=tajne123", "| FR-001 | Wymagane |"])

    def test_excel_is_read_locally(self):
        ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        rel = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        path = self.dir / "a.xlsx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("xl/workbook.xml", f'<workbook {ns} {rel}><sheets><sheet name="Dane" r:id="rId1"/></sheets></workbook>')
            archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/s1.xml"/></Relationships>')
            archive.writestr("xl/sharedStrings.xml", f'<sst {ns}><si><t>Status</t></si></sst>')
            archive.writestr("xl/worksheets/s1.xml", f'<worksheet {ns}><sheetData><row><c t="s"><v>0</v></c><c><v>7</v></c></row></sheetData></worksheet>')
        self.assertEqual(fx.excel_lines(path), ["# Arkusz: Dane", "Status\t7"])

    def test_malicious_xml_is_rejected(self):
        path = self.dir / "b.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", '<!DOCTYPE x [<!ENTITY a "b">]><x/>')
        with self.assertRaises(ValueError):
            fx.word_lines(path)

    def test_sensitive_document_is_rejected(self):
        path = self.dir / ".env"
        path.write_text("A=1", encoding="utf-8")
        with self.assertRaises(ValueError):
            fx.document_lines(path)


class TestLocalOnlySolution(unittest.TestCase):

    def agent_files(self):
        return list((ROOT / "agents" / "adapters").rglob("*.md")) + list((ROOT / "agents").glob("*_agent.md"))

    def test_agents_have_no_mcp_or_web_tools(self):
        for path in self.agent_files():
            data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            tools = [str(t).lower() for t in data["tools"]]
            self.assertFalse(any("mcp" in t or "web" in t for t in tools), path.name)
            self.assertNotIn("mcpServers", data, path.name)

    def test_plugin_has_no_mcp_configuration(self):
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("mcpServers", manifest)
        self.assertFalse((ROOT / ".mcp.json").exists())

    def test_runtime_and_skill_scripts_do_not_use_network_libraries(self):
        pattern = re.compile(r"^\s*(?:import|from)\s+(socket|urllib|http|requests|httpx|aiohttp|ftplib|smtplib)\b", re.M)
        files = list((ROOT / "runtime").glob("*.py")) + list((ROOT / "skills").rglob("scripts/*.py"))
        self.assertGreater(len(files), 6)
        for path in files:
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), path.name)

    def test_claude_subagents_have_model_and_turn_limits(self):
        for path in (ROOT / "agents" / "adapters" / "claude-code").glob("agent-3x3-*.md"):
            data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            self.assertEqual(data["model"], "sonnet", path.name)
            self.assertGreater(data["maxTurns"], 0, path.name)

    def test_agents_with_bash_have_guard_hook(self):
        for path in (ROOT / "agents" / "adapters" / "claude-code").glob("*.md"):
            data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            if "Bash" in data["tools"]:
                self.assertIn("guard_bash.py", json.dumps(data["hooks"]), path.name)

    def test_plugin_hook_guards_bash(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"][0]
        self.assertEqual(hooks["matcher"], "Bash")
        self.assertIn("guard_bash.py", hooks["hooks"][0]["command"])

    def test_orchestrator_procedures_exist(self):
        source = (ROOT / "agents" / "agent-3x3_agent.md").read_text(encoding="utf-8")
        names = set(re.findall(r"`([a-z-]+\.md)`", source)) - {"flowkit-project.md"}
        self.assertEqual(len(names), 5)
        for name in names:
            self.assertTrue((ROOT / "runtime" / "procedures" / name).exists(), name)


class TestEvalRunner(unittest.TestCase):

    def test_trigger_set_has_positive_and_negative_cases(self):
        data = yaml.safe_load((ROOT / "tests" / "evals" / "triggers.yaml").read_text(encoding="utf-8"))["skills"]
        self.assertEqual(len(data), 4)
        for groups in data.values():
            self.assertEqual(len(groups["should_trigger"]) + len(groups["should_not_trigger"]), 10)
            self.assertGreaterEqual(len(groups["should_not_trigger"]), 3)

    def test_runner_never_loads_mcp_servers(self):
        argv = run_evals.command("x", "sonnet")
        self.assertIn("--strict-mcp-config", argv)
        self.assertIn('{"mcpServers":{}}', argv)

    def test_stream_parser_reads_skills_answer_and_tokens(self):
        events = [
            json.dumps({"message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "flowkit:client-meeting-recap"}}]}}),
            json.dumps({"type": "result", "result": "OK", "usage": {"input_tokens": 10, "output_tokens": 5}}),
        ]
        parsed = run_evals.parse_events(events)
        self.assertEqual(parsed["skills"], ["client-meeting-recap"])
        self.assertEqual(parsed["answer"], "OK")
        self.assertEqual(parsed["usage"], {"input_tokens": 10, "output_tokens": 5})


if __name__ == "__main__":
    unittest.main()
