"""Wykrywa angielskie nazwy statusów, priorytetów i wymagalności w tabelach dokumentu.

Użycie: python check_status_labels.py dokument.md|dokument.docx

Sprawdzane są tylko całe komórki tabel, więc nazwy własne i kod w opisach nie dają
fałszywych alarmów. Słownik odpowiada plikowi references/status-vocabulary.md.
Kody wyjścia: 0 = brak uwag, 1 = znaleziono angielskie nazwy, 3 = brak python-docx.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TERMS = {
    # Wymagalność (MoSCoW)
    "must": "Wymagane", "must have": "Wymagane", "mandatory": "Wymagane", "required": "Wymagane",
    "should": "Zalecane", "should have": "Zalecane", "recommended": "Zalecane",
    "could": "Opcjonalne", "could have": "Opcjonalne", "nice to have": "Opcjonalne", "optional": "Opcjonalne",
    "won't": "Wyłączone z zakresu", "won’t": "Wyłączone z zakresu", "wont": "Wyłączone z zakresu",
    "won't have": "Wyłączone z zakresu", "won’t have": "Wyłączone z zakresu", "out of scope": "Poza zakresem",
    # Priorytet, wpływ, ważność
    "blocker": "Blokujący", "critical": "Krytyczny", "high": "Wysoki", "medium": "Średni",
    "normal": "Normalny", "low": "Niski", "major": "Poważny", "minor": "Drobny",
    # Status
    "new": "Nowy", "draft": "Roboczy", "proposed": "Proponowany", "open": "Otwarty", "to do": "Do zrobienia",
    "todo": "Do zrobienia", "in progress": "W toku", "wip": "W toku", "in review": "W weryfikacji",
    "under review": "W weryfikacji", "pending": "Oczekujący", "on hold": "Wstrzymany", "blocked": "Zablokowany",
    "approved": "Zaakceptowany", "accepted": "Zaakceptowany", "rejected": "Odrzucony", "resolved": "Rozstrzygnięty",
    "done": "Zakończony", "completed": "Zakończony", "closed": "Zamknięty", "cancelled": "Anulowany",
    "canceled": "Anulowany", "deferred": "Odłożony",
    # Wynik testu i wartości ogólne
    "pass": "Zaliczony", "passed": "Zaliczony", "fail": "Niezaliczony", "failed": "Niezaliczony",
    "skipped": "Pominięty", "yes": "Tak", "no": "Nie", "n/a": "Nie dotyczy", "tbd": "DO POTWIERDZENIA",
    # Nagłówki kolumn
    "priority": "Priorytet", "severity": "Ważność", "impact": "Wpływ", "owner": "Właściciel",
    "probability": "Prawdopodobieństwo", "requirement level": "Wymagalność",
}


def lookup(cell: str) -> str | None:
    value = re.sub(r"[*_`]", "", cell).strip().casefold()
    return TERMS.get(re.sub(r"\s+", " ", value))


def markdown_cells(path: Path):
    fenced = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        stripped = line.strip()
        if fenced or not stripped.startswith("|") or re.fullmatch(r"[|:\-\s]+", stripped):
            continue
        for cell in re.split(r"(?<!\\)\|", stripped.strip("|")):
            yield f"wiersz {number}", cell


def docx_cells(path: Path):
    from docx_support import open_document
    for t, table in enumerate(open_document(path).tables, 1):
        for r, row in enumerate(table.rows, 1):
            for cell in row.cells:
                yield f"tabela {t}, wiersz {r}", cell.text


def find_issues(path: Path) -> list[str]:
    cells = docx_cells(path) if path.suffix.lower() in (".docx", ".dotx") else markdown_cells(path)
    issues = []
    for where, cell in cells:
        polish = lookup(cell)
        if polish:
            issues.append(f"{where}: '{cell.strip()}' → '{polish}'")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    try:
        issues = find_issues(args.document)
    except ImportError:
        print("BRAK python-docx: nie można sprawdzić pliku .docx.")
        return 3
    for issue in issues:
        print(issue)
    print(f"Znaleziono angielskich nazw: {len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
