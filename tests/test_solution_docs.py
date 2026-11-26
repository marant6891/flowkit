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

    def test_client_and_final_reject_raw_mermaid_and_diagram_marker(self):
        doc = "# Pomoc\n\n## 1. Przepływ\n\n[[DIAGRAM:D-01]]\n\n```mermaid\nflowchart LR\n  A --> B\n```\n"
        for mode in ("client", "final"):
            errors, _ = run(doc, audience="tech", mode=mode)
            joined = " | ".join(errors)
            self.assertIn("znacznik diagramu", joined)
            self.assertIn("surowy blok mermaid", joined)

    def test_stub_section_triggers_warning(self):
        doc = "# Dokumentacja\n\n## 1. Wprowadzenie\n\nDokument opisuje integrację.\n"
        _, warnings = run(doc, audience="tech", mode="final")
        self.assertTrue(any("ma tylko" in w for w in warnings))

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

    def test_working_sections_are_exempt_only_in_draft(self):
        doc = ("# Pomoc\n\n## 1. Logowanie\n\nKliknij **Zaloguj**.\n\n"
               "## Załącznik B. Materiały źródłowe\n\n| SRC-001 | views/login/login.html | Strona logowania |\n\n"
               "## 2. Wylogowanie\n\nPlik login.html.\n")
        errors, _ = run(doc, mode="draft")
        self.assertEqual(len(errors), 1)  # tylko rozdział 2 po sekcji roboczej
        self.assertIn("login.html", errors[0])
        self.assertGreater(len(run(doc, mode="client")[0]), 1)

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


CATALOG = """| ID | Element (nazwa w interfejsie) | Rodzaj | Gdzie | Co robi lub co znaczy | Warunek | Funkcja | Status | Źródło |
|---|---|---|---|---|---|---|---|---|
| OPT-001 | **Zgłoś zwrot** | przycisk | lista zamówień | Otwiera formularz | brak | FEAT-001 | opisana | pl.json |
| OPT-002 | **Powód zwrotu** | pole | formularz | Wymagany wybór | brak | FEAT-001 | opisana | routes.py:27 |
| OPT-003 | **Akceptuj częściowo** | przycisk | panel kierownika | Brak działania | rola | FEAT-002 | pominięta: nieukończona | routes.py:44 |
"""


class TestCheckCoverage(unittest.TestCase):

    def files(self, document: str):
        import check_coverage as cc
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        doc = Path(tmp.name) / "pomoc.md"
        doc.write_text(document, encoding="utf-8")
        catalog = Path(tmp.name) / "katalog.md"
        catalog.write_text(CATALOG, encoding="utf-8")
        return cc.check(doc, catalog)

    def test_skipped_items_are_not_required(self):
        errors, _, stats = self.files(GOOD_TOPIC + "\n| **Powód zwrotu** | Tak | Wybór z listy |\n")
        self.assertEqual(errors, [])
        self.assertEqual((stats["total"], stats["required"], stats["skipped"]), (3, 2, 1))

    def test_missing_option_fails(self):
        errors, _, _ = self.files("# Zwroty\n\nKliknij **Zgłoś zwrot**.\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("OPT-002", errors[0])

    def test_no_pictures_in_large_help_is_warning(self):
        text = "# A\n\nZgłoś zwrot, Powód zwrotu\n\n# B\n\ntekst\n\n# C\n\ntekst\n"
        _, warnings, _ = self.files(text)
        self.assertTrue(any("rysunku" in w for w in warnings))
        _, warnings, stats = self.files(text + "\n[[DIAGRAM:D-01]]\n")
        self.assertEqual(warnings, [])
        self.assertEqual(stats["images"], 1)


DRAFT = """# Pomoc

**Uwaga dla zespołu (wersja robocza):** nazwy są robocze.
Do sprawdzenia z eksportem.

## 1. Logowanie

1. Otwórz adres aplikacji w przeglądarce. (OPEN-002: adres)
2. Kliknij **Zaloguj**.

[ZRZUT: Strona logowania, pusty formularz]

(SRC-001, login.html:168-256)

## 2. Wylogowanie

Wybierz **Wyloguj**. DO POTWIERDZENIA (OPEN-004: położenie panelu).

## 3. Tematy do wyjaśnienia

| ID | Temat | Czego brakuje | Kto |
|---|---|---|---|
| OPEN-004 | Wylogowanie | Położenie panelu | Zespół |

## Załącznik A. Robocze nazwy

| Nazwa | Klucz |
|---|---|
| Zaloguj | login.LOG |
"""


class TestMakeClientVersion(unittest.TestCase):

    def setUp(self):
        import make_client_version as mcv
        self.mcv = mcv

    def test_final_refuses_open_gaps(self):
        _, _, gaps = self.mcv.convert(DRAFT, "final")
        self.assertEqual(len(gaps), 1)
        self.assertIn("OPEN-004", gaps[0])

    def test_final_output_is_clean_and_register_keeps_sources(self):
        draft = DRAFT.replace(" DO POTWIERDZENIA (OPEN-004: położenie panelu).", " (OPEN-004: położenie panelu)")
        body, register, gaps = self.mcv.convert(draft, "final")
        self.assertEqual(gaps, [])
        for marker in ("SRC-", "OPEN-", "ZRZUT", "Uwaga dla zespołu", "Tematy do wyjaśnienia", "Załącznik A",
                       "login.html", "Do sprawdzenia z eksportem"):
            self.assertNotIn(marker, body, marker)
        self.assertIn("Otwórz adres aplikacji w przeglądarce.", body)
        self.assertIn("Kliknij **Zaloguj**.", body)
        self.assertIn("SRC-001, login.html:168-256", register)
        self.assertIn("[ZRZUT: Strona logowania", register)
        self.assertIn("login.LOG", register)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pomoc.md"
            path.write_text(body, encoding="utf-8")
            self.assertEqual(cu.check_file(path, "user", "final")[0], [])

    def test_client_mode_turns_gaps_into_questions(self):
        body, _, gaps = self.mcv.convert(DRAFT, "client")
        self.assertEqual(gaps, [])
        self.assertIn("Do ustalenia (K-01).", body)
        self.assertIn("| K-01 | Wylogowanie |", body)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pomoc.md"
            path.write_text(body, encoding="utf-8")
            self.assertEqual(cu.check_file(path, "user", "client")[0], [])


class TestSkillWiring(unittest.TestCase):

    def test_executor_allows_check_script(self):
        self.assertIn("check_user_docs.py", fx.SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertIn("check_user_docs.py", fx.READONLY_SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertIn("check_coverage.py", fx.SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertIn("check_coverage.py", fx.READONLY_SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertIn("make_client_version.py", fx.SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
        self.assertNotIn("make_client_version.py", fx.READONLY_SKILL_SCRIPTS["flowkit-client-solution-docs-writer"])
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
