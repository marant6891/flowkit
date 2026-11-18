"""Ocenia zapisaną odpowiedź modelu względem scenariusza z tests/evals/cases.yaml.

Użycie: python scripts/grade_eval.py <id-scenariusza> <plik-z-odpowiedzią>
Kody wyjścia: 0 = zaliczono, 1 = niezaliczono, 2 = nieznany scenariusz.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "evals" / "cases.yaml"


def load_cases() -> dict[str, dict]:
    data = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    return {case["id"]: case for case in data["cases"]}


def grade(case: dict, answer: str) -> list[str]:
    problems = [f"brak wymaganego wzorca: {p}" for p in case["must_contain"] if not re.search(p, answer)]
    problems += [f"niedozwolona treść: {p}" for p in case["must_not_contain"] if re.search(p, answer)]
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("case")
    parser.add_argument("answer", type=Path)
    args = parser.parse_args()
    cases = load_cases()
    if args.case not in cases:
        print(f"Nieznany scenariusz. Dostępne: {', '.join(cases)}")
        return 2
    problems = grade(cases[args.case], args.answer.read_text(encoding="utf-8"))
    for problem in problems:
        print(f"NIEZALICZONO: {problem}")
    if not problems:
        print("ZALICZONO")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
