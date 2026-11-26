"""Testy skilla flowkit-client-message-editor.
Uruchom: python -m unittest tests/test_message_editor.py
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "flowkit-client-message-editor"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))

import check_message as cm  # noqa: E402
import flowkit_exec as fx  # noqa: E402

DRAFT = (ROOT / "tests" / "fixtures" / "messages" / "draft_scope_change.txt").read_text(encoding="utf-8")
EXAMPLES = (SKILL / "examples" / "rewrite-examples.md").read_text(encoding="utf-8")


def example(kind: str) -> list[str]:
    return re.findall(rf"\*\*{kind}:\*\*\n\n```text\n(.*?)```", EXAMPLES, re.S)


class TestCheckMessage(unittest.TestCase):

    def test_example_results_pass_and_drafts_do_not(self):
        regular, cya = example("Wersja do wysłania")
        self.assertEqual(cm.check(regular, "zwykly")[0], [])
        self.assertEqual(cm.check(cya, "dupokrytka")[0], [])
        draft_regular, draft_cya = example("Szkic")
        self.assertTrue(cm.check(draft_regular)[1])  # emocje jako ostrzeżenia
        self.assertTrue(cm.check(draft_cya, "dupokrytka")[0])

    def test_cya_draft_errors(self):
        errors, warnings = cm.check(DRAFT, "dupokrytka")
        joined = " | ".join(errors)
        self.assertIn("uwaga wewnętrzna", joined)
        self.assertIn("brak odpowiedzi oznacza akceptację", joined)
        self.assertIn("ponumerowanych punktów", joined)
        self.assertTrue(any("po raz kolejny" in w for w in warnings))
        self.assertTrue(any("wykrzykników" in w for w in warnings))

    def test_silence_clause_allowed_only_with_agreement(self):
        text = "1. Punkt 01.12.\n2. Punkt.\nBrak odpowiedzi do 05.12 oznacza akceptację. Proszę o potwierdzenie."
        self.assertTrue(cm.check(text, "dupokrytka")[0])
        self.assertEqual(cm.check(text, "dupokrytka", silence_agreed=True)[0], [])

    def test_dashes_secrets_and_template_leftovers_are_errors(self):
        for text, fragment in (("Termin — piątek.", "myślnik"), ("hasło: Tajne123", "hasło"),
                               ("Dzień dobry [Pani/Panie Imię],", "szablonu")):
            self.assertTrue(any(fragment in e for e in cm.check(text)[0]), text)

    def test_placeholders_are_errors_only_in_final_version(self):
        text = "Termin: [DO UZUPEŁNIENIA: data]."
        self.assertEqual(cm.check(text)[0], [])
        self.assertTrue(cm.check(text, final=True)[0])

    def test_risky_commitments_are_flagged(self):
        warnings = cm.check("Gwarantujemy termin i zrobimy to bezpłatnie, to nasza wina.")[1]
        self.assertEqual(sum("zobowiązanie" in w for w in warnings), 3)

    def test_chat_message_length(self):
        text = "Raz. Dwa. Trzy. Cztery. Pięć. Sześć. Siedem."
        self.assertTrue(any("zdań" in w for w in cm.check(text, channel="wiadomosc")[1]))

    def test_command_line_exit_codes(self):
        script = SKILL / "scripts" / "check_message.py"
        fixture = ROOT / "tests" / "fixtures" / "messages" / "draft_scope_change.txt"
        result = subprocess.run([sys.executable, str(script), str(fixture), "--mode", "dupokrytka"],
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(subprocess.run([sys.executable, str(script), "brak.txt"], capture_output=True,
                                        check=False).returncode, 2)


class TestIntegration(unittest.TestCase):

    def test_agents_can_run_the_check(self):
        script = "C:/x/flowkit-client-message-editor/scripts/check_message.py"
        for role in ("orchestrator", "analyst", "verifier"):
            self.assertIsNone(fx.check(role, ["python", script, "mail.txt"]), role)
        self.assertIsNotNone(fx.check("validator", ["python", script, "mail.txt"]))

    def test_skill_is_available_on_all_channels(self):
        name = "flowkit-client-message-editor"
        self.assertIn(name, (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8"))
        self.assertIn(f"**{name}**", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(name, (ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8"))
        self.assertIn(name, (ROOT / "agents" / "flowkit-orchestrator_agent.md").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / ".github" / "prompts" / f"{name}.prompt.md").exists())

    def test_skill_defines_both_modes_and_channels(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for term in ("`ZWYKŁY`", "`DUPOKRYTKA`", "`EMAIL`", "`WIADOMOŚĆ`", "[DO UZUPEŁNIENIA", "Milczenie to nie zgoda"):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
