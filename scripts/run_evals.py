"""Uruchamia scenariusze oceny przez lokalny Claude Code i zapisuje wynik w tests/evals/results/.

Użycie:
  python scripts/run_evals.py triggers [--skill NAZWA] [--model sonnet] [--dry-run]
  python scripts/run_evals.py cases [--case ID] [--model sonnet] [--baseline] [--dry-run]
  Limity czasu: --timeout SEKUNDY (jeden scenariusz, domyślnie 600), --total-timeout SEKUNDY (cała sesja, 3600)

Tryb --baseline uruchamia scenariusz bez wtyczki FlowKit, aby porównać jakość i zużycie tokenów.
Skrypt używa modelu skonfigurowanego w Claude Code i nie korzysta z serwerów MCP.

Statusy scenariusza: PASS, FAIL (błąd jakości odpowiedzi), TIMEOUT i ERROR (błąd infrastruktury),
SKIPPED (przekroczony limit sesji). Wyniki są zapisywane po każdym scenariuszu, więc przerwanie
sesji nie usuwa wyników już zakończonych scenariuszy.
Kody wyjścia: 0 = wszystkie PASS, 1 = FAIL, 2 = TIMEOUT/ERROR/SKIPPED, 3 = brak Claude Code.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_eval import grade, load_cases  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "tests" / "evals"
RESULTS = EVALS / "results"
EMPTY_MCP = '{"mcpServers":{}}'
DEFAULT_TIMEOUT = 600
DEFAULT_TOTAL_TIMEOUT = 3600
INFRASTRUCTURE = ("TIMEOUT", "ERROR", "SKIPPED")


def parse_events(lines: list[str]) -> dict:
    """Wyciąga z wyjścia stream-json użyte skille, odpowiedź i zużycie tokenów."""
    skills, answer, usage, finished, api_error = [], "", {"input_tokens": 0, "output_tokens": 0}, False, False
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                skills.append(str((block.get("input") or {}).get("skill", "")).rsplit(":", 1)[-1])
        if event.get("type") == "result":
            finished = True
            answer = str(event.get("result") or "")
            api_error = bool(event.get("is_error"))
            for key in usage:
                usage[key] = int((event.get("usage") or {}).get(key) or 0)
    return {"skills": skills, "answer": answer, "usage": usage, "finished": finished, "api_error": api_error}


def command(prompt: str, model: str, baseline: bool = False) -> list[str]:
    argv = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", model,
            "--strict-mcp-config", "--mcp-config", EMPTY_MCP, "--permission-mode", "plan"]
    return argv if baseline else [*argv, "--plugin-dir", str(ROOT)]


def kill_tree(process: subprocess.Popen) -> None:
    """Kończy proces razem z procesami potomnymi, aby zawieszony scenariusz nie blokował sesji."""
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], capture_output=True, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            process.kill()


def run_process(argv: list[str], cwd: str, timeout: float) -> tuple[str, str, str]:
    """Zwraca (status, stdout, opis błędu); status: OK, TIMEOUT albo ERROR."""
    options = {"start_new_session": True} if os.name != "nt" else {}
    try:
        process = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", **options)
    except OSError as error:
        return "ERROR", "", f"nie uruchomiono procesu: {error}"
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_tree(process)
        stdout, _ = process.communicate()
        return "TIMEOUT", stdout or "", f"przekroczono {timeout:.0f} s"
    if process.returncode != 0:
        return "ERROR", stdout, f"kod wyjścia {process.returncode}: {(stderr or '').strip()[-300:]}"
    return "OK", stdout, ""


def execute(prompt: str, model: str, baseline: bool, dry_run: bool, timeout: float = DEFAULT_TIMEOUT) -> dict:
    argv = command(prompt, model, baseline)
    if dry_run:
        print(" ".join(argv[:2]), repr(prompt[:70]))
        return {**parse_events([]), "status": "OK", "error": ""}
    with tempfile.TemporaryDirectory() as workspace:
        status, stdout, error = run_process(argv, workspace, timeout)
    outcome = parse_events(stdout.splitlines())
    if outcome["api_error"]:
        # Błąd API (np. brak środków, limit) to problem infrastruktury, nie jakości odpowiedzi.
        status, error = "ERROR", f"błąd API Claude Code: {outcome['answer'][:200]}"
    elif status == "OK" and not outcome["finished"]:
        status, error = "ERROR", "brak zdarzenia result w wyjściu Claude Code"
    return {**outcome, "status": status, "error": error}


def trigger_items(args) -> list[dict]:
    data = yaml.safe_load((EVALS / "triggers.yaml").read_text(encoding="utf-8"))["skills"]
    items = []
    for skill, groups in data.items():
        if args.skill and skill != args.skill:
            continue
        for expected, prompts in ((True, groups["should_trigger"]), (False, groups["should_not_trigger"])):
            items += [{"skill": skill, "prompt": prompt, "expected": expected} for prompt in prompts]
    return items


def case_items(args) -> list[dict]:
    items = []
    for case in load_cases().values():
        if args.case and case["id"] != args.case:
            continue
        source = (ROOT / "tests" / "fixtures" / case["fixture"]).read_text(encoding="utf-8")
        items.append({"case": case["id"], "baseline": args.baseline, "definition": case,
                      "prompt": f"{case['prompt']}\n\n<source_materials>\n{source}\n</source_materials>"})
    return items


def evaluate(item: dict, outcome: dict) -> dict:
    """Ocena jakości tylko dla scenariuszy, które się zakończyły; błąd infrastruktury nie jest FAIL."""
    row = {k: v for k, v in item.items() if k not in ("definition", "prompt")}
    if "skill" in item:
        row["prompt"] = item["prompt"]
    row["usage"] = outcome["usage"]
    if outcome["status"] != "OK":
        return {**row, "status": outcome["status"], "error": outcome["error"]}
    if "skill" in item:
        row["triggered"] = item["skill"] in outcome["skills"]
        return {**row, "status": "PASS" if row["triggered"] == item["expected"] else "FAIL"}
    row["problems"] = grade(item["definition"], outcome["answer"])
    return {**row, "status": "FAIL" if row["problems"] else "PASS"}


def run_all(items: list[dict], args, target: Path | None) -> list[dict]:
    rows: list[dict] = []
    deadline = time.monotonic() + args.total_timeout
    for item in items:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            rows.append({**evaluate(item, {"status": "SKIPPED", "error": "przekroczono limit sesji",
                                           "usage": {"input_tokens": 0, "output_tokens": 0}})})
        else:
            outcome = execute(item["prompt"], args.model, item.get("baseline", False), args.dry_run,
                              min(args.timeout, remaining))
            rows.append(evaluate(item, outcome))
        if target is not None:  # zapis po każdym scenariuszu: wyniki cząstkowe przetrwają przerwanie
            target.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def summary(rows: list[dict]) -> tuple[str, int]:
    counts = {status: sum(r["status"] == status for r in rows) for status in ("PASS", "FAIL", *INFRASTRUCTURE)}
    tokens = sum(r["usage"]["input_tokens"] + r["usage"]["output_tokens"] for r in rows)
    text = (f"PASS {counts['PASS']} · FAIL {counts['FAIL']} (jakość) · TIMEOUT {counts['TIMEOUT']} · "
            f"ERROR {counts['ERROR']} · SKIPPED {counts['SKIPPED']} (infrastruktura) z {len(rows)}. Tokeny: {tokens}.")
    if counts["FAIL"]:
        return text, 1
    return text, 2 if any(counts[s] for s in INFRASTRUCTURE) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("suite", choices=("triggers", "cases"))
    parser.add_argument("--skill")
    parser.add_argument("--case")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--total-timeout", type=float, default=DEFAULT_TOTAL_TIMEOUT)
    args = parser.parse_args()
    if args.timeout <= 0 or args.total_timeout <= 0:
        parser.error("limity czasu muszą być dodatnie")
    if not args.dry_run and shutil.which("claude") is None:
        print("BRAK NARZĘDZIA: claude")
        return 3
    items = trigger_items(args) if args.suite == "triggers" else case_items(args)
    target = None
    if not args.dry_run:
        RESULTS.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = RESULTS / f"{args.suite}-{stamp}.json"
    rows = run_all(items, args, target)
    if args.dry_run:
        print(f"Scenariuszy: {len(rows)}")
        return 0
    text, code = summary(rows)
    for row in rows:
        if row["status"] in INFRASTRUCTURE:
            print(f"{row['status']}: {row.get('case') or row.get('skill')} — {row.get('error')}")
    print(f"{text} Wynik: {target}")
    return code


if __name__ == "__main__":
    sys.exit(main())
