"""Tworzy z wersji roboczej (Markdown) czystą wersję dla klienta i osobny rejestr pochodzenia.

Użycie:
  python make_client_version.py robocza.md --out czysta.md [--register rejestr.md] [--mode final|client]

Z treści usuwa i przenosi do rejestru pochodzenia:
- dopiski pochodzenia w nawiasie, które zaczynają się od SRC-, OPEN-, ASSUMPTION- (osobny akapit albo koniec zdania),
- znaczniki brakujących zrzutów `[ZRZUT: …]`,
- akapity robocze zaczynające się od „**Uwaga dla zespołu”,
- rozdziały robocze: „Tematy do wyjaśnienia”, „Materiały źródłowe”, „Rejestr…”, załączniki z „robocze” w tytule.

Tryb `final` (domyślny): każde pozostałe „DO POTWIERDZENIA” jest błędem; luki rozstrzyga autor w wersji roboczej
(uzupełnienie, pominięcie albo neutralne sformułowanie), a skrypt niczego nie zgaduje.
Tryb `client`: „DO POTWIERDZENIA (OPEN-NNN…)” zmienia się w „Do ustalenia (K-NN)”, a na końcu powstaje rozdział
„Kwestie do wyjaśnienia” z tematami z tabeli „Tematy do wyjaśnienia”.

Kody wyjścia: 0 = zapisano, 1 = w treści zostały luki (tryb final), 2 = błąd odczytu.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WORKING_HEADINGS = ("tematy do wyjaśnienia", "materiały źródłowe", "rejestr źródeł", "rejestr pochodzenia", "robocze")
SOURCE_NOTE = re.compile(r"\s*\((?:SRC|OPEN|ASSUMPTION)-\d{3}[^()]*(?:\([^()]*\)[^()]*)*\)")
SCREENSHOT = re.compile(r"\[ZRZUT:[^\]]*\]", re.I)
GAP = re.compile(r"DO POTWIERDZENIA(?:\s*\((OPEN-\d{3})[^)]*\))?\.?", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.*)")


def split_sections(lines: list[str]) -> list[tuple[str | None, int, list[str]]]:
    """Dzieli dokument na (nagłówek, poziom, wiersze sekcji)."""
    sections: list[tuple[str | None, int, list[str]]] = [(None, 0, [])]
    for line in lines:
        match = HEADING.match(line)
        if match:
            sections.append((match.group(2), len(match.group(1)), [line]))
        else:
            sections[-1][2].append(line)
    return sections


def open_topics(lines: list[str]) -> dict[str, list[str]]:
    topics = {}
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(r"OPEN-\d{3}", cells[0]):
            topics[cells[0]] = cells[1:]
    return topics


def convert(text: str, mode: str = "final") -> tuple[str, str, list[str]]:
    """Zwraca (czysta treść, rejestr pochodzenia, lista luk pozostawionych w treści)."""
    sections = split_sections(text.splitlines())
    kept: list[str] = []
    register: list[str] = []
    notes: list[str] = []
    screenshots: list[str] = []
    topics: dict[str, list[str]] = {}
    gaps: list[str] = []
    questions: dict[str, str] = {}

    def replace_gap(match: re.Match) -> str:
        open_id = match.group(1)
        if mode == "client":
            key = questions.setdefault(open_id or f"brak-{len(questions) + 1}", f"K-{len(questions) + 1:02d}")
            return f"Do ustalenia ({key})."
        gaps.append(match.group(0))
        return match.group(0)

    skip_level = 0
    current = "(początek)"
    for heading, level, lines in sections:
        if heading is not None:
            if skip_level and level <= skip_level:
                skip_level = 0
            if any(w in heading.casefold() for w in WORKING_HEADINGS):
                skip_level = level
            current = heading
        if skip_level:
            topics.update(open_topics(lines))
            register.extend(lines)
            register.append("")
            continue
        paragraph_skip = False
        for line in lines:
            if line.startswith("**Uwaga dla zespołu"):
                paragraph_skip = True
            if paragraph_skip:
                if not line.strip():
                    paragraph_skip = False
                continue
            line = GAP.sub(replace_gap, line)
            for shot in SCREENSHOT.findall(line):
                screenshots.append(f"- {current}: {shot}")
            for note in SOURCE_NOTE.findall(line):
                notes.append(f"| {current} | {note.strip()[1:-1]} |")
            cleaned = SCREENSHOT.sub("", SOURCE_NOTE.sub("", line)).rstrip()
            if line.strip() and not cleaned.strip():
                continue
            kept.append(cleaned)

    body = "\n".join(kept)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
    if mode == "client" and questions:
        rows = ["", "## Kwestie do wyjaśnienia", "", "| Nr | Kwestia | Czego dotyczy | Kto decyduje |", "|---|---|---|---|"]
        for open_id, key in questions.items():
            topic = topics.get(open_id, ["Do uzupełnienia", "", ""])
            rows.append(f"| {key} | {topic[0]} | {topic[1] if len(topic) > 1 else ''} | Do wskazania |")
        body += "\n".join(rows) + "\n"

    register_text = ["# Rejestr pochodzenia", "", "Plik wewnętrzny: pochodzenie treści czystej wersji dokumentu.", "",
                     "## Źródła według rozdziałów", "", "| Rozdział | Źródło |", "|---|---|", *notes, ""]
    if screenshots:
        register_text += ["## Brakujące zrzuty ekranu", "", *screenshots, ""]
    if questions:
        register_text += ["## Kwestie K-NN i tematy OPEN", "", *[f"- {k} = {o}" for o, k in questions.items()], ""]
    register_text += ["## Rozdziały robocze przeniesione z dokumentu", "", *register]
    return body, "\n".join(register_text).rstrip() + "\n", gaps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--register", type=Path)
    parser.add_argument("--mode", choices=("final", "client"), default="final")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        text = args.draft.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Nie można odczytać pliku: {exc}")
        return 2
    body, register, gaps = convert(text, args.mode)
    if gaps:
        for gap in gaps:
            print(f"LUKA: „{gap}” — rozstrzygnij w wersji roboczej (uzupełnij, pomiń albo neutralne sformułowanie)")
        print(f"Luk w treści: {len(gaps)} — nie zapisano czystej wersji")
        return 1
    args.out.write_text(body, encoding="utf-8")
    register_path = args.register or args.out.with_name(args.out.stem + "-rejestr-pochodzenia.md")
    register_path.write_text(register, encoding="utf-8")
    print(f"ZAPISANO: {args.out}\nRejestr pochodzenia: {register_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
