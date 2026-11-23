"""Testy lokalnej warstwy bezpieczeństwa FlowKit.
Uruchom: python -m unittest tests/test_runtime.py
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
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
            "orchestrator": ["python -m unittest tests/test_a.py", "pytest -q", "dotnet test", "tsc --noEmit", "git status", "git add src/a.py", "git commit -m opis", "git push -u origin feat/a",
                             "gh pr create --fill", "python C:/x/flowkit-client-pt-prd-writer/scripts/generate_diagram.py m.yaml"],
            "analyst": ["read-document brief.docx --outline", "python /x/flowkit-client-pt-prd-writer/scripts/check_status_labels.py d.md",
                        "python /x/flowkit-client-pt-prd-writer/scripts/check_client_version.py d.docx --mode client"],
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
        result = self.run_guard("flowkit-diagnostics", "kubectl get pods")
        self.assertEqual(result.returncode, 2)
        self.assertIn("flowkit_exec.py", result.stderr)

    def test_plugin_scoped_agent_name_is_recognised(self):
        self.assertEqual(self.run_guard("flowkit:flowkit-verifier", "rm -rf build").returncode, 2)

    def test_executor_with_allowed_command_passes(self):
        command = f'python "{EXEC}" --role diagnostics -- kubectl get pods'
        self.assertEqual(self.run_guard("flowkit:flowkit-diagnostics", command).returncode, 0)

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
            self.assertEqual(self.run_guard("flowkit-diagnostics", command).returncode, 2, command)

    def test_legacy_agent_names_stay_guarded(self):
        self.assertEqual(self.run_guard("agent-3x3-verifier", "rm -rf build").returncode, 2)
        self.assertEqual(self.run_guard("flowkit:agent-3x3", "rm -rf build").returncode, 2)
        self.assertEqual(self.run_guard("agent-3x3-pm", "ls").returncode, 2)

    def test_foreign_agents_are_not_affected(self):
        self.assertEqual(self.run_guard("flowkit-my-own-agent", "rm -rf build").returncode, 0)

    def test_agents_without_execution_role_are_blocked(self):
        self.assertEqual(self.run_guard("flowkit-devops", "ls").returncode, 2)

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

    def test_source_code_and_text_files_are_read(self):
        code = self.dir / "Program.cs"
        code.write_text("namespace A {\n  // zażółć\n}\n", encoding="utf-8-sig")
        self.assertEqual(fx.document_lines(code), ["namespace A {", "  // zażółć", "}"])
        legacy = self.dir / "stary.sql"
        legacy.write_bytes("SELECT 'Łódź';".encode("cp1250"))
        self.assertEqual(fx.document_lines(legacy), ["SELECT 'Łódź';"])
        utf16 = self.dir / "App.config"
        utf16.write_text("<config/>", encoding="utf-16")
        self.assertEqual(fx.document_lines(utf16), ["<config/>"])
        binary = self.dir / "a.dll"
        binary.write_bytes(b"MZ\0\0\x90")
        with self.assertRaises(ValueError):
            fx.document_lines(binary)

    def test_rejection_hint_points_to_the_right_role_or_command(self):
        self.assertIn("verifier", fx.check("analyzer", ["pytest", "-q"]))
        self.assertIn("md-to-docx", fx.check("orchestrator", ["pandoc", "a.md"]))
        self.assertNotIn("md-to-docx", fx.check("orchestrator", ["python", "evil.py"]))

    def test_sensitive_document_is_rejected(self):
        path = self.dir / ".env"
        path.write_text("A=1", encoding="utf-8")
        with self.assertRaises(ValueError):
            fx.document_lines(path)


HAS_DOCX = importlib.util.find_spec("docx") is not None
MERMAID_SAMPLE = """```mermaid
flowchart LR
  A --> B
```
"""
DOCX_SAMPLE = """# Zakres

Tekst **ważny**.

| ID | Status |
|---|---|
| FR-001 | Wymagane |

- punkt
"""


class TestDocxWriting(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_help_and_docx_policy(self):
        for role in fx.ROLE_COMMANDS:
            self.assertIsNone(fx.check(role, ["help"]), role)
        for role in ("orchestrator", "analyst", "implementer"):
            self.assertIsNone(fx.check(role, ["md-to-docx", "a.md", "a.docx", "--template", "t.dotx"]), role)
        for role in ("analyzer", "verifier", "diagnostics"):
            self.assertIsNotNone(fx.check(role, ["md-to-docx", "a.md", "a.docx"]), role)
        for command in (["md-to-docx", "a.md", "a.md"], ["md-to-docx", "a.md"], ["md-to-docx", "a.md", "b.docx", "c.docx"],
                        ["md-to-docx", "a.md", "b.docx", "--output-file", "x"]):
            self.assertIsNotNone(fx.check("analyst", command), command)
        self.assertIn("md-to-docx", fx.check("orchestrator", ["pandoc", "a.md", "-o", "a.docx"]))

    def test_help_lists_role_commands(self):
        result = subprocess.run([sys.executable, EXEC, "--role", "analyst", "--", "help"], capture_output=True,
                                text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("md-to-docx", result.stdout)
        self.assertIn("read-document", result.stdout)

    def test_guard_allows_docx_conversion(self):
        command = f'python "{EXEC}" --role analyst -- md-to-docx dok.md dok.docx --reference-doc szablon.dotx'
        payload = {"agent_type": "flowkit-analyst", "tool_name": "Bash", "tool_input": {"command": command}}
        result = subprocess.run([sys.executable, str(ROOT / "runtime" / "guard_bash.py")], input=json.dumps(payload),
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_remote_images_are_not_fetched(self):
        import md_to_docx as md
        report = md.Report()
        text = md.resolve_images("![logo](https://example.com/a.png)", self.dir, self.dir, report)
        self.assertEqual(text, "logo")
        self.assertTrue(report.warnings)

    def test_mermaid_without_renderer_stays_as_code(self):
        import md_to_docx as md
        original = md.mermaid_commands
        md.mermaid_commands = lambda: []
        try:
            report = md.Report()
            text = md.replace_mermaid(MERMAID_SAMPLE, self.dir, report)
        finally:
            md.mermaid_commands = original
        self.assertIn("```mermaid", text)
        self.assertTrue(report.warnings)

    @unittest.skipUnless(HAS_DOCX, "wymaga python-docx")
    def test_docx_check_detects_lost_structure(self):
        import md_to_docx as md
        from docx import Document
        doc = Document()
        doc.add_paragraph("Bez nagłówków")
        doc.save(self.dir / "pusty.docx")
        report = md.Report()
        self.assertFalse(md.verify_output("# A\n\n## B\n", self.dir / "pusty.docx", None, report))
        self.assertTrue(any("FAIL" in note for note in report.notes))

    @unittest.skipUnless(HAS_DOCX, "wymaga python-docx")
    def test_document_keeps_template_styles_header_and_content(self):
        from docx import Document
        template = Document()
        template.styles["Heading 1"].font.size = 400000
        template.add_paragraph("Strona tytułowa", style="Title")
        table = template.add_table(rows=1, cols=1)
        table.style = template.styles["Light Grid Accent 1"]
        template.sections[0].footer.paragraphs[0].text = "Stopka klienta"
        template.add_paragraph("[[FLOWKIT:TREŚĆ]]")
        template.add_paragraph("Zakończenie szablonu")
        template.save(self.dir / "szablon.docx")
        (self.dir / "dok.md").write_text(DOCX_SAMPLE,
                                          encoding="utf-8")
        for option, output in (("--template", "a.docx"), ("--reference-doc", "b.docx")):
            result = subprocess.run([sys.executable, EXEC, "--role", "analyst", "--", "md-to-docx", str(self.dir / "dok.md"),
                                     str(self.dir / output), option, str(self.dir / "szablon.docx")],
                                    capture_output=True, text=True, encoding="utf-8", check=False, cwd=self.dir)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Kontrola DOCX", result.stdout)
            self.assertIn("— PASS", result.stdout)
            doc = Document(self.dir / output)
            self.assertEqual(doc.sections[0].footer.paragraphs[0].text, "Stopka klienta")
            self.assertEqual(len(doc.styles), len(template.styles))
            self.assertIn("Light Grid Accent 1", [t.style.name for t in doc.tables])
            styles = [(p.style.name, p.text) for p in doc.paragraphs]
            self.assertIn(("Heading 1", "Zakres"), styles)
            self.assertIn(("List Bullet", "punkt"), styles)
        texts = [p.text for p in Document(self.dir / "a.docx").paragraphs]
        self.assertLess(texts.index("Strona tytułowa"), texts.index("Zakres"))
        self.assertLess(texts.index("Zakres"), texts.index("Zakończenie szablonu"))
        self.assertNotIn("[[FLOWKIT:TREŚĆ]]", texts)


class TestWorkspaceBoundary(unittest.TestCase):

    def setUp(self):
        self.outside = tempfile.TemporaryDirectory()
        self.addCleanup(self.outside.cleanup)
        self.outside_dir = Path(self.outside.name).resolve()
        (self.outside_dir / "tajne.txt").write_text("x", encoding="utf-8")
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.previous = Path.cwd()
        os.chdir(self.workspace.name)
        self.addCleanup(os.chdir, self.previous)
        self.addCleanup(os.environ.pop, fx.EXTRA_PATHS_ENV, None)
        os.environ.pop(fx.EXTRA_PATHS_ENV, None)
        Path("dok.md").write_text("# A", encoding="utf-8")

    def test_paths_outside_workspace_are_rejected(self):
        outside = str(self.outside_dir / "tajne.txt")
        for argv in (["read-document", outside], ["read-document", "../tajne.txt"], ["rg", "x", outside],
                     ["grep", "-r", "x", str(self.outside_dir)], ["find", str(self.outside_dir), "-name", "*.txt"],
                     ["md-to-docx", "dok.md", "wynik.docx", "--reference-doc", str(self.outside_dir / "s.docx")],
                     ["md-to-docx", "dok.md", "wynik.docx", f"--template={self.outside_dir / 's.docx'}"],
                     ["md-to-docx", "dok.md", str(self.outside_dir / "wynik.docx")],
                     ["read-document", "~/.ssh/config"]):
            problem = fx.check("analyst" if argv[0] != "find" else "analyzer", argv)
            self.assertIsNotNone(problem, argv)
            self.assertIn("poza katalogiem roboczym", problem, argv)

    def test_paths_inside_workspace_and_non_paths_are_allowed(self):
        Path("docs").mkdir()
        for role, argv in (("analyst", ["read-document", "dok.md", "--lines", "1-20"]),
                           ("analyst", ["read-document", "./docs/../dok.md"]),
                           ("analyzer", ["git", "show", "HEAD:README.md"]),
                           ("analyzer", ["rg", "TODO", "src/app"]),
                           ("orchestrator", ["gh", "pr", "create", "--title", "feat: a/b"]),
                           ("diagnostics", ["kubectl", "get", "deployment/app", "-n", "prod", "-o", "yaml"])):
            self.assertIsNone(fx.check(role, argv), argv)

    def test_globs_are_expanded_inside_the_workspace_only(self):
        Path("diagrams").mkdir()
        for name in ("D-01-a.yaml", "D-02-b.yaml"):
            (Path("diagrams") / name).write_text("x", encoding="utf-8")
        self.assertEqual(fx.expand_globs(["python", "s.py", "diagrams/D-*.yaml", "--out", "x*"]),
                         ["python", "s.py", str(Path("diagrams/D-01-a.yaml")), str(Path("diagrams/D-02-b.yaml")),
                          "--out", "x*"])
        outside = str(self.outside_dir / "*.txt")
        self.assertEqual(fx.expand_globs(["rg", "x", outside]), ["rg", "x", outside])

    def test_extra_paths_are_configured_by_the_user(self):
        os.environ[fx.EXTRA_PATHS_ENV] = str(self.outside_dir)
        self.assertIsNone(fx.check("analyst", ["read-document", str(self.outside_dir / "tajne.txt")]))

    def test_symlink_escape_is_rejected(self):
        try:
            Path("link").symlink_to(self.outside_dir, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("system nie pozwala tworzyć dowiązań symbolicznych")
        self.assertIsNotNone(fx.check("analyst", ["read-document", "link/tajne.txt"]))

    def test_skill_script_path_is_allowed_but_its_arguments_are_checked(self):
        script = "C:/x/flowkit-client-pt-prd-writer/scripts/check_status_labels.py"
        self.assertIsNone(fx.check("analyst", ["python", script, "dok.md"]))
        self.assertIsNotNone(fx.check("analyst", ["python", script, str(self.outside_dir / "tajne.txt")]))

    def test_docx_images_outside_workspace_are_not_embedded(self):
        import md_to_docx as md
        report = md.Report()
        image = self.outside_dir / "a.png"
        image.write_bytes(b"x")
        text = md.resolve_images(f"![logo]({image.as_posix()})", Path.cwd(), Path.cwd() / "img", report)
        self.assertEqual(text, "logo")
        self.assertIn("poza katalogiem roboczym", report.warnings[0])


class TestEvalRunnerLimits(unittest.TestCase):

    def test_hanging_process_is_stopped(self):
        started = time.monotonic()
        status, _, error = run_evals.run_process([sys.executable, "-c", "import time; time.sleep(30)"], ".", 1)
        self.assertEqual(status, "TIMEOUT")
        self.assertLess(time.monotonic() - started, 15)
        self.assertIn("1 s", error)

    def test_infrastructure_errors_are_not_quality_failures(self):
        item = {"skill": "flowkit-client-meeting-recap", "prompt": "x", "expected": True}
        usage = {"input_tokens": 0, "output_tokens": 0}
        timeout = run_evals.evaluate(item, {"status": "TIMEOUT", "error": "przekroczono", "usage": usage})
        failed = run_evals.evaluate(item, {"status": "OK", "error": "", "usage": usage, "skills": [], "answer": ""})
        self.assertEqual(timeout["status"], "TIMEOUT")
        self.assertEqual(failed["status"], "FAIL")
        self.assertEqual(run_evals.summary([timeout])[1], 2)
        self.assertEqual(run_evals.summary([timeout, failed])[1], 1)

    def test_partial_results_are_saved_and_session_limit_skips_the_rest(self):
        items = [{"skill": "s", "prompt": "p", "expected": True}, {"skill": "s", "prompt": "q", "expected": False}]
        calls = []

        def fake_execute(prompt, model, baseline, dry_run, timeout):
            calls.append(prompt)
            time.sleep(0.2)
            return {"status": "OK", "error": "", "skills": ["s"], "answer": "", "finished": True,
                    "usage": {"input_tokens": 1, "output_tokens": 1}}

        original = run_evals.execute
        run_evals.execute = fake_execute
        try:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "wynik.json"
                args = argparse.Namespace(model="sonnet", dry_run=False, timeout=10, total_timeout=0.1)
                rows = run_evals.run_all(items, args, target)
                saved = json.loads(target.read_text(encoding="utf-8"))
        finally:
            run_evals.execute = original
        self.assertEqual(calls, ["p"])
        self.assertEqual([r["status"] for r in rows], ["PASS", "SKIPPED"])
        self.assertEqual(saved, rows)


class TestValidatorAndConsent(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.allow = self.dir / "allow.json"
        os.environ[fx.ALLOW_FILE_ENV] = str(self.allow)
        self.addCleanup(os.environ.pop, fx.ALLOW_FILE_ENV, None)

    def test_validator_runs_only_static_checks(self):
        for command in ("terraform fmt -check", "terraform validate", "hadolint Dockerfile", "docker compose config -q",
                        "helm lint charts/api", "helm template api charts/api", "kubeconform k8s/a.yaml",
                        "yamllint k8s", "actionlint", "shellcheck run.sh", "check-json a.json"):
            self.assertIsNone(fx.check("validator", command.split()), command)
        for command in ("terraform apply", "terraform init", "helm install api charts/api", "kubectl apply -f a.yaml",
                        "docker push api", "docker compose up", "helm template api charts/api --dependency-update",
                        "kubectl get pods --kubeconfig x", "git commit -m x", "pytest -q"):
            self.assertIsNotNone(fx.check("validator", command.split()), command)

    def test_check_json_reports_each_file(self):
        good, bad = self.dir / "a.json", self.dir / "b.json"
        good.write_text('{"a": 1}', encoding="utf-8")
        bad.write_text("{a:", encoding="utf-8")
        result = subprocess.run([sys.executable, EXEC, "--role", "validator", "--", "check-json", "a.json", "b.json"],
                                capture_output=True, text=True, encoding="utf-8", check=False, cwd=self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("PASS a.json", result.stdout)
        self.assertIn("FAIL b.json", result.stdout)
        self.assertIn("[kod wyjścia: 1]", result.stdout)

    def test_missing_tool_is_not_run(self):
        result = subprocess.run([sys.executable, EXEC, "--role", "validator", "--", "tflint"], capture_output=True,
                                text=True, encoding="utf-8", check=False,
                                env={**os.environ, "PATH": str(self.dir)})
        self.assertIn("NOT_RUN", result.stdout)

    def test_user_consent_allows_listed_commands_only(self):
        self.allow.write_text(json.dumps({"commands": {"*": ["make lint"], "orchestrator": ["dotnet build", "terraform plan",
                                                                                              "bash", "node", "python -c"]}}),
                              encoding="utf-8")
        self.assertIsNone(fx.check("orchestrator", ["dotnet", "build", "src/App.sln"]))
        self.assertIsNone(fx.check("analyst", ["make", "lint"]))
        self.assertIsNotNone(fx.check("analyst", ["dotnet", "build"]))
        for argv in (["bash", "-c", "ls"], ["node", "x.js"], ["python", "-c", "print(1)"], ["terraform", "apply"]):
            self.assertIsNotNone(fx.check("orchestrator", argv), argv)
        allowed, ignored = fx.user_allowed("orchestrator")
        self.assertEqual(allowed, ["make lint", "dotnet build", "terraform plan"])
        self.assertEqual(len(ignored), 3)

    def test_consent_keeps_hard_limits(self):
        self.allow.write_text(json.dumps({"commands": {"orchestrator": ["cat", "git push", "kubectl get"]}}), encoding="utf-8")
        self.assertIsNotNone(fx.check("orchestrator", ["cat", str(Path.home() / "x.txt")]))
        self.assertIsNotNone(fx.check("orchestrator", ["cat", ".env"]))
        self.assertIsNotNone(fx.check("orchestrator", ["git", "push", "-u", "origin", "main"]))
        self.assertIsNotNone(fx.check("orchestrator", ["kubectl", "get", "secret", "db"]))

    def test_rejection_explains_how_to_allow(self):
        problem = fx.check("orchestrator", ["terraform", "plan"])
        self.assertIn('"terraform plan"', problem)
        self.assertIn(str(self.allow), problem)

    def test_broken_consent_file_grants_nothing(self):
        self.allow.write_text("{nie json", encoding="utf-8")
        self.assertIsNotNone(fx.check("orchestrator", ["dotnet", "build"]))
        self.assertTrue(fx.user_allowed("orchestrator")[1])

    def run_guard(self, payload):
        return subprocess.run([sys.executable, str(ROOT / "runtime" / "guard_bash.py")], input=json.dumps(payload),
                              capture_output=True, text=True, encoding="utf-8", check=False,
                              env={**os.environ, fx.ALLOW_FILE_ENV: str(self.allow)})

    def test_agents_cannot_edit_consent_file_or_runtime(self):
        for agent in ("flowkit-orchestrator", "flowkit-devops", "flowkit:flowkit-implementer"):
            for path in (str(self.allow), str(ROOT / "runtime" / "flowkit_exec.py")):
                result = self.run_guard({"agent_type": agent, "tool_name": "Write", "tool_input": {"file_path": path}})
                self.assertEqual(result.returncode, 2, (agent, path))
        allowed = self.run_guard({"agent_type": "flowkit-devops", "tool_name": "Edit",
                                  "tool_input": {"file_path": str(self.dir / "k8s.yaml")}})
        self.assertEqual(allowed.returncode, 0)
        user = self.run_guard({"tool_name": "Write", "tool_input": {"file_path": str(self.allow)}})
        self.assertEqual(user.returncode, 0)


class TestRolePermissionContract(unittest.TestCase):

    def test_agents_runtime_roles_and_guard_agree(self):
        import build_agents
        self.assertEqual(build_agents.EXEC_ROLES, guard.ROLES)
        for agent, role in build_agents.EXEC_ROLES.items():
            self.assertIn(role, fx.ROLE_COMMANDS, agent)
            self.assertIn("Bash", build_agents.CLAUDE_TOOLS[agent], agent)
            source = (ROOT / "agents" / f"{agent}_agent.md").read_text(encoding="utf-8")
            self.assertIn("execute", yaml.safe_load(source.split("---", 2)[1])["tools"], agent)
        for agent in set(build_agents.AGENTS) - set(build_agents.EXEC_ROLES):
            self.assertNotIn("Bash", build_agents.CLAUDE_TOOLS[agent], agent)

    def test_read_only_roles_cannot_write_or_deliver(self):
        for role in ("analyzer", "verifier", "diagnostics", "validator"):
            for command in (["md-to-docx", "a.md", "a.docx"], ["git", "commit", "-m", "x"], ["git", "push", "-u", "origin", "a"]):
                self.assertIsNotNone(fx.check(role, command), (role, command))


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
        for path in (ROOT / "agents" / "adapters" / "claude-code").glob("flowkit-*.md"):
            data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            if data["name"] == "flowkit-orchestrator":
                continue
            self.assertEqual(data["model"], "sonnet", path.name)
            self.assertGreater(data["maxTurns"], 0, path.name)

    def test_agents_with_bash_have_guard_hook(self):
        for path in (ROOT / "agents" / "adapters" / "claude-code").glob("*.md"):
            data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            if "Bash" in data["tools"]:
                self.assertIn("guard_bash.py", json.dumps(data["hooks"]), path.name)

    def test_plugin_hook_guards_bash(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"][0]
        self.assertEqual(hooks["matcher"], "Bash|Edit|Write|MultiEdit|NotebookEdit")
        self.assertIn("guard_bash.py", hooks["hooks"][0]["command"])

    def test_orchestrator_procedures_exist(self):
        source = (ROOT / "agents" / "flowkit-orchestrator_agent.md").read_text(encoding="utf-8")
        names = set(re.findall(r"`([a-z-]+\.md)`", source)) - {"flowkit-project.md"}
        self.assertEqual(len(names), 6)
        for name in names:
            self.assertTrue((ROOT / "runtime" / "procedures" / name).exists(), name)


class TestEvalRunner(unittest.TestCase):

    def test_trigger_set_has_positive_and_negative_cases(self):
        data = yaml.safe_load((ROOT / "tests" / "evals" / "triggers.yaml").read_text(encoding="utf-8"))["skills"]
        self.assertEqual(len(data), 5)
        for groups in data.values():
            self.assertEqual(len(groups["should_trigger"]) + len(groups["should_not_trigger"]), 10)
            self.assertGreaterEqual(len(groups["should_not_trigger"]), 3)

    def test_runner_never_loads_mcp_servers(self):
        argv = run_evals.command("x", "sonnet")
        self.assertIn("--strict-mcp-config", argv)
        self.assertIn('{"mcpServers":{}}', argv)

    def test_stream_parser_reads_skills_answer_and_tokens(self):
        events = [
            json.dumps({"message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "flowkit:flowkit-client-meeting-recap"}}]}}),
            json.dumps({"type": "result", "result": "OK", "usage": {"input_tokens": 10, "output_tokens": 5}}),
        ]
        parsed = run_evals.parse_events(events)
        self.assertEqual(parsed["skills"], ["flowkit-client-meeting-recap"])
        self.assertEqual(parsed["answer"], "OK")
        self.assertEqual(parsed["usage"], {"input_tokens": 10, "output_tokens": 5})


if __name__ == "__main__":
    unittest.main()
