"""Hook PostToolUse: zapisuje w dzienniku audytu użycie okna pytań, skilli i subagentów FlowKit.

Służy do diagnozy, kiedy pytanie trafiło do okna pytań (`AskUserQuestion`), a kiedy nie. Hook tylko
zapisuje: nie zmienia odpowiedzi modelu, nie blokuje narzędzia i zawsze kończy się kodem 0.

Zapisywane są wyłącznie zdarzenia FlowKit: narzędzia agentów `flowkit-*`, skille i subagenci `flowkit-*`
oraz okno pytań w sesji, w której wcześniej działał FlowKit. Treść pytań i odpowiedzi nie jest zapisywana,
tylko ich liczba. Dziennik: `~/.flowkit/audit.log` (`FLOWKIT_AUDIT_FILE`, wyłączenie: `off`).
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flowkit_exec import audit_file, write_audit  # noqa: E402

FLOWKIT = re.compile(r"(^|[:/])flowkit-")
QUESTION_TOOL = "AskUserQuestion"
TAIL_BYTES = 512 * 1024


def is_flowkit(value: object) -> bool:
    return bool(value) and bool(FLOWKIT.search(str(value)))


def log_tail() -> str:
    path = audit_file()
    if path is None or not path.exists():
        return ""
    with path.open("rb") as handle:
        size = handle.seek(0, 2)
        handle.seek(max(0, size - TAIL_BYTES))
        return handle.read().decode("utf-8", "replace")


def build_entry(data: dict) -> dict | None:
    """Zwraca wpis dziennika albo None, gdy zdarzenie nie dotyczy FlowKit lub było już zapisane."""
    tool = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") or {}
    agent = str(data.get("agent_type") or "").rsplit(":", 1)[-1] or "main"
    session = str(data.get("session_id") or "")
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "event": "tool",
        "session_id": session,
        "agent": agent,
        "tool": tool,
    }
    if tool == "Skill":
        entry["skill"] = str(tool_input.get("skill") or tool_input.get("command") or "")
    elif tool in ("Agent", "Task"):
        entry["subagent"] = str(tool_input.get("subagent_type") or "")
    elif tool == QUESTION_TOOL:
        questions = tool_input.get("questions") or []
        entry["questions"] = len(questions)
        entry["options"] = [len(q.get("options") or []) for q in questions if isinstance(q, dict)]
    tool_use_id = str(data.get("tool_use_id") or "")
    if tool_use_id:
        entry["tool_use_id"] = tool_use_id

    tail = None
    relevant = is_flowkit(agent) or is_flowkit(entry.get("skill")) or is_flowkit(entry.get("subagent"))
    if not relevant and tool == QUESTION_TOOL and session:
        tail = log_tail()
        relevant = f'"session_id": {json.dumps(session)}' in tail
    if not relevant:
        return None
    if tool_use_id:
        # Ten sam hook może być zarejestrowany w pluginie i w agencie: zapisz zdarzenie tylko raz.
        tail = log_tail() if tail is None else tail
        if f'"tool_use_id": {json.dumps(tool_use_id)}' in tail:
            return None
    return entry


def main() -> int:
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        entry = build_entry(data) if isinstance(data, dict) else None
        if entry is not None:
            write_audit(entry)
    except Exception as error:  # hook diagnostyczny nigdy nie przerywa pracy
        print(f"FlowKit: nie zapisano zdarzenia narzędzia: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
