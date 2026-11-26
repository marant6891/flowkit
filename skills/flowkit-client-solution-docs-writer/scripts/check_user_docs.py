"""Kontrola dokumentacji rozwiązania lub pomocy dla użytkownika. Tylko czyta plik.

Użycie:
  python check_user_docs.py dokument.md|dokument.docx [--audience user|admin|tech] [--mode draft|client|final]
                                                       [--questions-heading TEKST] [--lang auto|pl|en]

--audience  profil odbiorcy: `user` (help dla użytkownika końcowego, bez języka kodu), `admin`, `tech`
--mode      `draft` (roboczy, oznaczenia źródeł dozwolone), `client` (wersja dla klienta, wątpliwości tylko
            w sekcji końcowej jako K-NN), `final` (końcowy bez dopisków)

Sprawdza: sekrety i adresy wewnętrzne, język kodu w pomocy dla użytkownika (pliki, endpointy, kody HTTP,
wyjątki, identyfikatory), oznaczenia robocze i znaczniki zrzutów w wersji dla klienta i końcowej, odwołania
K-NN / OPEN-NNN bez punktu w sekcji wątpliwości, długie myślniki, formułki AI, zbyt długie kroki oraz prosty
język według runtime/procedures/plain-language.md (w trybach client i final reguły FAIL są błędami).

Kody wyjścia: 0 = PASS (mogą być ostrzeżenia), 1 = błędy, 2 = nie można odczytać pliku, 3 = brak python-docx.
"""
from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

QUESTION_HEADINGS = ("kwestie do wyjaśnienia", "tematy do wyjaśnienia", "otwarte kwestie", "pytania otwarte")
# Sekcje dla zespołu w wersji roboczej: mogą zawierać nazwy plików i klucze, kontrola języka odbiorcy ich nie obejmuje.
WORKING_HEADINGS = ("materiały źródłowe", "rejestr źródeł", "rejestr pochodzenia", "tematy do wyjaśnienia", "robocze")
CODE_EXT = r"(?:cs|py|java|kt|ts|tsx|js|jsx|vue|sql|xml|json|ya?ml|config|properties|go|rb|php|razor|cshtml|html)"

SECRET = (
    re.compile(r"(?i)\b(hasło|haslo|password|passwd|pwd|token|api[_-]?key|secret|client[_-]?secret)\b\s*[:=]\s*[^\s`|]{3,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@"),
    re.compile(r"(?i)\b(server|data source)=[^;\n]+;[^\n]*\b(password|pwd)=[^;\s]+"),
    re.compile(r"\b(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,})\b"),
)
INTERNAL_HOST = re.compile(r"(?i)\b(localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}"
                           r"|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|[\w-]+\.(local|internal|corp|lan))\b")
WORKING_MARKERS = (
    (re.compile(r"\bSRC-\d+"), "oznaczenie źródła"),
    (re.compile(r"\bFEAT-\d+"), "identyfikator z katalogu funkcji"),
    (re.compile(r"\bASSUMPTION-\d+"), "identyfikator założenia"),
    (re.compile(r"\bOPEN-\d+"), "identyfikator tematu otwartego"),
    (re.compile(r"\bQ-\d{3}\b"), "identyfikator pytania"),
    (re.compile(r"DO POTWIERDZENIA", re.I), "„DO POTWIERDZENIA”"),
    (re.compile(r"\bBrak danych\b|\bNie analizowano\b", re.I), "dopisek roboczy"),
    (re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b"), "znacznik roboczy"),
    (re.compile(r"\[ZRZUT:[^\]]*\]", re.I), "znacznik brakującego zrzutu ekranu"),
    (re.compile(r"\[\[DIAGRAM:[^\]]*\]\]", re.I), "niezastąpiony znacznik diagramu"),
    (re.compile(rf"[\w./\\-]+\.{CODE_EXT}:\d+"), "odwołanie plik:linia"),
    (re.compile(r"\[(?:WPISZ[^\]]*|[A-ZĄĆĘŁŃÓŚŹŻ][A-ZĄĆĘŁŃÓŚŹŻ /_-]{2,}|\.\.\.|DD\.MM\.RRRR)\](?!\()"), "placeholder szablonu"),
    (re.compile(r"<!--"), "komentarz"),
    (re.compile(r"\[INJECTION\?\]"), "uwaga o podejrzanym fragmencie"),
)
# Język kodu, który nie należy do pomocy dla użytkownika końcowego.
CODE_LANGUAGE = (
    (re.compile(rf"(?<![\w/])[\w-]+(?:[/\\][\w.-]+)*\.{CODE_EXT}\b"), "nazwa pliku z kodu"),
    (re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/[\w/{}<>:.-]*"), "endpoint API"),
    (re.compile(r"(?i)\b(HTTP\s*\d{3}|(błąd|kod|status)\w*\s+(4\d\d|5\d\d)\b)"), "kod HTTP"),
    (re.compile(r"\b[A-Z]\w*(Exception|Error)\b"), "nazwa wyjątku"),
    (re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b"), "identyfikator snake_case"),
    (re.compile(r"\b[a-z]+[A-Z]\w*\("), "wywołanie metody"),
    (re.compile(r"\b[a-z]\w*\.[a-z]\w*\s*(==|!=|=)"), "warunek z kodu"),
)
JARGON = re.compile(r"(?i)\b(endpoint\w*|request\w*|payload|response|backend\w*|frontend\w*|cache|stack ?trace"
                    r"|JSON|null|boolean|string|enum)\b")
DASH = re.compile(r"[—–]")
AI_PHRASES = re.compile(r"(?i)niniejszy dokument|należy zauważyć|warto podkreślić|w tej sekcji (opisano|przedstawiono)"
                        r"|poniższa tabela przedstawia|w niniejszym rozdziale")
SOURCE_NOTE = re.compile(r"\((?:SRC-\d+|interpretacja)[^)]*\)")
SOURCE_HEADER = re.compile(r"^\s*źródł[oa]\s*$", re.I)
QUESTION_REF = re.compile(r"\bK-\d{2,3}\b")
QUESTION_ITEM = re.compile(r"^\W*(K-\d{2,3})\b")
OPEN_REF = re.compile(r"\bOPEN-\d{3}\b")
MAX_STEP_WORDS = 30


class Block:
    def __init__(self, where: str, text: str, heading: int = 0, cells: list[str] | None = None,
                 step: bool = False, code: bool = False, mermaid: bool = False) -> None:
        self.where, self.text, self.heading = where, text, heading
        self.cells, self.step, self.code, self.mermaid = cells or [], step, code, mermaid


def markdown_blocks(path: Path) -> list[Block]:
    blocks, fenced = [], False
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stripped_left = line.lstrip()
        if stripped_left.startswith("```"):
            if not fenced and stripped_left[3:].strip().casefold() == "mermaid":
                blocks.append(Block(f"wiersz {number}", stripped_left, code=True, mermaid=True))
            fenced = not fenced
            continue
        if not line.strip():
            continue
        where = f"wiersz {number}"
        if fenced:
            blocks.append(Block(where, line, code=True))
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)", line)
        stripped = line.strip()
        if stripped.startswith("|"):
            if re.fullmatch(r"[|:\-\s]+", stripped):
                continue
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", stripped.strip("|"))]
            blocks.append(Block(where, stripped, cells=cells))
        elif heading:
            blocks.append(Block(where, heading.group(2), len(heading.group(1))))
        else:
            blocks.append(Block(where, line, step=bool(re.match(r"^\s*\d+[.)]\s", line))))
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
            step = bool(re.search(r"(?i)list\s*number|lista\s*numer", style))
            code = bool(re.search(r"(?i)code|kod|source", style))
            blocks.append(Block(f"akapit {paragraph_no}", paragraph.text, int(level.group(1)) if level else 0,
                                step=step, code=code))
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


# Te reguły prostego języka sprawdza już ten skrypt, więc nie są powtarzane.
OWN_PLAIN_RULES = {"NS-1", "NS-3"}


def load_plain_language():
    """Wspólny moduł FlowKit (runtime/plain_language.py): wtyczka, instalacja Claude Code lub VS Code."""
    here = Path(__file__).resolve()
    candidates = [Path(os.environ["FLOWKIT_RUNTIME"])] if os.environ.get("FLOWKIT_RUNTIME") else []
    candidates += [here.parents[3] / "runtime", here.parents[3] / "flowkit" / "runtime",
                   Path.home() / ".claude" / "flowkit" / "runtime"]
    for directory in candidates:
        if (directory / "plain_language.py").is_file():
            if str(directory) not in sys.path:
                sys.path.insert(0, str(directory))
            return importlib.import_module("plain_language")
    return None


def plain_language_check(body: list[Block], audience: str, mode: str,
                         lang: str) -> tuple[list[str], list[str]] | None:
    """Prosty język w całej treści (bez kodu); None, gdy modułu nie ma w instalacji."""
    module = load_plain_language()
    if module is None:
        return None
    starts: list[tuple[int, Block]] = []
    parts: list[str] = []
    line = 1
    for block in body:
        if block.code or not block.text.strip():
            continue
        starts.append((line, block))
        parts.append(block.text)
        line += block.text.count("\n") + 2
    findings = module.check_text("\n\n".join(parts), lang=lang, strict=mode in ("client", "final"),
                                 audience="user" if audience == "user" else "tech")
    errors: list[str] = []
    warnings: list[str] = []
    for finding in findings:
        if finding.rule_id in OWN_PLAIN_RULES:
            continue
        block = next(b for start, b in reversed(starts) if start <= finding.line)
        message = f"{block.where}: prosty język {finding.rule_id}: {finding.message} [{finding.excerpt}]"
        (errors if finding.level == module.FAIL else warnings).append(message)
    return errors, warnings


def check_blocks(blocks: list[Block], audience: str = "user", mode: str = "draft",
                 heading_text: str | None = None, lang: str = "auto") -> tuple[list[str], list[str]]:
    """Zwraca (błędy, ostrzeżenia)."""
    errors: list[str] = []
    warnings: list[str] = []
    body, questions = split_questions(blocks, heading_text)

    for block in blocks:
        if any(p.search(block.text) for p in SECRET):
            errors.append(f"{block.where}: hasło, klucz, token lub dane logowania w treści — usuń wartość")
        host = INTERNAL_HOST.search(block.text)
        if host:
            target = errors if audience == "user" else warnings
            target.append(f"{block.where}: adres wewnętrzny „{host.group(0)}” — sprawdź, czy odbiorca ma go znać")

    working_level = 0  # poziom nagłówka otwartej sekcji roboczej (0 = poza nią)
    for block in body:
        if block.heading:
            if working_level and block.heading <= working_level:
                working_level = 0
            if mode == "draft" and any(w in block.text.casefold() for w in WORKING_HEADINGS):
                working_level = block.heading
        if block.mermaid and mode in ("client", "final"):
            errors.append(f"{block.where}: surowy blok mermaid w dokumencie dla klienta — wygeneruj i osadź rysunek przez silnik diagramów")
        if block.code or working_level:
            continue
        text = SOURCE_NOTE.sub("", block.text) if mode == "draft" else block.text
        if mode in ("client", "final"):
            for pattern, label in WORKING_MARKERS:
                match = pattern.search(text)
                if match:
                    errors.append(f"{block.where}: {label} „{match.group(0)}” w treści dokumentu")
            if any(SOURCE_HEADER.match(cell) for cell in block.cells):
                errors.append(f"{block.where}: kolumna „Źródło” w treści dokumentu")
            if DASH.search(text):
                errors.append(f"{block.where}: długi myślnik (— lub –) — użyj przecinka, dwukropka lub łącznika")
        elif DASH.search(text):
            warnings.append(f"{block.where}: długi myślnik (— lub –)")
        if mode == "final":
            ref = QUESTION_REF.search(text)
            if ref:
                errors.append(f"{block.where}: odwołanie {ref.group(0)} do kwestii otwartej w dokumencie końcowym")
        if audience == "user":
            # Nazwy w czcionce kodu (np. ustawienia) nie należą do pomocy dla użytkownika.
            plain = re.sub(r"`[^`]*`", lambda m: m.group(0).strip("`"), text)
            for pattern, label in CODE_LANGUAGE:
                match = pattern.search(plain)
                if match:
                    errors.append(f"{block.where}: {label} „{match.group(0)}” w pomocy dla użytkownika")
                    break
            jargon = JARGON.search(plain)
            if jargon:
                warnings.append(f"{block.where}: żargon techniczny „{jargon.group(0)}” — użyj słów z interfejsu")
            if "`" in text:
                warnings.append(f"{block.where}: tekst w czcionce kodu w pomocy dla użytkownika")
        ai = AI_PHRASES.search(text)
        if ai:
            warnings.append(f"{block.where}: formułka „{ai.group(0)}” — usuń")
        if block.step:
            words = len(re.sub(r"^\s*\d+[.)]\s*", "", text).split())
            if words > MAX_STEP_WORDS:
                warnings.append(f"{block.where}: krok ma {words} słów — podziel na kroki (jedna czynność na krok)")

    # Ostrzegaj przed powierzchownymi sekcjami-zaślepkami (## bez podsekcji, tabel i z < 15 słowami).
    for idx, block in enumerate(body):
        if block.heading != 2:
            continue
        if any(w in block.text.casefold() for w in WORKING_HEADINGS + QUESTION_HEADINGS):
            continue
        sec_blocks: list[Block] = []
        for nxt in body[idx + 1:]:
            if 0 < nxt.heading <= 2:
                break
            sec_blocks.append(nxt)
        if any(b.heading > 2 or b.cells or b.code for b in sec_blocks):
            continue
        sec_words = sum(len(b.text.split()) for b in sec_blocks)
        if 0 < sec_words < 15:
            warnings.append(f"{block.where}: sekcja „{block.text}” ma tylko {sec_words} słów — rozwiń treść z kodu albo pomiń")

    defined = set()
    for block in questions:
        first = block.cells[0] if block.cells else block.text
        item = QUESTION_ITEM.match(first) or re.match(r"^\W*(OPEN-\d{3})\b", first)
        if item:
            defined.add(item.group(1))
    if mode == "client":
        for block in questions:
            for pattern, label in WORKING_MARKERS[:5]:
                match = pattern.search(block.text)
                if match:
                    errors.append(f"{block.where}: {label} „{match.group(0)}” w sekcji wątpliwości (użyj K-NN)")
        for block in body:
            for ref in QUESTION_REF.findall(block.text):
                if ref not in defined:
                    errors.append(f"{block.where}: odwołanie {ref} bez punktu w sekcji wątpliwości")
    elif mode == "draft":
        missing = sorted({ref for b in body for ref in OPEN_REF.findall(b.text)} - defined)
        if missing:
            warnings.append("tematy bez wiersza w „Tematach do wyjaśnienia”: " + ", ".join(missing))
    plain = plain_language_check(body, audience, mode, lang)
    if plain is None:
        warnings.append("brak modułu plain_language w runtime FlowKit: reguły prostego języka nie zostały sprawdzone")
    else:
        errors.extend(plain[0])
        warnings.extend(plain[1])
    return errors, warnings


def check_file(path: Path, audience: str = "user", mode: str = "draft",
               heading_text: str | None = None, lang: str = "auto") -> tuple[list[str], list[str]]:
    blocks = docx_blocks(path) if path.suffix.lower() in (".docx", ".dotx") else markdown_blocks(path)
    return check_blocks(blocks, audience, mode, heading_text, lang)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--audience", choices=("user", "admin", "tech"), default="user")
    parser.add_argument("--mode", choices=("draft", "client", "final"), default="draft")
    parser.add_argument("--questions-heading", help="nagłówek sekcji wątpliwości, gdy szablon nazywa ją inaczej")
    parser.add_argument("--lang", choices=("auto", "pl", "en"), default="auto")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        errors, warnings = check_file(args.document, args.audience, args.mode, args.questions_heading, args.lang)
    except ImportError:
        print("BRAK python-docx: nie można sprawdzić pliku .docx (pip install python-docx).")
        return 3
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Nie można odczytać pliku: {exc}")
        return 2
    for message in errors:
        print(f"BŁĄD: {message}")
    for message in warnings:
        print(f"OSTRZEŻENIE: {message}")
    print(f"Błędy: {len(errors)}, ostrzeżenia: {len(warnings)} — {'PASS' if not errors else 'FAIL'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
