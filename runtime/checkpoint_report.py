"""Raport diagnostyczny okna pytań FlowKit. Tylko czyta pliki, niczego nie zmienia.

Źródła:
- dziennik audytu (`~/.flowkit/audit.log`, zdarzenia `"event": "tool"` z hooka `log_tool_event.py`):
  ile razy agenci i skille FlowKit użyli okna pytań, skilli i subagentów;
- zapisy rozmów Claude Code (`~/.claude/projects/<projekt>/*.jsonl`, opcja `--transcripts`): które
  punkty kontrolne (`Next:` lub `Ask:`) zakończyły się oknem pytań, a które zwykłym tekstem i dlaczego.

Użycie:
  python checkpoint_report.py
  python checkpoint_report.py --transcripts ~/.claude/projects/<projekt> --since 2026-11-01
  python checkpoint_report.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flowkit_exec import audit_file  # noqa: E402

QUESTION_TOOL = "AskUserQuestion"
NEXT_LINE = re.compile(r"^\s*Next:\s*1\.", re.MULTILINE)
ASK_LINE = re.compile(r"^\s*Ask:\s*(window|text|auto)\b\s*(?:[—–-]\s*(.*))?$", re.MULTILINE | re.IGNORECASE)
AUTO_LINE = re.compile(r"^\s*AUTO\s*→", re.MULTILINE)


# --- Dziennik audytu ------------------------------------------------------------------

def read_audit(path: Path | None, since: str | None) -> list[dict]:
    if path is None or not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict) and entry.get("event") == "tool" and (not since or entry.get("ts", "") >= since):
            events.append(entry)
    return events


def summarize_audit(events: list[dict]) -> dict:
    sessions: dict[str, dict] = {}
    for entry in events:
        info = sessions.setdefault(entry.get("session_id") or "?", {"skills": set(), "subagents": set(), "questions": 0})
        if entry.get("skill"):
            info["skills"].add(entry["skill"])
        if entry.get("subagent"):
            info["subagents"].add(entry["subagent"])
        if entry.get("tool") == QUESTION_TOOL:
            info["questions"] += 1
    silent = sorted(sid for sid, info in sessions.items() if info["questions"] == 0)
    return {
        "events": len(events),
        "by_tool": dict(Counter(e.get("tool") for e in events)),
        "by_agent": dict(Counter(e.get("agent") for e in events)),
        "skills": dict(Counter(e["skill"] for e in events if e.get("skill"))),
        "question_calls_by_agent": dict(Counter(e.get("agent") for e in events if e.get("tool") == QUESTION_TOOL)),
        "sessions": len(sessions),
        "sessions_without_question_window": silent,
    }


# --- Zapisy rozmów Claude Code --------------------------------------------------------

def transcript_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        path = path.expanduser()
        files.extend(sorted(path.rglob("*.jsonl")) if path.is_dir() else [path] if path.exists() else [])
    return files


def blocks(entry: dict) -> list[dict]:
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content or [] if isinstance(b, dict)]


def is_user_turn(entry: dict) -> bool:
    """Nowa wiadomość użytkownika (nie wynik narzędzia) zamyka poprzednią turę."""
    if entry.get("type") != "user":
        return False
    parts = blocks(entry)
    return bool(parts) and not all(b.get("type") == "tool_result" for b in parts)


def classify(turn: dict) -> dict | None:
    text = "\n".join(turn["texts"])
    asks = ASK_LINE.findall(text)
    if not (NEXT_LINE.search(text) or asks or turn["questions"]):
        return None
    declared, reason = (asks[-1][0].lower(), asks[-1][1].strip()) if asks else (None, "")
    if turn["questions"]:
        status = "window"
    elif declared == "auto" or AUTO_LINE.search(text):
        status = "auto"
    elif declared == "window":
        status = "mismatch"  # deklaracja okna bez wywołania narzędzia
    elif declared == "text":
        status = "text"
    else:
        status = "text-undeclared"
    return {"file": turn["file"], "ts": turn["ts"], "status": status, "declared": declared,
            "reason": reason[:160], "skills": sorted(turn["skills"]), "subagents": sorted(turn["subagents"])}


def read_transcript(path: Path, since: str | None) -> list[dict]:
    checkpoints: list[dict] = []
    turn = None

    def close() -> None:
        if turn is not None and (not since or turn["ts"] >= since):
            result = classify(turn)
            if result:
                checkpoints.append(result)

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("isSidechain"):
            continue
        if is_user_turn(entry):
            close()
            turn = {"file": path.name, "ts": str(entry.get("timestamp") or ""), "texts": [], "questions": 0,
                    "skills": set(), "subagents": set()}
            continue
        if turn is None or entry.get("type") != "assistant":
            continue
        for block in blocks(entry):
            if block.get("type") == "text":
                turn["texts"].append(str(block.get("text") or ""))
            elif block.get("type") == "tool_use":
                name, tool_input = block.get("name"), block.get("input") or {}
                if name == QUESTION_TOOL:
                    turn["questions"] += 1
                elif name == "Skill":
                    turn["skills"].add(str(tool_input.get("skill") or ""))
                elif name in ("Agent", "Task"):
                    turn["subagents"].add(str(tool_input.get("subagent_type") or ""))
    close()
    return checkpoints


def summarize_transcripts(checkpoints: list[dict]) -> dict:
    return {
        "checkpoints": len(checkpoints),
        "by_status": dict(Counter(c["status"] for c in checkpoints)),
        "text_reasons": dict(Counter(c["reason"] or "(brak powodu)" for c in checkpoints if c["status"] == "text")),
        "not_window": [c for c in checkpoints if c["status"] in ("text", "text-undeclared", "mismatch")],
    }


# --- Wynik ----------------------------------------------------------------------------

STATUS_LABELS = {
    "window": "okno pytań",
    "auto": "AUTO (bez pytania, zamierzone)",
    "text": "tekst, z podanym powodem",
    "text-undeclared": "tekst, bez wiersza Ask:",
    "mismatch": "Ask: window, ale bez wywołania okna",
}


def print_report(audit: dict, transcripts: dict | None, audit_path: Path | None) -> None:
    print(f"Dziennik audytu: {audit_path or 'wyłączony'}")
    if not audit["events"]:
        print("  Brak zdarzeń narzędzi FlowKit (hook log_tool_event.py nie działał albo nic nie uruchomiono).")
    else:
        print(f"  Zdarzenia: {audit['events']} w {audit['sessions']} sesjach")
        print(f"  Narzędzia: {audit['by_tool']}")
        print(f"  Agenci: {audit['by_agent']}")
        print(f"  Skille: {audit['skills'] or 'brak'}")
        print(f"  Okno pytań według agenta: {audit['question_calls_by_agent'] or 'brak wywołań'}")
        silent = audit["sessions_without_question_window"]
        print(f"  Sesje FlowKit bez okna pytań: {len(silent)}" + (f" ({', '.join(silent[:10])})" if silent else ""))
    if transcripts is None:
        print("\nZapisy rozmów: nie podano (--transcripts).")
        return
    print(f"\nPunkty kontrolne w zapisach rozmów: {transcripts['checkpoints']}")
    for status, count in sorted(transcripts["by_status"].items()):
        print(f"  {STATUS_LABELS.get(status, status)}: {count}")
    for reason, count in sorted(transcripts["text_reasons"].items(), key=lambda item: -item[1]):
        print(f"  powód tekstu: {reason} ({count})")
    if transcripts["not_window"]:
        print("\nPunkty kontrolne bez okna pytań:")
        for item in transcripts["not_window"][:50]:
            where = ", ".join(item["skills"] + item["subagents"]) or "bez skilla/subagenta"
            reason = f" — {item['reason']}" if item["reason"] else ""
            print(f"  {item['ts'][:19]} {item['file']}: {STATUS_LABELS[item['status']]} [{where}]{reason}")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", type=Path, help="ścieżka dziennika audytu (domyślnie jak FLOWKIT_AUDIT_FILE)")
    parser.add_argument("--transcripts", type=Path, nargs="*", help="pliki .jsonl lub katalogi zapisów Claude Code")
    parser.add_argument("--since", help="tylko zdarzenia od daty, np. 2026-11-01")
    parser.add_argument("--json", action="store_true", help="wynik w JSON")
    args = parser.parse_args(argv)

    audit_path = args.audit.expanduser() if args.audit else audit_file()
    audit = summarize_audit(read_audit(audit_path, args.since))
    transcripts = None
    if args.transcripts is not None:
        checkpoints = [c for f in transcript_files(args.transcripts) for c in read_transcript(f, args.since)]
        transcripts = summarize_transcripts(checkpoints)
    if args.json:
        print(json.dumps({"audit": audit, "transcripts": transcripts}, ensure_ascii=False, indent=2))
    else:
        print_report(audit, transcripts, audit_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
