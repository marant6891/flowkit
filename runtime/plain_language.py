"""Kontrola prostego języka (PL i EN) według runtime/procedures/plain-language.md. Tylko czyta pliki.

Użycie: python plain_language.py <plik> [...] [--lang auto|pl|en] [--strict] [--audience tech|user]
                                 [--glossary flowkit-project.md]
  --strict    tryb końcowy: reguły oznaczone FAIL blokują wynik (kod wyjścia 1)
  --audience  user: tekst dla użytkownika końcowego (dodatkowe reguły, np. „komponent”)
  --glossary  plik z dozwolonymi terminami; domyślnie flowkit-project.md w bieżącym katalogu, jeśli istnieje

Reguły z poziomem PRZEGLĄD (szyk, strona bierna) nie są sprawdzane skryptem: ocenia je autor lub verifier.
Kody wyjścia: 0 = brak błędów (mogą być ostrzeżenia), 1 = błędy w trybie końcowym, 2 = nie można odczytać pliku.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WARN = "WARN"
FAIL = "FAIL"
SENTENCE_LIMITS = {"pl": (20, 35), "en": (25, 35)}  # (ostrzeżenie powyżej, błąd w trybie końcowym powyżej)
DEFAULT_GLOSSARY = {
    "API", "UI", "UX", "SQL", "SLA", "SLO", "URL", "HTTP", "HTTPS", "JSON", "XML", "YAML", "PDF", "DOCX", "CSV",
    "ID", "IT", "OK", "CI", "CD", "PR", "QA", "AI", "PL", "EN", "UTC", "CET", "VPN", "DNS", "IP", "SSO", "MFA",
    "PT", "PRD", "MVP", "PM", "PO", "RODO", "GDPR", "NIP", "PESEL", "REGON", "VAT", "PLN", "EUR", "USD", "FAQ",
    "CPU", "RAM", "GB", "MB", "TB", "KB", "DB", "ERP", "CRM", "ETL", "BI", "KPI", "ITP", "TJ", "NP", "CEO",
    "CTO", "IOS", "MS", "SMS", "RAID", "HR", "UE", "EU", "USA", "UK", "SVG", "PNG", "JPG", "GIF", "HTML", "CSS",
    "JS", "TS", "VS", "SRE", "UAT", "OWASP", "MCP", "JWT", "SSH", "TLS", "SSL", "LLM", "SDK", "CLI", "OS", "PC",
    # Etykiety FlowKit w wynikach skilli (tryby, kanały, statusy, klasy działań): nazwy, nie krzyk.
    "ZWYKŁY", "DUPOKRYTKA", "EMAIL", "WIADOMOŚĆ", "AUTO", "OPEN", "PREVENT", "DETECT", "MITIGATE", "SEV",
    "PASS", "FAIL", "WARN", "UNKNOWN", "NOT_RUN", "ROLLBACK", "COMMIT", "UKRYTO",
}
WORD = re.compile(r"[0-9A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]")
ABBREVIATION = re.compile(r"(?<![\w/.-])([A-ZĄĆĘŁŃÓŚŹŻ]{2,5})s?(?![\w/.-])")
SENTENCE_END = re.compile(r"(?<=[.!?…])\s+(?=[„\"(\[]?[A-ZĄĆĘŁŃÓŚŹŻ0-9])")
LIST_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}")
# Celowe złe przykłady (np. kolumna „Zamiast” w tabeli zwrotów) wyłącza się komentarzami HTML.
PLAIN_OFF = re.compile(r"^<!--\s*plain-check:\s*off\s*-->$", re.IGNORECASE)
PLAIN_ON = re.compile(r"^<!--\s*plain-check:\s*on\s*-->$", re.IGNORECASE)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    lang: str  # pl, en albo all
    pattern: re.Pattern
    level: str  # poziom w trybie końcowym
    message: str
    audience: str = "all"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    level: str
    line: int
    message: str
    excerpt: str


def _r(rule_id: str, lang: str, pattern: str, level: str, message: str, flags: int = re.IGNORECASE,
       audience: str = "all") -> Rule:
    return Rule(rule_id, lang, re.compile(pattern, flags), level, message, audience)


MONTHS = r"(stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|październik|listopad|grud)\w*"
RULES: tuple[Rule, ...] = (
    # Polski: wata i nominalizacje (gov.pl i FK)
    _r("PL-W1", "pl", r"\bdokon(a|y)\w*\s+\w+", FAIL, "„dokonać X” zamień na czasownik: „zmienić”, „kupić”"),
    _r("PL-Z3", "pl", r"\b(przeprowadz|wykon|zrealiz)\w*\s+(analiz|weryfikac|aktualizac|modyfikac|zmian|sprawdzeni|wdrożeni)\w*",
       WARN, "czasownik zamiast rzeczownika: „przeanalizować”, „sprawdzić”, „wdrożyć”"),
    _r("PL-W2", "pl", r"\bule(gł|gła|gło|gły|c|ga|gają)\s+(pogorszeniu|poprawie|zmianie|skróceniu|wydłużeniu|zwiększeniu|zmniejszeniu)",
       WARN, "„uległ pogorszeniu” zamień na „pogorszył się”"),
    _r("PL-W3", "pl", r"\bw dniu (dzisiejszym|jutrzejszym|wczorajszym)", FAIL, "pisz „dziś”, „jutro”, „wczoraj”"),
    _r("PL-W4", "pl", rf"\bw miesiącu {MONTHS}", FAIL, "„w miesiącu maju” zamień na „w maju”"),
    _r("PL-W5", "pl", r"\bcelem\s+\w+(ania|enia|acji|cia)\b", WARN, "„celem X” zamień na „aby”, „żeby”"),
    _r("PL-W6", "pl", r"\bniniejsz\w*", FAIL, "„niniejszy” zamień na „ten”"),
    _r("PL-W7", "pl", r"\bdedykowan\w*", WARN, "„dedykowany” zamień na „przeznaczony dla”, „osobny”"),
    _r("PL-W8", "pl", r"\bkomponent\w*", WARN, "w tekście dla użytkownika: „składnik”, „część”, „element”",
       audience="user"),
    _r("PL-W9", "pl", r"\bw chwili obecnej\b|\bna chwilę obecną\b", WARN, "pisz „teraz”, „obecnie”"),
    _r("PL-W10", "pl", r"\bposiad(a|ać|ał|ała|ało|ali|ały|aj|ają|amy|acie|asz|any|ana|ane|ani)\b", WARN,
       "„posiadać” w znaczeniu „mieć” zamień na „mieć”"),
    _r("PL-W11", "pl", r"\bw oparciu o\b", WARN, "pisz „na podstawie”"),
    _r("PL-W12", "pl", r"\bw związku z (tym )?faktem\b|\bz uwagi na fakt\b|\bze względu na fakt\b", WARN,
       "pisz „bo”, „ponieważ”"),
    # Polski: korpomowa i kalki leksykalne (OJ UW i FK)
    _r("PL-K1", "pl", r"\bzaparkow\w*|\bzaparkuj\w*", WARN, "korpomowa: „odłóżmy to, wrócimy do tego [kiedy]”"),
    _r("PL-K2", "pl", r"\bpołącz\w*\s+kropk\w*", WARN, "korpomowa: „powiązać fakty”, „wyciągnąć wniosek”"),
    _r("PL-K3", "pl", r"\bsto(i|ją|ać|ał\w*)\s+w\s+sprzeczności", WARN, "pisz „przeczy”, „jest sprzeczne z”"),
    _r("PL-K4", "pl", r"\bzaadresow\w*", WARN, "korpomowa: „zająć się”, „odpowiedzieć na”"),
    _r("PL-K5", "pl", r"\bdowie(źć|ziemy|zie|ziesz|zą|źli|ziony|ziona|zione|zł|zła|zło)\b", WARN,
       "korpomowa: „dostarczyć”, „wdrożyć”, „skończyć”"),
    _r("PL-K6", "pl", r"\bna ten moment\b", WARN, "pisz „teraz”, „na razie”"),
    _r("PL-K7", "pl", r"\bro(bi|bią|bić|biło)\s+sens\b", WARN, "kalka: „ma sens”"),
    _r("PL-K8", "pl", r"\bna tej samej stronie\b", WARN, "kalka: „zgadzamy się”, „rozumiemy tak samo”"),
    _r("PL-K9", "pl", r"\bna koniec dnia\s*,", WARN, "kalka: „ostatecznie”, „w sumie”"),
    _r("PL-K10", "pl", r"\bASAP\b", WARN, "podaj termin: „do [data]” albo „jak najszybciej”"),
    # Polski: kalki składniowe (Górnicz, PAN)
    _r("PL-P4", "pl", r"\bto\s+(jest\s+)?(już\s+)?(nie\s+)?(pierwsz|drug|trzec|czwart|kolejn|ostatn)\w*\s+raz,?\s+(gdy|kiedy)\b",
       WARN, "kalka „it's the second time that”: pisz „po raz drugi”"),
    _r("PL-P5", "pl", r"\b(uży|wykorzysta)(ł|li|ła|ły|liśmy|łem|łam|my|j|jcie|ć)\s+[^.!?\n]{1,40}?,?\s+(by|aby|żeby)\b",
       WARN, "kalka „used X to”: narzędzie w narzędniku, np. „przenieśliśmy dane skryptem”"),
    _r("PL-P6", "pl", r"\bTo,\s+(co|czego|czym|czemu)\b[^.!?]{1,150}?,\s*to\b", WARN,
       "kalka „What… is…”: zmień szyk, np. „Prace blokuje brak dostępu”", flags=0),
    _r("PL-P7", "pl", r"^Był(a|o|y)?\s+[^.!?,]{1,40},\s+(kiedy|gdy)\b", WARN,
       "kalka „It was X when”: pisz okolicznik czasu, np. „W poniedziałek…”", flags=0),
    _r("PL-P8", "pl", r"^(To\s+może\s+zająć\b[^.!?]*\bzanim\b|(To było|Było to|To jest)\s+(\w+\s+){0,3}\w+(ące|ne|ny|we|wy)\s+(\w+\s+){0,2}\w+ć\b)",
       WARN, "puste „to” jako podmiot: zacznij od czynności lub oceny, np. „Dotarcie do… może zająć”", flags=0),
    # English (Federal Plain Language Guidelines, GOV.UK, FK)
    _r("EN-W1", "en", r"\b(make|makes|made|making)\s+(a\s+)?(decision|recommendation|assessment)s?\b"
       r"|\b(carry|carries|carried|carrying)\s+out\s+(an?\s+)?(analysis|review|assessment|investigation)\b"
       r"|\bprovid\w*\s+assistance\b", WARN, "use the verb: decide, analyse, help"),
    _r("EN-W2", "en", r"\bin order to\b", WARN, "write „to”"),
    _r("EN-W3", "en", r"\bat (this|the present) (point in )?time\b", FAIL, "write „now”"),
    _r("EN-W4", "en", r"\b(due to|in view of|owing to) the fact that\b", WARN, "write „because”"),
    _r("EN-W5", "en", r"\bprior to\b|\bsubsequent to\b", WARN, "write „before”, „after”"),
    _r("EN-W6", "en", r"\bwith (regard|regards|respect) to\b|\bin relation to\b", WARN, "write „about”"),
    _r("EN-W7", "en", r"\butili[sz]\w*|\bcommenc\w*|\bfacilitat\w*", WARN, "write „use”, „start”, „help”"),
    _r("EN-W8", "en", r"\bdo(n't| not) hesitate\b", WARN, "write „contact us if you have questions”"),
    _r("EN-K1", "en", r"\bleverag\w*", WARN, "corporate jargon: write „use”"),
    _r("EN-K2", "en", r"\bgoing forward\b", WARN, "write „from now on”, „in future”"),
    _r("EN-K3", "en", r"\bcircl\w*\s+back\b|\btouch(ing)?\s+base\b", WARN, "say what and when: reply, talk, meet"),
    _r("EN-K4", "en", r"\bdeep[- ]dives?\b", WARN, "write „detailed review”, „analysis”"),
    _r("EN-K5", "en", r"\blow[- ]hanging fruit", WARN, "write „quick wins”, „easy changes”"),
    _r("EN-K6", "en", r"\brobust\b|\bstreamlin\w*|\bsynerg\w*", WARN, "say what it does, with a number if you can"),
    _r("EN-K7", "en", r"\bpark\w*\s+(this|that|the)\s+(topic|question|issue|discussion)", WARN,
       "write „come back to this on [date]”"),
    _r("EN-F1", "en", r"\bactual\s+(version|status|state|data|price|list|plan|schedule|situation|release)\b", WARN,
       "false friend (aktualny): write „current”"),
    _r("EN-F2", "en", r"\bactually\s+(we|I)\s+(are|am|'re|'m)\s+\w+ing\b", WARN,
       "false friend (aktualnie): write „currently”"),
    _r("EN-F3", "en", r"\beventually,?\s+(we|you|I)\s+(can|could|may|might)\b", WARN,
       "false friend (ewentualnie): write „if needed”, „possibly”"),
    _r("EN-F4", "en", r"\breali[sz]\w*\s+(the\s+|this\s+|a\s+|our\s+|your\s+)?(project|task|order|contract|plan|delivery|implementation)",
       WARN, "calque (realizować): write „carry out”, „deliver”"),
    _r("EN-F6", "en", r"\baccording to (me|us)\b", WARN, "write „in my view”, „in our view”"),
    _r("EN-F7", "en", r"\bbasing on\b", WARN, "write „based on”"),
    _r("EN-F8", "en", r"\bquestions?\s+to\s+(you|him|her|them)\b", WARN, "write „a question for you”"),
    _r("EN-F9", "en", r"\bin (the )?attachment,?\s+(I|we)\s+(send|sent)\b", WARN, "write „I've attached”"),
    _r("EN-F10", "en", r"\b(we|I)\s+(are|am|'re|'m)\s+after\s+the\b", WARN, "calque: write „we had the meeting”"),
    _r("EN-F12", "en", r"\bconcretely\b", WARN, "write „specifically”"),
    # Styl naturalny (oba języki)
    _r("NS-1", "all", r"[—–]", FAIL, "półpauza lub pauza: użyj „-”, przecinka lub dwukropka"),
    _r("NS-2", "all", "[\U0001F300-\U0001FAFF☀-➿]", FAIL, "emoji ozdobne"),
    _r("NS-3", "all", r"\bwarto podkreślić\b|\bnależy zauważyć\b|\bmam nadzieję, że (ta )?wiadomość\b"
       r"|\bhope this (e-?mail|message) finds you\b|\bit is (worth noting|important to note)\b", WARN, "formułka AI lub wata"),
    _r("NS-4", "all", r"!{2,}", WARN, "kilka wykrzykników"),
)
CAPS_WORD = re.compile(r"\b[A-ZĄĆĘŁŃÓŚŹŻ]{6,}\b")
CAPS_RUN = re.compile(r"\b[A-ZĄĆĘŁŃÓŚŹŻ]{2,}(?:[ ,]+[A-ZĄĆĘŁŃÓŚŹŻ]{2,}){2,}\b")  # trzy i więcej słów wielkimi literami


def detect_language(text: str) -> str:
    polish = len(re.findall(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", text)) + 3 * len(
        re.findall(r"(?i)\b(i|w|z|na|się|nie|jest|że|do|to|oraz|dla)\b", text))
    english = 3 * len(re.findall(r"(?i)\b(the|and|of|to|is|are|for|with|that|this|we|you)\b", text))
    return "pl" if polish >= english else "en"


def load_glossary(path: Path | None) -> set[str]:
    """Terminy z sekcji „terminologia” lub „Słownik” pliku projektu: wiersze „- termin = znaczenie” lub listy po przecinku."""
    if path is None or not path.is_file():
        return set()
    terms: set[str] = set()
    section = None  # "glossary": każdy punkt to termin; "terms": tylko „Terminy…: a, b” i „termin = znaczenie”
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("#"):
            section = ("glossary" if re.search(r"(?i)słownik|glossary", line)
                       else "terms" if re.search(r"(?i)terminolog", line) else None)
            continue
        if section is None or not LIST_ITEM.match(line):
            continue
        item = LIST_ITEM.sub("", line)
        if re.match(r"(?i)\s*terminy[^:]*:", item):
            item = item.split(":", 1)[1]
        elif section == "terms" and " = " not in item:
            continue
        for part in re.split(r"[,;]", item):
            term = re.split(r"\s*[=:(]\s*", part.strip(), maxsplit=1)[0].strip(" `*[]")
            if term:
                terms.add(term)
    return terms


def _clean(text: str) -> str:
    """Usuwa to, czego reguły nie dotyczą: kod, adresy URL, cytaty, znaczniki do uzupełnienia, cel linków."""
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"\]\([^)\s]*\)", "]", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"„[^”\n]*”|\"[^\"\n]*\"|“[^”\n]*”", "„”", text)
    text = re.sub(r"\[[A-ZĄĆĘŁŃÓŚŹŻ][A-ZĄĆĘŁŃÓŚŹŻ ]{2,}[^\]\n]*\]", " ", text)
    text = re.sub(r"<!--.*?-->|<[^>\n]+>", " ", text)
    return text.replace("**", "").replace("__", "")


def blocks(text: str) -> list[tuple[int, str]]:
    """Dzieli Markdown lub zwykły tekst na bloki: akapity, punkty list, nagłówki i komórki tabel (z numerem wiersza)."""
    result: list[tuple[int, str]] = []
    current: list[str] = []
    start = 0
    fence = False

    def flush() -> None:
        if current:
            result.append((start, "\n".join(current)))
            current.clear()

    lines = text.splitlines()
    frontmatter_end = 0
    if lines and lines[0].strip() == "---":  # nagłówek YAML (np. SKILL.md) to metadane, nie tekst
        frontmatter_end = next((i + 1 for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), 0)
    disabled = False
    for number, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if number <= frontmatter_end:
            continue
        if PLAIN_OFF.match(stripped) or PLAIN_ON.match(stripped):
            flush()
            disabled = bool(PLAIN_OFF.match(stripped))
            continue
        if stripped.startswith(("```", "~~~")):
            flush()
            fence = not fence
            continue
        if disabled or fence or raw.startswith(("    ", "\t")) and not current:
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith("|"):
            flush()
            if not TABLE_SEPARATOR.match(stripped):
                result.extend((number, cell) for cell in stripped.strip("|").split("|") if cell.strip())
            continue
        if stripped.startswith(("#", ">")) or LIST_ITEM.match(raw):
            flush()
            start = number
            current.append(re.sub(r"^#+\s*|^>\s*", "", LIST_ITEM.sub("", raw)))
            if stripped.startswith("#"):
                flush()
            continue
        if not current:
            start = number
        current.append(stripped)
    flush()
    return result


def sentences(block: str) -> list[tuple[int, str]]:
    """Zdania w bloku z przesunięciem wiersza względem początku bloku."""
    result = []
    position = 0
    for part in SENTENCE_END.split(block):
        index = block.find(part, position)
        position = index + len(part)
        if part.strip():
            result.append((block.count("\n", 0, max(index, 0)), part.strip()))
    return result


def _excerpt(text: str, limit: int = 70) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def check_text(text: str, lang: str = "auto", strict: bool = False, audience: str = "tech",
               glossary: set[str] | frozenset[str] = frozenset()) -> list[Finding]:
    """Zwraca naruszenia. W trybie roboczym (strict=False) każde naruszenie ma poziom WARN."""
    language = detect_language(text) if lang == "auto" else lang
    allowed = {term.upper() for term in DEFAULT_GLOSSARY | set(glossary)}
    rules = [r for r in RULES if r.lang in ("all", language) and r.audience in ("all", audience)]
    warn_limit, fail_limit = SENTENCE_LIMITS[language]
    findings: list[Finding] = []
    seen_abbreviations: set[str] = set()
    cleaned_blocks = [(line, _clean(block)) for line, block in blocks(text)]
    cleaned_text = "\n".join(block for _, block in cleaned_blocks)

    def add(rule_id: str, level: str, line: int, message: str, excerpt: str) -> None:
        findings.append(Finding(rule_id, level if strict else WARN, line, message, _excerpt(excerpt)))

    for line, block in cleaned_blocks:
        for offset, sentence in sentences(block):
            number = line + offset
            words = sum(1 for token in sentence.split() if WORD.search(token))
            if words > warn_limit:
                level = FAIL if words > fail_limit else WARN
                add(f"{language.upper()}-Z1", level, number, f"zdanie ma {words} słów (limit {warn_limit})", sentence)
            for rule in rules:
                match = rule.pattern.search(sentence)
                if match:
                    add(rule.rule_id, rule.level, number, rule.message, match.group(0))
            shouting = CAPS_RUN.search(sentence)
            if shouting:
                add("NS-4", WARN, number, "WIELKIE LITERY dla nacisku", shouting.group(0))
            else:
                for word in CAPS_WORD.findall(sentence):
                    if word.upper() not in allowed:
                        add("NS-4", WARN, number, "WIELKIE LITERY dla nacisku", word)
            for match in ABBREVIATION.finditer(CAPS_RUN.sub(" ", sentence)):
                abbreviation = match.group(1)
                if abbreviation in seen_abbreviations or abbreviation.upper() in allowed or len(abbreviation) > 5:
                    continue
                seen_abbreviations.add(abbreviation)
                explained = re.search(rf"\({re.escape(abbreviation)}s?\)|\b{re.escape(abbreviation)}s?\s*\([^)]{{4,}}\)",
                                      cleaned_text)
                if not explained:
                    add(f"{language.upper()}-S4", WARN, number, "skrót bez rozwinięcia przy pierwszym użyciu", abbreviation)
    return sorted(findings, key=lambda f: (f.line, f.rule_id))


def report(findings: list[Finding], name: str, language: str, strict: bool) -> str:
    lines = [f"{f.level} {f.rule_id} {name}:{f.line}: {f.message} [{f.excerpt}]" for f in findings]
    fails = sum(f.level == FAIL for f in findings)
    lines.append(f"{name}: FAIL {fails} · WARN {len(findings) - fails} · język {language} · "
                 f"tryb {'końcowy' if strict else 'roboczy'}")
    return "\n".join(lines)


def read_text(path: Path) -> str:
    if path.suffix.lower() in (".docx", ".dotx", ".pdf", ".xlsx"):
        import flowkit_exec  # odczyt dokumentów z executora (ten sam katalog runtime)

        return "\n".join(flowkit_exec.document_lines(path))
    return path.read_text(encoding="utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="plain-check", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--lang", choices=("auto", "pl", "en"), default="auto")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--audience", choices=("tech", "user"), default="tech")
    parser.add_argument("--glossary", type=Path)
    args = parser.parse_args(argv)
    glossary_path = args.glossary or (Path("flowkit-project.md") if Path("flowkit-project.md").is_file() else None)
    glossary = load_glossary(glossary_path)
    code = 0
    for path in args.files:
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError, ValueError, KeyError) as error:
            print(f"BŁĄD: nie można odczytać pliku {path}: {error}")
            code = 2
            continue
        language = detect_language(text) if args.lang == "auto" else args.lang
        findings = check_text(text, language, args.strict, args.audience, glossary)
        print(report(findings, str(path), language, args.strict))
        if code == 0 and any(f.level == FAIL for f in findings):
            code = 1
    return code


if __name__ == "__main__":
    sys.exit(main())
