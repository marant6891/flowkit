"""Testy skilla flowkit-client-solution-docs-writer.
Uruchom: python -m unittest tests/test_solution_docs.py
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "flowkit-client-solution-docs-writer"
SCRIPT = SKILL / "scripts" / "check_user_docs.py"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))

import check_user_docs as cu  # noqa: E402
import flowkit_exec as fx  # noqa: E402

EXAMPLE = (SKILL / "examples" / "code-to-help-example.md").read_text(encoding="utf-8")
GOOD_TOPIC = re.search(r"```markdown\n(.*?)```", EXAMPLE, re.S).group(1)
BAD_TOPIC = re.search(r"^> (.*?)\n\n", EXAMPLE, re.S | re.M).group(1).replace("\n> ", " ")

CLIENT_DOC = """# Pomoc: Zwroty

## 1. Zgłaszanie zwrotu

1. Wybierz **Zamówienia** > **Moje zamówienia**.
2. Kliknij **Zgłoś zwrot**.

Kontakt z obsługą: Do ustalenia (K-01).

## 2. Kwestie do wyjaśnienia

| Nr | Kwestia | Czego dotyczy | Kto decyduje |
|---|---|---|---|
| K-01 | Kontakt do obsługi | Rozdział 1 | Zamawiający |
"""


def run(text: str, audience: str = "user", mode: str = "draft"):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "doc.md"
        path.write_text(text, encoding="utf-8")
        return cu.check_file(path, audience, mode)


class TestCheckUserDocs(unittest.TestCase):

    def test_good_example_passes_in_draft(self):
        errors, warnings = run(GOOD_TOPIC)
        self.assertEqual(errors, [])
        self.assertTrue(any("OPEN-003" in w for w in warnings))  # brak wiersza w Tematach do wyjaśnienia

    def test_bad_example_uses_code_language(self):
        errors, _ = run(BAD_TOPIC)
        self.assertIn("endpoint API", " | ".join(errors))

    def test_draft_markers_fail_in_client_mode(self):
        errors, _ = run(GOOD_TOPIC, mode="client")
        joined = " | ".join(errors)
        self.assertIn("zrzutu", joined)
        self.assertIn("DO POTWIERDZENIA", joined)
        self.assertIn("oznaczenie źródła", joined)

    def test_clean_client_version_passes(self):
        self.assertEqual(run(CLIENT_DOC, mode="client")[0], [])

    def test_client_reference_without_item_fails(self):
        errors, _ = run(CLIENT_DOC.replace("| K-01 | Kontakt", "| K-02 | Kontakt"), mode="client")
        self.assertTrue(any("K-01 bez punktu" in e for e in errors))

    def test_final_mode_rejects_open_questions(self):
        errors, _ = run(CLIENT_DOC.split("## 2.")[0], mode="final")
        self.assertTrue(any("K-01" in e for e in errors))

    def test_secrets_are_errors_for_every_audience(self):
        for audience in ("user", "admin", "tech"):
            self.assertTrue(run("Ustaw `Db:Password=Sup3rTajne` w konfiguracji.", audience)[0], audience)
            self.assertTrue(run("Adres bazy: postgres://app:Sekret12@db:5432/app", audience)[0], audience)

    def test_internal_host_is_error_only_for_user_help(self):
        text = "Otwórz http://localhost:5000 w przeglądarce."
        self.assertTrue(run(text, "user")[0])
        errors, warnings = run(text, "tech")
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_admin_may_name_settings_and_files(self):
        text = "| `Returns:MaxDays` | Liczba dni na zwrot | 30 | Dotyczy nowych zgłoszeń |\n\nPlik `appsettings.json`."
        self.assertEqual(run(text, "admin")[0], [])
        self.assertTrue(run("Plik appsettings.json zawiera ustawienia.", "user")[0])

    def test_long_step_and_ai_phrase_are_warnings(self):
        step = "1. " + " ".join(["słowo"] * 35)
        _, warnings = run(step + "\n\nNiniejszy dokument opisuje zwroty.")
        joined = " | ".join(warnings)
        self.assertIn("krok ma", joined)
        self.assertIn("formułka", joined)

    def test_code_blocks_are_ignored(self):
        self.assertEqual(run("```\nGET /api/orders\n```\n")[0], [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "ok.md"
            good.write_text(CLIENT_DOC, encoding="utf-8")
            bad = Path(tmp) / "bad.md"
            bad.write_text(BAD_TOPIC, encoding="utf-8")
            ok = subprocess.run([sys.executable, str(SCRIPT), str(good), "--mode", "client"],
                                capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(ok.returncode, 0, ok.stdout)
            self.assertIn("PASS", ok.stdout)
            fail = subprocess.run([sys.executable, str(SCRIPT), str(bad)], capture_output=True, text=True,
                                  encoding="utf-8")
            self.assertEqual(fail.returncode, 1)

    def test_docx_is_checked(self):
        try:
            import docx
        except ImportError:
            self.skipTest("brak python-docx")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pomoc.docx"
            document = docx.Document()
            document.add_heading("Zgłaszanie zwrotu", 1)
            document.add_paragraph("Kliknij Zgłoś zwrot. [ZRZUT: formularz]")
            document.save(path)
            errors, _ = cu.check_file(path, "user", "final")
            self.assertTrue(any("zrzutu" in e for e in errors))


class TestSkillWiring(unittest.TestCase):

    def test_executor_allows_check_script(self):
        self.assertIn("check_user_docs.py", fx.SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertIn("check_user_docs.py", fx.READONLY_SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertIsNone(fx.check("analyst", ["python", str(SCRIPT), "pomoc.md", "--mode", "client"]))

    def test_docx_engine_reference_is_shared_copy(self):
        ours = (SKILL / "references" / "docx-engine.md").read_text(encoding="utf-8")
        theirs = (ROOT / "skills" / "flowkit-client-pt-prd-writer" / "references" / "docx-engine.md").read_text(
            encoding="utf-8")
        self.assertEqual(ours, theirs)

    def test_example_facts_come_from_fixture(self):
        fixture = (ROOT / "tests" / "fixtures" / "app" / "returns" / "pl.json").read_text(encoding="utf-8")
        for label in ("Zgłoś zwrot", "Wyślij zgłoszenie", "Oczekuje na akceptację", "Minął termin zwrotu"):
            self.assertIn(label, fixture)
            self.assertIn(label, GOOD_TOPIC)


if __name__ == "__main__":
    unittest.main()
