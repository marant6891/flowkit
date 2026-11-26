"""Kontrola kompletności pomocy lub dokumentacji rozwiązania względem katalogu opcji. Tylko czyta pliki.

Użycie:
  python check_coverage.py dokument.md|dokument.docx --catalog katalog-opcji.md [--min-modules 3]

Katalog opcji to tabela Markdown z kolumnami: ID (OPT-NNN), Element, ..., Status. Pozycja ze statusem
zaczynającym się od „pomin” (pominięta, pominięto) nie musi występować w dokumencie. Każda inna pozycja musi
mieć w dokumencie swoją nazwę z kolumny „Element” (bez pogrubienia, wielkość liter bez znaczenia).

Sprawdza też rysunki: obrazy w .docx, obrazy Markdown `![...](...)` i znaczniki `[[DIAGRAM:D-NN]]`. Gdy dokument
ma co najmniej `--min-modules` rozdziałów najwyższego poziomu, a nie ma żadnego rysunku, zgłasza ostrzeżenie.

Kody wyjścia: 0 = PASS (mogą być ostrzeżenia), 1 = brakujące pozycje, 2 = błąd odczytu, 3 = brak python-docx.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OPT_ID = re.compile(r"^OPT-\d{3}$")
DIAGRAM_MARKER = re.compile(r"\[\[DIAGRAM:D-\d+\]\]")
MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")


def clean(text: str) -> str:
    text = re.sub(r"[*_`„”\"]", "", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def load_catalog(path: Path) -> list[dict]:
    rows, header = [], None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or re.fullmatch(r"[|:\-\s]+", stripped):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", stripped.strip("|"))]
        if header is None or not OPT_ID.match(cells[0]):
            if cells and clean(cells[0]) == "id":
                header = [clean(c) for c in cells]
            continue
        record = dict(zip(header, cells))
        name = record.get("element (nazwa w interfejsie)") or record.get("element") or (cells[1] if len(cells) > 1 else "")
        status = next((v for k, v in record.items() if k.startswith("status")), "")
        rows.append({"id": cells[0], "name": name, "status": status})
    return rows


def document_text(path: Path) -> tuple[str, int, int]:
    """Zwraca (tekst, liczba rysunków, liczba rozdziałów najwyższego poziomu)."""
    if path.suffix.lower() in (".docx", ".dotx"):
        from docx_support import open_document

        doc = open_document(path)
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.extend(cell.text for cell in row.cells)
        images = len(doc.inline_shapes)
        text = "\n".join(parts)
        images += len(DIAGRAM_MARKER.findall(text))
        levels = []
        for p in doc.paragraphs:
            style = (p.style.name if p.style is not None else "") or ""
            level = re.search(r"(?:heading|nag\w*)\s*(\d)", style, re.I)
            if level and p.text.strip():
                levels.append(int(level.group(1)))
        top = min(levels) if levels else 1
        return text, images, levels.count(top)
    text = path.read_text(encoding="utf-8-sig")
    images = len(MD_IMAGE.findall(text)) + len(DIAGRAM_MARKER.findall(text))
    levels = [len(m.group(1)) for m in re.finditer(r"(?m)^(#{1,6})\s+\S", text)]
    top = min(levels) if levels else 1
    return text, images, levels.count(top)


def check(document: Path, catalog: Path, min_modules: int = 3) -> tuple[list[str], list[str], dict]:
    rows = load_catalog(catalog)
    text, images, chapters = document_text(document)
    haystack = clean(text)
    errors, warnings = [], []
    required = [r for r in rows if not clean(r["status"]).startswith("pomin")]
    skipped = len(rows) - len(required)
    for row in required:
        if not row["name"] or clean(row["name"]) not in haystack:
            errors.append(f"{row['id']} „{row['name']}” nie występuje w dokumencie")
    if not rows:
        errors.append("katalog opcji nie zawiera pozycji OPT-NNN")
    if images == 0 and chapters >= min_modules:
        warnings.append(f"dokument ma {chapters} rozdziałów i żadnego rysunku: oceń układ ekranu i procesy")
    stats = {"total": len(rows), "required": len(required), "skipped": skipped, "images": images,
             "chapters": chapters}
    return errors, warnings, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--min-modules", type=int, default=3)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        errors, warnings, stats = check(args.document, args.catalog, args.min_modules)
    except ImportError:
        print("BRAK python-docx: nie można sprawdzić pliku .docx (pip install python-docx).")
        return 3
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Nie można odczytać pliku: {exc}")
        return 2
    for message in errors:
        print(f"BRAK: {message}")
    for message in warnings:
        print(f"OSTRZEŻENIE: {message}")
    covered = stats["required"] - len([e for e in errors if e.startswith("OPT-")])
    print(f"Katalog opcji: {stats['total']} pozycji, wymagane {stats['required']}, opisane {covered}, "
          f"pominięte świadomie {stats['skipped']}; rysunki: {stats['images']} — {'PASS' if not errors else 'FAIL'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
