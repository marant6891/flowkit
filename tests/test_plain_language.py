"""Testy kontroli prostego języka (runtime/plain_language.py i polecenie plain-check).
Uruchom: python -m unittest tests/test_plain_language.py
"""
import io
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "plain_language"
sys.path.insert(0, str(ROOT / "runtime"))

import flowkit_exec as fx  # noqa: E402
import plain_language as pl  # noqa: E402


def ids(findings) -> set[str]:
    return {f.rule_id for f in findings}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class TestRules(unittest.TestCase):
    def test_polish_bad_fixture_hits_rules_from_all_three_sources(self):
        found = ids(pl.check_text(fixture("pl-bad.md"), strict=True))
        gov = {"PL-W1", "PL-W3", "PL-W6", "PL-W7", "PL-Z1", "PL-S4"}
        ojuw = {"PL-K1", "PL-K2"}
        pan = {"PL-P4", "PL-P5", "PL-P6", "PL-P7", "PL-P8"}
        self.assertLessEqual(gov | ojuw | pan | {"NS-1"}, found)

    def test_good_fixtures_are_clean(self):
        for name in ("pl-good.md", "en-good.md"):
            self.assertEqual([], pl.check_text(fixture(name), strict=True), name)

    def test_english_bad_fixture(self):
        found = ids(pl.check_text(fixture("en-bad.md")))
        self.assertLessEqual({"EN-W1", "EN-W2", "EN-W5", "EN-K1", "EN-K4", "EN-F1", "EN-F3", "EN-F6", "EN-F7", "NS-3"},
                             found)

    def test_language_rules_do_not_leak(self):
        self.assertFalse(any(f.rule_id.startswith("EN-") for f in pl.check_text(fixture("pl-bad.md"))))
        self.assertFalse(any(f.rule_id.startswith("PL-") for f in pl.check_text(fixture("en-bad.md"))))

    def test_language_detection(self):
        self.assertEqual("pl", pl.detect_language(fixture("pl-good.md")))
        self.assertEqual("en", pl.detect_language(fixture("en-good.md")))

    def test_draft_mode_reports_only_warnings(self):
        findings = pl.check_text(fixture("pl-bad.md"))
        self.assertTrue(findings)
        self.assertEqual({pl.WARN}, {f.level for f in findings})
        self.assertIn(pl.FAIL, {f.level for f in pl.check_text(fixture("pl-bad.md"), strict=True)})

    def test_calques_stay_warnings_in_final_mode(self):
        """OJ UW: kalki oceniamy przypadek po przypadku, więc nigdy nie blokują wyniku."""
        for f in pl.check_text(fixture("pl-bad.md"), strict=True):
            if f.rule_id.startswith(("PL-K", "PL-P")):
                self.assertEqual(pl.WARN, f.level, f.rule_id)

    def test_sentence_length_thresholds(self):
        words = lambda n: " ".join(["słowo"] * n) + "."  # noqa: E731
        self.assertEqual([], pl.check_text(words(20), lang="pl", strict=True))
        self.assertEqual([pl.WARN], [f.level for f in pl.check_text(words(21), lang="pl", strict=True)])
        self.assertEqual([pl.FAIL], [f.level for f in pl.check_text(words(36), lang="pl", strict=True)])
        self.assertEqual([], pl.check_text(" ".join(["word"] * 25) + ".", lang="en", strict=True))

    def test_wrapped_paragraph_counts_as_one_sentence_with_its_first_line(self):
        text = "Intro.\n\n" + "\n".join(["jeden dwa trzy cztery pięć sześć siedem"] * 4) + "."
        findings = pl.check_text(text, lang="pl")
        self.assertEqual([("PL-Z1", 3)], [(f.rule_id, f.line) for f in findings])

    def test_code_urls_quotes_and_placeholders_are_exempt(self):
        text = ("Uruchom `w dniu dzisiejszym — niniejszy`.\n\n```\nASAP — dokonać zmiany\n```\n\n"
                "Klient napisał: „zaparkujmy temat”. Zobacz https://example.com/a—b oraz [DO UZUPEŁNIENIA: NFR].")
        self.assertEqual([], pl.check_text(text, lang="pl", strict=True))

    def test_frontmatter_and_disabled_regions_are_exempt(self):
        text = ("---\nname: x\ndescription: " + "słowo " * 40 + "\n---\n\nDziś działa.\n\n"
                "<!-- plain-check: off -->\n| W dniu dzisiejszym | Dziś |\n<!-- plain-check: on -->\n\nNiniejszy raport.\n")
        self.assertEqual([("PL-W6", 12)], [(f.rule_id, f.line) for f in pl.check_text(text, lang="pl")])

    def test_repository_docs_and_skill_files_pass_final_mode(self):
        """Etap 6: dokumentacja i pliki skilli nie łamią reguł FAIL (półpauzy, zdania powyżej 35 słów, wata)."""
        paths = [ROOT / name for name in ("README.md", "DEVELOPMENT.md", "CONTRIBUTING.md", "SECURITY.md")]
        paths += [ROOT / "docs" / "USAGE.md", ROOT / "runtime" / "procedures" / "plain-language.md"]
        for pattern in ("flowkit-*/SKILL.md", "flowkit-*/checklists/*.md", "flowkit-*/references/*.md"):
            paths += sorted((ROOT / "skills").glob(pattern))
        for path in paths:
            failures = [(f.rule_id, f.line) for f in pl.check_text(path.read_text(encoding="utf-8"), strict=True)
                        if f.level == pl.FAIL]
            self.assertEqual([], failures, path.relative_to(ROOT).as_posix())

    def test_table_cells_and_list_items_are_separate_sentences(self):
        text = "| Kolumna | Opis |\n|---|---|\n| A | Niniejszy raport |\n\n- pierwszy punkt\n- celem weryfikacji danych"
        found = [(f.rule_id, f.line) for f in pl.check_text(text, lang="pl")]
        self.assertEqual([("PL-W6", 3), ("PL-W5", 6)], found)

    def test_abbreviation_explained_anywhere_or_in_glossary_is_fine(self):
        self.assertEqual([], pl.check_text("Wymagania niefunkcjonalne (NFR) są gotowe. NFR są w załączniku.", lang="pl"))
        self.assertEqual([], pl.check_text("NFR (wymagania niefunkcjonalne) są gotowe.", lang="pl"))
        self.assertEqual(["PL-S4"], [f.rule_id for f in pl.check_text("NFR są gotowe. NFR są w załączniku.", lang="pl")])
        self.assertEqual([], pl.check_text("API i SQL działają.", lang="pl"))

    def test_project_glossary(self):
        glossary = pl.load_glossary(FIXTURES / "glossary-project.md")
        self.assertLessEqual({"KSeF", "ZUS", "WMS", "HPA"}, glossary)
        self.assertNotIn("Nazwa projektu", glossary)
        text = "Dane z ZUS trafiają do WMS przez HPA."
        self.assertEqual({"PL-S4"}, ids(pl.check_text(text, lang="pl")))
        self.assertEqual([], pl.check_text(text, lang="pl", glossary=glossary))

    def test_shouting_is_reported_once(self):
        findings = pl.check_text("UWAGA TO JEST BARDZO WAŻNE dla zespołu.", lang="pl")
        self.assertEqual(["NS-4"], [f.rule_id for f in findings])

    def test_user_audience_rules(self):
        text = "Komponent raportu pokazuje sumy."
        self.assertEqual([], pl.check_text(text, lang="pl"))
        self.assertEqual(["PL-W8"], [f.rule_id for f in pl.check_text(text, lang="pl", audience="user")])

    def test_no_false_positives_on_legitimate_phrases(self):
        ok_pl = ("Wyślę raport na koniec dnia. Użyliśmy nowej wersji. Celem projektu jest migracja. "
                 "Po raz drugi system działa. To, co ważne, opisaliśmy w punkcie 2.")
        self.assertEqual(set(), ids(pl.check_text(ok_pl, lang="pl")) - {"PL-P6"})
        ok_en = "Eventually the job finished. We actually tested it. The actual cause was a timeout."
        self.assertEqual([], pl.check_text(ok_en, lang="en"))

    def test_every_rule_id_is_documented_in_the_standard(self):
        standard = (ROOT / "runtime" / "procedures" / "plain-language.md").read_text(encoding="utf-8")
        documented = set(re.findall(r"\b(?:PL|EN|NS)-[A-Z]\d+\b|\bNS-\d+\b", standard))
        for rule in pl.RULES:
            self.assertIn(rule.rule_id, documented, rule.rule_id)
        for rule_id in ("PL-Z1", "EN-Z1", "PL-S4", "EN-S4"):
            self.assertIn(rule_id, documented)


class TestSkillCoverage(unittest.TestCase):
    """Prosty język obejmuje wszystkie skille, ich prompty VS Code i redaktora maili."""

    def skills(self) -> list[Path]:
        return sorted(p for p in (ROOT / "skills").glob("flowkit-*") if p.is_dir())

    def test_every_skill_references_standard_and_checks_it(self):
        self.assertGreaterEqual(len(self.skills()), 8)
        for skill in self.skills():
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("procedures/plain-language.md", text, skill.name)
            self.assertTrue("plain-check" in text or "scripts/check_" in text, skill.name)

    def test_every_skill_prompt_references_standard(self):
        for skill in self.skills():
            prompt = ROOT / ".github" / "prompts" / f"{skill.name}.prompt.md"
            self.assertIn("plain-language.md", prompt.read_text(encoding="utf-8"), skill.name)

    def test_skill_templates_pass_final_mode(self):
        """Szablony zapasowe kształtują wynik dla klienta, więc nie mogą łamać reguł FAIL (np. półpauzy)."""
        templates = sorted((ROOT / "skills").glob("flowkit-*/templates/*.md"))
        self.assertTrue(templates)
        for path in templates:
            failures = [f for f in pl.check_text(path.read_text(encoding="utf-8"), strict=True) if f.level == pl.FAIL]
            self.assertEqual([], failures, path.relative_to(ROOT).as_posix())

    def test_plain_language_evals_cover_both_languages(self):
        import yaml

        cases = {c["id"]: c for c in yaml.safe_load((ROOT / "tests" / "evals" / "cases.yaml").read_text(encoding="utf-8"))["cases"]}
        for case_id in ("message-editor-plain-pl", "message-editor-plain-en"):
            case = cases[case_id]
            draft = (ROOT / "tests" / "fixtures" / case["fixture"]).read_text(encoding="utf-8")
            hits = [p for p in case["must_not_contain"] if re.search(p, draft)]
            self.assertGreaterEqual(len(hits), 8, case_id)  # szkic naprawdę zawiera to, czego wynik ma nie mieć
            self.assertTrue(pl.check_text(draft), case_id)

    def test_eval_cases_are_graded_offline_with_golden_answers(self):
        """Bez API: grader ocenia wzorcową odpowiedź; szkic nie przechodzi, wzorzec przechodzi wszystkie kontrole."""
        sys.path.insert(0, str(ROOT / "scripts"))
        sys.path.insert(0, str(ROOT / "skills" / "flowkit-client-message-editor" / "scripts"))
        import check_message as cm
        import grade_eval

        cases = grade_eval.load_cases()
        for golden in sorted((FIXTURES / "golden").glob("*.md")):
            case = cases[golden.stem]
            answer = golden.read_text(encoding="utf-8")
            draft = (ROOT / "tests" / "fixtures" / case["fixture"]).read_text(encoding="utf-8")
            self.assertEqual([], grade_eval.grade(case, answer), golden.name)
            self.assertTrue(grade_eval.grade(case, draft), golden.name)
            self.assertEqual([], pl.check_text(answer, strict=True), golden.name)
            self.assertEqual([], cm.check(answer, final=True)[0], golden.name)
        self.assertEqual({"message-editor-plain-pl", "message-editor-plain-en"},
                         {p.stem for p in (FIXTURES / "golden").glob("*.md")})

    def test_text_producing_agents_follow_standard(self):
        for agent in ("flowkit-orchestrator", "flowkit-analyst", "flowkit-verifier", "flowkit-product-owner"):
            for path in (ROOT / "agents" / f"{agent}_agent.md", ROOT / "agents" / "adapters" / "claude-code" / f"{agent}.md",
                         ROOT / "agents" / "adapters" / "vscode" / f"{agent}.agent.md"):
                self.assertIn("plain-language.md", path.read_text(encoding="utf-8"), path.name)
        verifier = (ROOT / "agents" / "flowkit-verifier_agent.md").read_text(encoding="utf-8")
        self.assertIn("plain-check <document> --strict", verifier)
        self.assertIn("plain-language.md", (ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8"))
        for path in (ROOT / "agents" / "core").glob("*.md"):
            self.assertNotIn("Natural style", path.read_text(encoding="utf-8"), path.name)

    def test_skill_scripts_load_shared_module(self):
        import importlib.util

        for script in ("flowkit-client-message-editor/scripts/check_message.py",
                       "flowkit-client-solution-docs-writer/scripts/check_user_docs.py"):
            spec = importlib.util.spec_from_file_location(Path(script).stem + "_plain", ROOT / "skills" / script)
            module = importlib.util.module_from_spec(spec)
            sys.path.insert(0, str((ROOT / "skills" / script).parent))
            spec.loader.exec_module(module)
            self.assertIsNotNone(module.load_plain_language(), script)

    def test_message_editor_reports_plain_language_in_both_languages(self):
        sys.path.insert(0, str(ROOT / "skills" / "flowkit-client-message-editor" / "scripts"))
        import check_message as cm

        errors, warnings = cm.check("Dzień dobry,\n\nniniejszym przesyłam raport. Zaparkujmy temat do piątku.\n")
        self.assertEqual([], errors)
        self.assertTrue(any("PL-W6" in w for w in warnings))
        self.assertTrue(any("PL-K1" in w for w in warnings))
        errors, _ = cm.check("Dzień dobry,\n\nniniejszym przesyłam raport.\n", final=True)
        self.assertTrue(any("PL-W6" in e for e in errors))
        _, warnings = cm.check("Hello,\n\nIn the attachment I send the actual version of the plan.\n", lang="en")
        self.assertTrue(any("EN-F9" in w for w in warnings) and any("EN-F1" in w for w in warnings))


class TestCommand(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out):
            code = pl.main(list(args))
        return code, out.getvalue()

    def test_exit_codes(self):
        self.assertEqual(0, self.run_main(str(FIXTURES / "pl-bad.md"))[0])
        code, output = self.run_main(str(FIXTURES / "pl-bad.md"), "--strict")
        self.assertEqual(1, code)
        self.assertRegex(output, r"FAIL PL-W3 .*pl-bad\.md:3:")
        self.assertIn("tryb końcowy", output)
        self.assertEqual(0, self.run_main(str(FIXTURES / "pl-good.md"), "--strict")[0])
        self.assertEqual(2, self.run_main(str(FIXTURES / "brak.md"))[0])

    def test_glossary_from_flowkit_project_in_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "note.md"
            note.write_text("Dane z ZUS są gotowe.", encoding="utf-8")
            (Path(tmp) / "flowkit-project.md").write_text(fixture("glossary-project.md"), encoding="utf-8")
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                code, output = self.run_main("note.md")
            finally:
                os.chdir(cwd)
        self.assertEqual(0, code)
        self.assertNotIn("PL-S4", output)

    def test_docx_is_read_through_executor(self):
        try:
            import docx
        except ImportError:
            self.skipTest("python-docx niedostępny")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.docx"
            document = docx.Document()
            document.add_paragraph("W dniu dzisiejszym wysyłamy raport.")
            document.save(path)
            code, output = self.run_main(str(path), "--strict")
        self.assertEqual(1, code)
        self.assertIn("PL-W3", output)

    def test_executor_allows_plain_check_for_text_roles_only(self):
        for role in ("orchestrator", "verifier", "analyst", "implementer"):
            self.assertIsNone(fx.check(role, ["plain-check", "docs/a.md", "--strict"]), role)
        self.assertIsNotNone(fx.check("validator", ["plain-check", "docs/a.md"]))
        self.assertIn("plain-check", fx.BUILTINS)

    def test_executor_runs_plain_check(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = fx.run(["plain-check", str(FIXTURES / "pl-bad.md"), "--strict"], role="verifier")
        self.assertEqual(1, code)
        self.assertIn("PL-W1", out.getvalue())
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(2, fx.run(["plain-check", "--lang", "xx", "a.md"], role="verifier"))


if __name__ == "__main__":
    unittest.main()
