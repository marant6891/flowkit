"""Sprawdza, czy dokument dla klienta nie zawiera dopisków roboczych.

Użycie:
  python check_client_version.py dokument.docx|dokument.md [--mode client|final] [--questions-heading TEKST]

Tryb `client` (wersja dla klienta): w treści dokumentu nie ma oznaczeń źródeł (SRC-NNN, plik:linia,
kolumna „Źródło”), identyfikatorów roboczych (ASSUMPTION, OPEN, Q, REC), sformułowań „DO POTWIERDZENIA”,
„Brak danych”, „Nie analizowano”, interpretacji ani placeholderów. Wątpliwości są wyłącznie w sekcji
końcowej („Kwestie do wyjaśnienia”) jako K-01, K-02…; każde odwołanie (K-NN) w treści ma tam swój punkt.
Tryb `final` (dokument końcowy bez dopisków): te same zakazy w całym dokumencie, bez odwołań K-NN.

Kody wyjścia: 0 = dokument czysty, 1 = znaleziono dopiski, 3 = brak python-docx dla pliku .docx.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

QUESTION_HEADINGS = ("kwestie do wyjaśnienia", "tematy do wyjaśnienia", "otwarte kwestie", "pytania otwarte",
                     "kwestie otwarte")
WORKING_MARKERS = (
    (re.compile(r"\bSRC-\d+"), "oznaczenie źródła"),
    (re.compile(r"\bASSUMPTION-\d+"), "identyfikator założenia"),
    (re.compile(r"\bOPEN-\d+"), "identyfikator tematu otwartego"),
    (re.compile(r"\bQ-\d{3}\b"), "identyfikator pytania"),
    (re.compile(r"\bREC-\d+"), "identyfikator rekomendacji"),
    (re.compile(r"DO POTWIERDZENIA", re.I), "„DO POTWIERDZENIA”"),
    (re.compile(r"\bNie analizowano\b", re.I), "„Nie analizowano”"),
    (re.compile(r"\bBrak danych\b", re.I), "„Brak danych”"),
    (re.compile(r"\(interpretacja|\bInterpretacja:", re.I), "oznaczenie interpretacji"),
    (re.compile(r"\bTBD\b"), "„TBD”"),
    (re.compile(r"[\w./\\-]+\.(?:cs|py|java|kt|ts|tsx|js|sql|xml|json|ya?ml|config|properties|go|rb|php):\d+"),
     "odwołanie plik:linia"),
    (re.compile(r"\[(?:WPISZ[^\]]*|[A-ZĄĆĘŁŃÓŚŹŻ][A-ZĄĆĘŁŃÓŚŹŻ /_-]{2,}|\.\.\.)\](?!\()"), "placeholder szablonu"),
    (re.compile(r"<!--"), "komentarz"),
)
SOURCE_HEADER = re.compile(r"^\s*źródł[oa]\s*$", re.I)
QUESTION_REF = re.compile(r"\bK-\d{2,3}\b")
QUESTION_ITEM = re.compile(r"^\W*(K-\d{2,3})\b")


class Block:
    def __init__(self, where: str, text: str, heading: int = 0, cells: list[str] | None = None) -> None:
        self.where, self.text, self.heading, self.cells = where, text, heading, cells or []


def markdown_blocks(path: Path) -> list[Block]:
    blocks, fenced = [], False
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.strip():
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)", line)
        stripped = line.strip()
        if stripped.startswith("|"):
            if re.fullmatch(r"[|:\-\s]+", stripped):
                continue
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", stripped.strip("|"))]
            blocks.append(Block(f"wiersz {number}", stripped, cells=cells))
        else:
            blocks.append(Block(f"wiersz {number}", heading.group(2) if heading else line,
                                len(heading.group(1)) if heading else 0))
    return blocks


def docx_blocks(path: Path) -> list[Block]:
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    from docx_support import open_document

    doc = open_document(path)
    blocks, paragraph_no, table_no = [], 0, 0
    for element in doc.element.body.iterchildren():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "p":
            paragraph_no += 1
            paragraph = Paragraph(element, doc)
            if not paragraph.text.strip():
                continue
            style = (paragraph.style.name if paragraph.style is not None else "") or ""
            level = re.search(r"(?:heading|nag\w*)\s*(\d)", style, re.I)
            blocks.append(Block(f"akapit {paragraph_no}", paragraph.text, int(level.group(1)) if level else 0))
        elif tag == "tbl":
            table_no += 1
            for row_no, row in enumerate(Table(element, doc).rows, 1):
                cells = [cell.text.strip() for cell in row.cells]
                blocks.append(Block(f"tabela {table_no}, wiersz {row_no}", " | ".join(cells), cells=cells))
    return blocks


def split_questions(blocks: list[Block], heading_text: str | None) -> tuple[list[Block], list[Block]]:
    """Zwraca (treść dokumentu, sekcja wątpliwości)."""
    wanted = [heading_text.casefold()] if heading_text else list(QUESTION_HEADINGS)
    start = next((i for i, b in enumerate(blocks) if b.heading and any(w in b.text.casefold() for w in wanted)), None)
    if start is None:
        return blocks, []
    level = blocks[start].heading
    end = next((i for i in range(start + 1, len(blocks)) if 0 < blocks[i].heading <= level), len(blocks))
    return blocks[:start] + blocks[end:], blocks[start:end]


def find_issues(path: Path, mode: str = "client", heading_text: str | None = None) -> list[str]:
    blocks = docx_blocks(path) if path.suffix.lower() in (".docx", ".dotx") else markdown_blocks(path)
    body, questions = split_questions(blocks, heading_text) if mode == "client" else (blocks, [])
    issues = []
    for block in body:
        for pattern, label in WORKING_MARKERS:
            match = pattern.search(block.text)
            if match:
                issues.append(f"{block.where}: {label} „{match.group(0)}” w treści dokumentu")
        if any(SOURCE_HEADER.match(cell) for cell in block.cells):
            issues.append(f"{block.where}: kolumna „Źródło” w treści dokumentu")
        ref = QUESTION_REF.search(block.text) if mode == "final" else None
        if ref:
            issues.append(f"{block.where}: odwołanie do kwestii otwartej {ref.group(0)} w dokumencie końcowym")
    if mode == "client":
        for block in questions:
            for pattern, label in WORKING_MARKERS[:5]:
                match = pattern.search(block.text)
                if match:
                    issues.append(f"{block.where}: {label} „{match.group(0)}” w sekcji wątpliwości (użyj K-NN)")
        defined = set()
        for block in questions:
            first = block.cells[0] if block.cells else block.text
            item = QUESTION_ITEM.match(first)
            if item:
                defined.add(item.group(1))
        for block in body:
            for ref in QUESTION_REF.findall(block.text):
                if ref not in defined:
                    issues.append(f"{block.where}: odwołanie {ref} bez punktu w sekcji wątpliwości")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--mode", choices=("client", "final"), default="client")
    parser.add_argument("--questions-heading", help="nagłówek sekcji wątpliwości, gdy szablon nazywa ją inaczej")
    args = parser.parse_args()
    try:
        issues = find_issues(args.document, args.mode, args.questions_heading)
    except ImportError:
        print("BRAK python-docx: nie można sprawdzić pliku .docx.")
        return 3
    for issue in issues:
        print(issue)
    print(f"Dopisków roboczych w dokumencie: {len(issues)} — {'PASS' if not issues else 'FAIL'}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
