"""Lokalna kontrola wersji wiadomości do wysłania klientowi. Tylko czyta plik.

Użycie: python check_message.py wiadomosc.txt [--mode zwykly|dupokrytka] [--channel email|wiadomosc]
                                             [--final] [--silence-agreed] [--lang auto|pl|en]
  --final           wersja ostateczna: niewypełnione `[DO UZUPEŁNIENIA: …]` są błędem, a reguły FAIL
                    prostego języka (runtime/procedures/plain-language.md) są błędami
  --silence-agreed  umowa lub procedura pozwala uznać brak odpowiedzi za akceptację
  --lang            język wiadomości dla reguł prostego języka (domyślnie rozpoznawany z treści)
Kody wyjścia: 0 = brak błędów (mogą być ostrzeżenia), 1 = błędy, 2 = nie można odczytać pliku.
"""
from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\[DO UZUPEŁNIENIA[^\]]*\]", re.IGNORECASE)
TEMPLATE_LEFTOVER = re.compile(r"\[(Imię|Pani/Panie|DD\.MM|data\]|osoba|temat\]|treść|…)", re.IGNORECASE)
INTERNAL = re.compile(r"\[\s*(dla nas|wewn\w*|internal)\b|\b(TODO|FIXME)\b", re.IGNORECASE)
SECRET = re.compile(r"(?i)\b(hasło|password|passwd|token|api[_-]?key|secret)\b\s*[:=]\s*\S+|-----BEGIN [A-Z ]*PRIVATE KEY")
DASH = re.compile(r"[—–]")
# „Milczenie oznacza zgodę” w różnych brzmieniach (kropki w datach, np. 05.12, nie kończą zdania).
SILENCE = re.compile(r"(?i)(brak\s+(odpowiedzi|reakcji|uwag)[^\n]{0,80}?(akceptac|zgod|zaakceptow)"
                     r"|milczenie[^\n]{0,40}?(zgod|akceptac)"
                     r"|(jeśli|jeżeli|gdy|o\s+ile)\s+(nie\s+)?(odpowie\w*|otrzymamy|dostaniemy|zgłosz\w*)[^\n]{0,80}?"
                     r"(uzna\w*|przyjm\w*|traktuj\w*)[^\n]{0,40}?(zgod|zgadza|akcept))")
EMOTION = (
    (re.compile(r"(?i)\bjak\s+(już\s+)?(kilka\s+razy\s+|wielokrotnie\s+)?(pisał\w*|wspominał\w*|mówił\w*)"), "odwołanie z wyrzutem"),
    (re.compile(r"(?i)\bpo\s+raz\s+(kolejny|n-ty|enty)\b"), "presja („po raz kolejny”)"),
    (re.compile(r"(?i)\bna\s+wczoraj\b|\basap\b"), "presja czasu bez terminu"),
    (re.compile(r"!{2,}"), "kilka wykrzykników"),
    (re.compile(r"(?i)\b(znowu|znów)\s+nie\b"), "wyrzut („znowu nie”)"),
)
RISK = (
    (re.compile(r"(?i)\bgwarant\w*|\bgwarancj\w*"), "gwarancja"),
    (re.compile(r"(?i)\bbezpłatn\w*|\bgratis\b|\bza\s+darmo\b"), "praca bez wynagrodzenia"),
    (re.compile(r"(?i)\bnasz[aey]?\s+(wina|błąd|winą)\b"), "przyznanie winy"),
    (re.compile(r"(?i)\bkar\w*\s+umown\w*|\bodszkodowan\w*|\bkonsekwencj\w*\s+prawn\w*"), "kary lub skutki prawne"),
)
AI_PHRASES = re.compile(r"(?i)mam nadzieję, że (ta )?wiadomość|warto podkreślić|należy zauważyć|proszę się nie wahać"
                        r"|hope this (e-?mail|message) finds you|do(n't| not) hesitate to")
# Te reguły prostego języka sprawdza już ten skrypt (z regułami redaktora), więc nie są powtarzane.
OWN_PLAIN_RULES = {"NS-1", "NS-3", "NS-4", "EN-W8", "PL-K10"}


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


def plain_language_check(text: str, final: bool, lang: str) -> tuple[list[str], list[str]] | None:
    """Reguły prostego języka jako (błędy, ostrzeżenia); None, gdy modułu nie ma w instalacji."""
    module = load_plain_language()
    if module is None:
        return None
    errors: list[str] = []
    warnings: list[str] = []
    for finding in module.check_text(PLACEHOLDER.sub(" ", text), lang=lang, strict=final):
        if finding.rule_id in OWN_PLAIN_RULES:
            continue
        line = f"prosty język {finding.rule_id} (wiersz {finding.line}): {finding.message} [{finding.excerpt}]"
        (errors if finding.level == module.FAIL else warnings).append(line)
    return errors, warnings
CAPS = re.compile(r"\b[A-ZĄĆĘŁŃÓŚŹŻ]{6,}\b")
DATE = re.compile(r"\b\d{1,2}\.\d{1,2}(\.\d{2,4})?\b|\[DO UZUPEŁNIENIA:[^\]]*dat", re.IGNORECASE)
NUMBERED = re.compile(r"(?m)^\s*\d+(\.\d+)*[.)]\s+\S")


def check(text: str, mode: str = "zwykly", channel: str = "email", final: bool = False,
          silence_agreed: bool = False, lang: str = "auto") -> tuple[list[str], list[str]]:
    """Zwraca (błędy, ostrzeżenia)."""
    errors: list[str] = []
    warnings: list[str] = []
    placeholders = PLACEHOLDER.findall(text)
    if placeholders:
        (errors if final else warnings).append(f"niewypełnione miejsca ({len(placeholders)}): " + "; ".join(placeholders[:5]))
    if TEMPLATE_LEFTOVER.search(text):
        errors.append("w treści zostały elementy szablonu w nawiasach kwadratowych")
    if INTERNAL.search(text):
        errors.append(f"uwaga wewnętrzna w treści dla klienta: {INTERNAL.search(text).group(0)}")
    if SECRET.search(text):
        errors.append("treść zawiera hasło, token lub klucz — zastąp go [UKRYTO]")
    if DASH.search(text):
        errors.append("długi myślnik (— lub –): użyj przecinka, dwukropka lub zwykłego łącznika")
    if SILENCE.search(text) and not silence_agreed:
        errors.append("„brak odpowiedzi oznacza akceptację” bez wskazanej umowy lub procedury")
    for pattern, label in EMOTION:
        if pattern.search(text):
            warnings.append(f"ton: {label}: „{pattern.search(text).group(0)}”")
    caps = [word for word in CAPS.findall(PLACEHOLDER.sub(" ", text)) if word not in ("DUPOKRYTKA", "ZWYKŁY", "WIADOMOŚĆ")]
    if caps:
        warnings.append(f"ton: słowa WIELKIMI LITERAMI: {', '.join(caps[:5])}")
    for pattern, label in RISK:
        if pattern.search(text):
            warnings.append(f"zobowiązanie do sprawdzenia ({label}): „{pattern.search(text).group(0)}”")
    if AI_PHRASES.search(text):
        warnings.append(f"formułka do usunięcia: „{AI_PHRASES.search(text).group(0)}”")
    if mode == "dupokrytka":
        if len(NUMBERED.findall(text)) < 2:
            errors.append("tryb DUPOKRYTKA wymaga ponumerowanych punktów (co najmniej dwóch)")
        if not re.search(r"(?i)potwierdz|korekt", text):
            errors.append("tryb DUPOKRYTKA wymaga prośby o potwierdzenie lub korekty")
        if not DATE.search(text):
            errors.append("tryb DUPOKRYTKA wymaga dat (albo [DO UZUPEŁNIENIA: data])")
    if channel == "wiadomosc":
        sentences = [s for s in re.split(r"[.!?]+\s", text.strip()) if s.strip()]
        if len(sentences) > 5:
            warnings.append(f"wiadomość na komunikator ma {len(sentences)} zdań (zalecane najwyżej 5)")
    plain = plain_language_check(text, final, lang)
    if plain is None:
        warnings.append("brak modułu plain_language w runtime FlowKit: reguły prostego języka nie zostały sprawdzone")
    else:
        errors.extend(plain[0])
        warnings.extend(plain[1])
    return errors, warnings


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("message", type=Path)
    parser.add_argument("--mode", choices=("zwykly", "dupokrytka"), default="zwykly")
    parser.add_argument("--channel", choices=("email", "wiadomosc"), default="email")
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--silence-agreed", action="store_true")
    parser.add_argument("--lang", choices=("auto", "pl", "en"), default="auto")
    args = parser.parse_args()
    try:
        text = args.message.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        print(f"BŁĄD: nie można odczytać pliku: {error}")
        return 2
    errors, warnings = check(text, args.mode, args.channel, args.final, args.silence_agreed, args.lang)
    for error in errors:
        print(f"BŁĄD: {error}")
    for warning in warnings:
        print(f"UWAGA: {warning}")
    print("OK: wiadomość spełnia zasady" if not errors else f"Znaleziono błędów: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
