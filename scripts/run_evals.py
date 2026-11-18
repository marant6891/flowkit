"""Uruchamia scenariusze oceny przez lokalny Claude Code i zapisuje wynik w tests/evals/results/.

Użycie:
  python scripts/run_evals.py triggers [--skill NAZWA] [--model sonnet] [--dry-run]
  python scripts/run_evals.py cases [--case ID] [--model sonnet] [--baseline] [--dry-run]

Tryb --baseline uruchamia scenariusz bez wtyczki FlowKit, aby porównać jakość i zużycie tokenów.
Skrypt używa modelu skonfigurowanego w Claude Code i nie korzysta z serwerów MCP.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_eval import grade, load_cases  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "tests" / "evals"
RESULTS = EVALS / "results"
EMPTY_MCP = '{"mcpServers":{}}'


def parse_events(lines: list[str]) -> dict:
    """Wyciąga z wyjścia stream-json użyte skille, odpowiedź i zużycie tokenów."""
    skills, answer, usage = [], "", {"input_tokens": 0, "output_tokens": 0}
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                skills.append(str((block.get("input") or {}).get("skill", "")).rsplit(":", 1)[-1])
        if event.get("type") == "result":
            answer = str(event.get("result") or "")
            for key in usage:
                usage[key] = int((event.get("usage") or {}).get(key) or 0)
    return {"skills": skills, "answer": answer, "usage": usage}


def command(prompt: str, model: str, baseline: bool = False) -> list[str]:
    argv = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", model,
            "--strict-mcp-config", "--mcp-config", EMPTY_MCP, "--permission-mode", "plan"]
    return argv if baseline else [*argv, "--plugin-dir", str(ROOT)]


def execute(prompt: str, model: str, baseline: bool, dry_run: bool) -> dict:
    argv = command(prompt, model, baseline)
    if dry_run:
        print(" ".join(argv[:2]), repr(prompt[:70]))
        return parse_events([])
    with tempfile.TemporaryDirectory() as workspace:
        result = subprocess.run(argv, cwd=workspace, capture_output=True, text=True, encoding="utf-8", check=False)
    return parse_events(result.stdout.splitlines())


def run_triggers(args) -> list[dict]:
    data = yaml.safe_load((EVALS / "triggers.yaml").read_text(encoding="utf-8"))["skills"]
    rows = []
    for skill, groups in data.items():
        if args.skill and skill != args.skill:
            continue
        for expected, prompts in ((True, groups["should_trigger"]), (False, groups["should_not_trigger"])):
            for prompt in prompts:
                outcome = execute(prompt, args.model, False, args.dry_run)
                rows.append({"skill": skill, "prompt": prompt, "expected": expected,
                             "triggered": skill in outcome["skills"], "usage": outcome["usage"]})
    return rows


def run_cases(args) -> list[dict]:
    rows = []
    for case in load_cases().values():
        if args.case and case["id"] != args.case:
            continue
        source = (ROOT / "tests" / "fixtures" / case["fixture"]).read_text(encoding="utf-8")
        prompt = f"{case['prompt']}\n\n<source_materials>\n{source}\n</source_materials>"
        outcome = execute(prompt, args.model, args.baseline, args.dry_run)
        rows.append({"case": case["id"], "baseline": args.baseline, "problems": grade(case, outcome["answer"]),
                     "usage": outcome["usage"]})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("suite", choices=("triggers", "cases"))
    parser.add_argument("--skill")
    parser.add_argument("--case")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and shutil.which("claude") is None:
        print("BRAK NARZĘDZIA: claude")
        return 3
    rows = run_triggers(args) if args.suite == "triggers" else run_cases(args)
    if args.dry_run:
        print(f"Scenariuszy: {len(rows)}")
        return 0
    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = RESULTS / f"{args.suite}-{stamp}.json"
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [r for r in rows if r.get("problems") or r.get("expected", r.get("triggered")) != r.get("triggered")]
    tokens = sum(r["usage"]["input_tokens"] + r["usage"]["output_tokens"] for r in rows)
    print(f"Zaliczono {len(rows) - len(failed)} z {len(rows)}. Tokeny: {tokens}. Wynik: {target}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
