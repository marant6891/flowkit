"""Testy okna pytań: wspólna reguła agentów i skilli, hook logujący i raport punktów kontrolnych.
Uruchom: python -m unittest tests/test_question_window.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(ROOT / "scripts"))

import build_agents  # noqa: E402
import checkpoint_report as report  # noqa: E402
import flowkit_exec as fx  # noqa: E402
import log_tool_event as hook  # noqa: E402

HOOK = str(RUNTIME / "log_tool_event.py")


class TestToolEventHook(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.log = Path(tmp.name) / "audit.log"
        self.env = {**os.environ, fx.AUDIT_FILE_ENV: str(self.log)}
        previous = os.environ.get(fx.AUDIT_FILE_ENV)
        os.environ[fx.AUDIT_FILE_ENV] = str(self.log)
        self.addCleanup(lambda: os.environ.__setitem__(fx.AUDIT_FILE_ENV, previous) if previous is not None
                        else os.environ.pop(fx.AUDIT_FILE_ENV, None))

    def run_hook(self, payload, raw=None):
        data = raw if raw is not None else json.dumps(payload).encode("utf-8")
        return subprocess.run([sys.executable, HOOK], input=data, capture_output=True, env=self.env, check=False)

    def entries(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_flowkit_skill_and_later_question_window_are_logged(self):
        self.assertEqual(self.run_hook({"session_id": "s1", "tool_name": "Skill", "tool_use_id": "t1",
                                        "tool_input": {"skill": "flowkit-sql-data-assistant"}}).returncode, 0)
        questions = [{"question": "Jaka baza?", "options": [{"label": "PostgreSQL"}, {"label": "Oracle"}]}]
        self.run_hook({"session_id": "s1", "tool_name": "AskUserQuestion", "tool_use_id": "t2",
                       "tool_input": {"questions": questions}})
        skill, ask = self.entries()
        self.assertEqual((skill["event"], skill["agent"], skill["skill"]), ("tool", "main", "flowkit-sql-data-assistant"))
        self.assertEqual((ask["tool"], ask["questions"], ask["options"]), ("AskUserQuestion", 1, [2]))
        self.assertNotIn("Jaka baza?", self.log.read_text(encoding="utf-8"))

    def test_unrelated_sessions_are_not_logged(self):
        self.run_hook({"session_id": "x", "tool_name": "Skill", "tool_input": {"skill": "pdf"}})
        self.run_hook({"session_id": "x", "tool_name": "AskUserQuestion", "tool_input": {"questions": []}})
        self.assertEqual(self.entries(), [])

    def test_flowkit_agents_and_subagents_are_logged_once(self):
        payload = {"session_id": "s2", "agent_type": "flowkit:flowkit-orchestrator", "tool_name": "Agent",
                   "tool_use_id": "t3", "tool_input": {"subagent_type": "flowkit-analyst"}}
        self.run_hook(payload)
        self.run_hook(payload)  # ten sam hook z pluginu i z agenta
        (entry,) = self.entries()
        self.assertEqual((entry["agent"], entry["subagent"]), ("flowkit-orchestrator", "flowkit-analyst"))

    def test_hook_never_fails(self):
        self.assertEqual(self.run_hook(None, raw=b"\xff not json").returncode, 0)
        env = {**self.env, fx.AUDIT_FILE_ENV: "off"}
        result = subprocess.run([sys.executable, HOOK], input=b'{"tool_name": "Skill", "tool_input": {"skill": "flowkit-x"}}',
                                capture_output=True, env=env, check=False)
        self.assertEqual(result.returncode, 0)

    def test_hook_is_registered_for_plugin_and_agents(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PostToolUse"][0]
        self.assertEqual(hooks["matcher"], "AskUserQuestion|Skill|Agent|Task")
        self.assertIn("log_tool_event.py", hooks["hooks"][0]["command"])
        for path in (ROOT / "agents" / "adapters" / "claude-code").glob("*.md"):
            data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            if {"Skill", "Agent", "AskUserQuestion"} & set(data["tools"]):
                self.assertIn("log_tool_event.py", json.dumps(data["hooks"]), path.name)


def transcript(lines):
    return "\n".join(json.dumps(line, ensure_ascii=False) for line in lines) + "\n"


def user(text, ts):
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": text}}


def assistant(*content):
    return {"type": "assistant", "message": {"role": "assistant", "content": list(content)}}


def text(value):
    return {"type": "text", "text": value}


def tool(name, **tool_input):
    return {"type": "tool_use", "name": name, "input": tool_input}


class TestCheckpointReport(unittest.TestCase):

    def test_checkpoints_are_classified(self):
        lines = [
            user("SQL: raport", "2026-11-25T10:00:00Z"),
            assistant(tool("Skill", skill="flowkit-sql-data-assistant"), text("Next: 1. A 2. B\nAsk: window"),
                      tool("AskUserQuestion", questions=[])),
            user("A", "2026-11-25T10:01:00Z"),
            assistant(text("Next: 1. A\nAsk: text — narzędzie niedostępne")),
            user("dalej", "2026-11-25T10:02:00Z"),
            assistant(text("AUTO → 1. A\nNext: 1. A\nAsk: auto")),
            user("dalej", "2026-11-25T10:03:00Z"),
            assistant(text("Next: 1. A 2. B")),
            user("dalej", "2026-11-25T10:04:00Z"),
            assistant(text("Next: 1. A\nAsk: window")),
            user("dalej", "2026-11-25T10:05:00Z"),
            assistant(text("Zwykła odpowiedź bez punktu kontrolnego.")),
            {"type": "assistant", "isSidechain": True, "message": {"content": [text("Next: 1. subagent")]}},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.jsonl"
            path.write_text(transcript(lines), encoding="utf-8")
            checkpoints = report.read_transcript(path, None)
            self.assertEqual([c["status"] for c in checkpoints],
                             ["window", "text", "auto", "text-undeclared", "mismatch"])
            self.assertEqual(checkpoints[0]["skills"], ["flowkit-sql-data-assistant"])
            self.assertEqual(checkpoints[1]["reason"], "narzędzie niedostępne")
            self.assertEqual(len(report.read_transcript(path, "2026-11-25T10:03")), 2)
            summary = report.summarize_transcripts(checkpoints)
            self.assertEqual(len(summary["not_window"]), 3)

    def test_audit_summary_finds_sessions_without_question_window(self):
        events = [{"event": "tool", "session_id": "a", "agent": "main", "tool": "Skill", "skill": "flowkit-x"},
                  {"event": "tool", "session_id": "a", "agent": "main", "tool": "AskUserQuestion"},
                  {"event": "tool", "session_id": "b", "agent": "flowkit-orchestrator", "tool": "Agent",
                   "subagent": "flowkit-analyst"}]
        summary = report.summarize_audit(events)
        self.assertEqual(summary["sessions_without_question_window"], ["b"])
        self.assertEqual(summary["question_calls_by_agent"], {"main": 1})

    def test_report_runs_from_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "audit.log"
            log.write_text(json.dumps({"event": "tool", "session_id": "a", "tool": "Skill", "agent": "main",
                                       "skill": "flowkit-x"}) + "\n{zły wiersz\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(RUNTIME / "checkpoint_report.py"), "--audit", str(log),
                                     "--transcripts", tmp, "--json"], capture_output=True, text=True,
                                    encoding="utf-8", check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["audit"]["events"], 1)
            self.assertEqual(data["transcripts"]["checkpoints"], 0)


class TestQuestionRule(unittest.TestCase):

    def test_orchestrator_has_question_tool_and_rule_on_both_platforms(self):
        self.assertIn("AskUserQuestion", build_agents.CLAUDE_TOOLS["flowkit-orchestrator"])
        for platform in ("claude", "vscode"):
            text = build_agents.target("flowkit-orchestrator", platform).read_text(encoding="utf-8")
            self.assertIn("## Question window (mandatory)", text)
            self.assertIn("Ask: window", text)

    def test_subagents_return_questions_instead_of_asking(self):
        for name in build_agents.AGENTS:
            if name == build_agents.ORCHESTRATOR:
                continue
            self.assertNotIn("AskUserQuestion", build_agents.CLAUDE_TOOLS[name], name)
            for platform in ("claude", "vscode"):
                self.assertIn("QUESTION-NNN", build_agents.target(name, platform).read_text(encoding="utf-8"), name)

    def test_every_skill_and_prompt_uses_question_window(self):
        for skill in (ROOT / "skills").glob("flowkit-*/SKILL.md"):
            body = skill.read_text(encoding="utf-8")
            self.assertRegex(body, r"(?m)^# Pytania do użytkownika$", skill.parent.name)
            for term in ("vscode/askQuestions", "AskUserQuestion", "Ask: window", "QUESTION-NNN"):
                self.assertIn(term, body, skill.parent.name)
        for prompt in (ROOT / ".github" / "prompts").glob("flowkit-*.prompt.md"):
            front = yaml.safe_load(prompt.read_text(encoding="utf-8").split("---", 2)[1])
            self.assertEqual(front["agent"], "agent", prompt.name)
            self.assertIn("vscode/askQuestions", front["tools"], prompt.name)

    def test_hook_entry_has_no_question_text(self):
        entry = hook.build_entry({"session_id": "z", "agent_type": "flowkit-orchestrator", "tool_name": "AskUserQuestion",
                                  "tool_input": {"questions": [{"question": "Tajne?", "options": [{}, {}, {}]}]}})
        self.assertEqual(entry["options"], [3])
        self.assertFalse(re.search("Tajne", json.dumps(entry)))


if __name__ == "__main__":
    unittest.main()
