"""Lokalne, kontrolowane uruchamianie poleceń agentów FlowKit.

Użycie: python flowkit_exec.py --role <rola> -- <polecenie> [argumenty]
Lista poleceń dozwolonych dla roli: python flowkit_exec.py --role <rola> -- help

Polecenie działa bez powłoki, wyłącznie z listy dozwolonej dla roli. Wynik jest skracany,
a sekrety ukrywane. Skrypt nie korzysta z sieci ani z zewnętrznych usług.
Kody wyjścia: kod polecenia, 2 = polecenie odrzucone, 3 = brak wymaganej biblioteki, 124 = przekroczony czas.
"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Wersja runtime: musi być równa wersji w .claude-plugin/plugin.json (sprawdza validate_manifest.py).
VERSION = "1.8.0"
MAX_LINES = 200
HEAD_LINES = 40
MAX_LINE_CHARS = 400
DOCUMENT_PAGE_LINES = 400
MAX_DOCUMENT_BYTES = 50_000_000
MAX_UNZIPPED_BYTES = 200_000_000
DEFAULT_TIMEOUT = 120
TEST_TIMEOUT = 900
DOCUMENT_TIMEOUT = 600
RUNTIME_DIR = Path(__file__).resolve().parent

GIT_READ = ("git status", "git diff", "git log", "git show", "git rev-parse", "git ls-files", "git blame",
            "git check-ignore", "git branch --list", "git branch --show-current")
SEARCH = ("rg", "grep", "find")
STATIC = ("tsc --noEmit", "eslint", "npm ls", "cargo check", "go vet", "pytest --collect-only",
          "python -m pytest --collect-only")
SECURITY_STATIC = ("semgrep scan", "osv-scanner", "gitleaks detect", "gitleaks dir")
TESTS = ("npm test", "jest", "pytest", "python -m pytest", "python -m unittest", "cargo test", "go test",
         "dotnet test", "mvn -q test", "mvn test", "mvn -q -Dtest", "gradle test", "gradlew test")
DIAGNOSTICS = (
    "kubectl get", "kubectl describe", "kubectl logs", "kubectl top", "kubectl version", "kubectl api-resources",
    "kubectl explain", "kubectl events", "kubectl apply --dry-run=client", "helm list", "helm status", "helm history",
    "helm lint", "docker ps", "docker logs", "docker images", "docker version", "docker stats --no-stream",
    "terraform validate", "terraform version", "terraform fmt -check", "hadolint", "yamllint", "actionlint",
    "shellcheck", "tflint", "kubeconform", "docker compose config -q", "docker compose config --quiet",
    "systemctl status", "journalctl", "df", "free", "uptime",
)
# Walidacja statyczna plików konfiguracyjnych: bez dostępu do klastra, chmury i rejestrów obrazów.
VALIDATION = (
    "terraform fmt -check", "terraform validate", "tflint", "hadolint", "docker compose config -q",
    "docker compose config --quiet", "helm lint", "helm template", "yamllint", "actionlint", "zizmor",
    "shellcheck", "kubeconform", "conftest test", "kyverno test", "osv-scanner", "gitleaks detect",
    "gitleaks dir", "check-json",
)
DELIVERY = ("git switch -c", "git add", "git commit -m", "git push -u origin", "gh pr create")
HELP = ("help", "doctor")
DOCUMENTS = ("read-document", "detect-docx-libs", "plain-check")
DOCUMENT_WRITE = ("md-to-docx",)
STATUS_FOOTER = "[kod wyjścia: {code}]"
BUILTINS = {
    "help": "help — lista poleceń dozwolonych dla roli",
    "doctor": "doctor — diagnoza FlowKit: instalacja i wersje, plik zgód (składnia, role, pominięte wpisy, uprawnienia), "
              "dziennik audytu, FLOWKIT_EXTRA_PATHS, narzędzia DOCX; każdy problem z podpowiedzią",
    "read-document": "read-document <plik> [--outline] [--lines OD-DO] — odczyt .docx/.dotx/.xlsx/.pdf/.md/.txt",
    "detect-docx-libs": "detect-docx-libs — biblioteki i narzędzia do pracy z DOCX i diagramami",
    "plain-check": "plain-check <plik> [...] [--lang auto|pl|en] [--strict] [--audience tech|user] [--glossary plik] — "
                   "prosty język i kalki według runtime/procedures/plain-language.md (.md/.txt/.docx/.pdf); --strict: tryb końcowy",
    "check-json": "check-json <plik.json> [...] — sprawdza poprawność składni JSON (PASS/FAIL dla każdego pliku)",
    "md-to-docx": "md-to-docx <wejście.md> <wynik.docx> [--reference-doc szablon] [--template szablon] "
                  "[--engine auto|pandoc|python-docx] [--set POLE=WARTOŚĆ] [--keep-images] [--pdf] — zapis DOCX z Markdown, "
                  "diagramy mermaid/SVG jako PNG, kontrola wyniku i opcjonalny podgląd PDF",
}

ROLE_COMMANDS = {
    # Orkiestrator uruchamia testy i kontrole statyczne w ścieżce szybkiej („make the change, run its check”).
    "orchestrator": HELP + GIT_READ + SEARCH + STATIC + TESTS + DELIVERY + DOCUMENTS + DOCUMENT_WRITE,
    "analyzer": HELP + GIT_READ + SEARCH + STATIC + SECURITY_STATIC,
    # Verifier czyta dokumenty i źródła w niezależnym audycie DOC-AUDIT (bez zapisu DOCX).
    "verifier": HELP + GIT_READ + SEARCH + STATIC + SECURITY_STATIC + TESTS + DOCUMENTS,
    "implementer": HELP + STATIC + TESTS + DOCUMENTS + DOCUMENT_WRITE,
    "diagnostics": HELP + GIT_READ + SEARCH + DIAGNOSTICS + DOCUMENTS,
    "analyst": HELP + GIT_READ + SEARCH + DOCUMENTS + DOCUMENT_WRITE,
    "validator": HELP + GIT_READ + SEARCH + VALIDATION,
}
SKILL_SCRIPTS = {
    "flowkit-client-pt-prd-writer": {"generate_diagram.py", "export_diagram.py", "validate_diagram.py", "insert_diagrams.py",
                             "check_status_labels.py", "check_client_version.py"},
    "flowkit-sql-data-assistant": {"check_sql.py"},
    "flowkit-client-message-editor": {"check_message.py"},
    "flowkit-client-solution-docs-writer": {"check_user_docs.py", "check_coverage.py", "make_client_version.py"},
}
# Skrypty kontrolne, które tylko czytają pliki: Verifier uruchamia je w audycie, ale nie generuje ani nie wstawia diagramów.
READONLY_SKILL_SCRIPTS = {
    "flowkit-client-pt-prd-writer": {"validate_diagram.py", "check_status_labels.py", "check_client_version.py"},
    "flowkit-sql-data-assistant": {"check_sql.py"},
    "flowkit-client-message-editor": {"check_message.py"},
    "flowkit-client-solution-docs-writer": {"check_user_docs.py", "check_coverage.py"},
}
ROLE_SKILL_SCRIPTS = {"orchestrator": SKILL_SCRIPTS, "analyst": SKILL_SCRIPTS, "verifier": READONLY_SKILL_SCRIPTS}
SKILL_SCRIPT_ROLES = set(ROLE_SKILL_SCRIPTS)

FORBIDDEN_FLAGS = {"--fix", "--autofix", "--write", "--output-file", "--report-path", "--apply", "--update",
                   "-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprintf",
                   "-fls", "--pre", "--token", "--as", "--as-group", "--password", "--dependency-update",
                   "--kube-context", "--kubeconfig"}
SENSITIVE_PATH = re.compile(
    r"(^|[\\/])(\.env(\.(?!example$)[^\\/]+)?|id_rsa|id_ed25519|credentials(\.[^\\/]+)?|secrets?\.[^\\/]+"
    r"|[^\\/]+\.(pem|key|pfx|p12))$", re.IGNORECASE)
SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(-----END [A-Z ]*PRIVATE KEY-----|$)", re.S), "[UKRYTO]"),
    (re.compile(r"(?i)\b(authorization\s*:\s*)(bearer|basic)\s+\S+"), r"\1[UKRYTO]"),
    (re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{12,}"), "Bearer [UKRYTO]"),
    (re.compile(r"(?i)\b([\w-]*(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key)[\w-]*)"
                r"(\"?\s*[:=]\s*\"?)[^\s\"',;]+"), r"\1\2[UKRYTO]"),
    (re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"), "[UKRYTO]"),
    (re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[abprs]-[A-Za-z0-9-]{10,})\b"), "[UKRYTO]"),
    (re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://[^\s:/@]+:)[^\s/@]+@"), r"\1[UKRYTO]@"),
)
PYTHON_NAMES = {"python", "python3", "py"}
SHELLS_AND_RUNNERS = {"sh", "bash", "zsh", "cmd", "powershell", "pwsh", "env", "xargs", "sudo", "eval", "exec"}


def command_name(token: str) -> str:
    name = token.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return re.sub(r"\.(exe|cmd|bat)$", "", name)


def normalized(argv: list[str]) -> list[str]:
    return [command_name(argv[0]), *argv[1:]] if argv else []


def matches(argv: list[str], prefix: str) -> bool:
    words = prefix.split()
    return argv[:len(words)] == words or (words[-1] == "-Dtest" and argv[:2] == ["mvn", "-q"]
                                          and len(argv) > 2 and argv[2].startswith("-Dtest="))


def is_skill_script(argv: list[str], scripts: dict[str, set[str]] = SKILL_SCRIPTS) -> bool:
    if len(argv) < 2 or argv[0] not in PYTHON_NAMES:
        return False
    parts = argv[1].replace("\\", "/").split("/")
    return (len(parts) >= 3 and ".." not in parts and parts[-2] == "scripts"
            and parts[-1] in scripts.get(parts[-3], set()))


def delivery_problem(argv: list[str]) -> str | None:
    if argv[:2] == ["git", "add"]:
        paths = argv[2:]
        if not paths or any(p.startswith("-") or p in (".", "*", ":/") for p in paths):
            return "git add wymaga jawnej listy plików"
    if argv[:2] == ["git", "commit"] and (len(argv) != 4 or argv[2] != "-m"):
        return "git commit dopuszcza wyłącznie postać: git commit -m <opis>"
    if argv[:2] == ["git", "push"]:
        if len(argv) != 5 or argv[4] in ("main", "master") or argv[4].startswith(("+", "-")) or ":" in argv[4]:
            return "dozwolony jest push nowej gałęzi, bez main, master i wymuszania"
    return None


# --- Granica katalogu roboczego ------------------------------------------------
# Agent widzi tylko katalog, w którym go uruchomiono, i katalogi dopisane przez użytkownika w zmiennej
# FLOWKIT_EXTRA_PATHS (lista rozdzielona ';' w Windows lub ':' w Linux/macOS). Hook odrzuca przypisania
# zmiennych w poleceniu agenta, więc listę zmienia tylko użytkownik.
EXTRA_PATHS_ENV = "FLOWKIT_EXTRA_PATHS"


def allowed_roots() -> list[Path]:
    roots = [Path.cwd().resolve()]
    for item in os.environ.get(EXTRA_PATHS_ENV, "").split(os.pathsep):
        if item.strip():
            roots.append(Path(item.strip()).expanduser().resolve())
    return roots


def within_allowed(path: Path, roots: list[Path] | None = None) -> bool:
    """Ścieżka po rozwinięciu `..`, `~` i dowiązań symbolicznych musi leżeć w dozwolonym katalogu."""
    try:
        target = path.expanduser().resolve()
    except (OSError, RuntimeError, ValueError):
        return False
    return any(target == root or root in target.parents for root in roots or allowed_roots())


def path_candidates(argv: list[str], skip: set[int]) -> list[str]:
    """Argumenty, które wyglądają na ścieżki: separator, `.`/`~` na początku, litera dysku albo istniejący plik."""
    found = []
    for index, token in enumerate(argv[1:], 1):
        if index in skip or "://" in token:
            continue
        value = token.split("=", 1)[1] if token.startswith("-") and "=" in token else token
        if value.startswith("-") or not value:
            continue
        drive = re.match(r"^[A-Za-z]:[\\/]", value)
        if ":" in value and not drive:
            continue  # rewizje git (HEAD:plik), typy kubectl, pola klucz:wartość
        if drive or "/" in value or "\\" in value or value.startswith((".", "~")) or Path(value).exists():
            found.append(value)
    return found


def path_problem(argv: list[str], skip: set[int]) -> str | None:
    roots = allowed_roots()
    for value in path_candidates(argv, skip):
        if not within_allowed(Path(value), roots):
            return (f"ścieżka poza katalogiem roboczym: {value}. Skopiuj plik do projektu albo poproś użytkownika "
                    f"o dopisanie katalogu do zmiennej {EXTRA_PATHS_ENV}")
    return None


# --- Zgody użytkownika ------------------------------------------------------------
# Polecenia spoza listy roli, które użytkownik świadomie pozwolił wykonywać. Plik leży poza projektem
# (domyślnie ~/.flowkit/allow.json, inna ścieżka: zmienna FLOWKIT_ALLOW_FILE), a hook blokuje jego edycję
# przez agentów. Zgoda nie wyłącza twardych zabezpieczeń: powłok, wrażliwych plików, granicy katalogu
# roboczego, odczytu obiektów Secret ani ochrony gałęzi głównej.
ALLOW_FILE_ENV = "FLOWKIT_ALLOW_FILE"
INLINE_CODE = {("python", "-c"), ("python3", "-c"), ("py", "-c"), ("node", "-e"), ("node", "--eval"), ("node", "-p"),
               ("perl", "-e"), ("ruby", "-e"), ("php", "-r"), ("deno", "eval"), ("bun", "-e")}
INTERPRETERS = {"python", "python3", "py", "node", "perl", "ruby", "php", "deno", "bun", "java", "npx"}


# --- Tryb tylko do odczytu -----------------------------------------------------------
# FLOWKIT_READONLY=1 ustawia użytkownik przed uruchomieniem sesji. Agent wtedy nie zmienia plików (hook blokuje
# Edit/Write), nie zapisuje DOCX i nie wykonuje commit/push/PR. Hook odrzuca przypisania zmiennych w poleceniach
# agenta, więc trybu nie wyłączy ani agent, ani prefiks AUTO:.
READONLY_ENV = "FLOWKIT_READONLY"
WRITE_COMMANDS = DELIVERY + DOCUMENT_WRITE


def readonly() -> bool:
    return os.environ.get(READONLY_ENV, "").strip().lower() in ("1", "true", "yes", "on")


def allow_file() -> Path:
    configured = os.environ.get(ALLOW_FILE_ENV, "").strip()
    return Path(configured).expanduser() if configured else Path.home() / ".flowkit" / "allow.json"


def allow_entry_problem(entry: str) -> str | None:
    words = normalized(entry.split())
    if not words:
        return "pusty wpis"
    if words[0] in SHELLS_AND_RUNNERS:
        return f"{words[0]} uruchamia dowolne polecenia"
    if words[0] in INTERPRETERS and len(words) < 2:
        return f"sam {words[0]} pozwoliłby uruchomić dowolny kod; podaj skrypt lub moduł"
    if tuple(words[:2]) in INLINE_CODE:
        return "kod podany w wierszu poleceń jest niedozwolony"
    if any(ch in entry for ch in ";&|<>`$\n"):
        return "znaki powłoki są niedozwolone"
    return None


def user_allowed(role: str) -> tuple[list[str], list[str]]:
    """Zwraca (dozwolone prefiksy dla roli, odrzucone wpisy z powodem). Błędny plik = brak zgód."""
    import json

    path = allow_file()
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return [], []
    except (OSError, ValueError) as error:
        return [], [f"{path}: {error}"]
    commands = data.get("commands") if isinstance(data, dict) else None
    if not isinstance(commands, dict):
        return [], [f"{path}: brak obiektu \"commands\""]
    allowed, ignored = [], []
    for key in ("*", role):
        entries = commands.get(key) or []
        for entry in entries if isinstance(entries, list) else []:
            problem = allow_entry_problem(str(entry))
            if problem:
                ignored.append(f"{entry}: {problem}")
            else:
                allowed.append(" ".join(normalized(str(entry).split())))
    return allowed, ignored


SUBCOMMAND = re.compile(r"^[a-z][a-z0-9-]*$")


def allow_hint(role: str, argv: list[str]) -> str:
    if argv[0] in BUILTINS:
        return (" To polecenie wbudowane FlowKit: nie dopisuj go do pliku zgód. Jeśli ta rola powinna je mieć, "
                "sprawdź instalację poleceniem doctor (możliwy stary runtime).")
    # Druga część wpisu tylko wtedy, gdy to podpolecenie (np. "dotnet build"), nigdy ścieżka pliku.
    prefix = " ".join(argv[:2]) if len(argv) > 1 and SUBCOMMAND.match(argv[1]) else argv[0]
    if allow_entry_problem(prefix):
        return ""
    return (f" Jeśli chcesz, aby agent wykonywał to polecenie, dopisz \"{prefix}\" do listy \"{role}\" "
            f"w pliku zgód {allow_file()}")


DOCX_TOOLS = ("pandoc", "pypandoc", "mmdc", "rsvg-convert")


def rejection_hint(role: str, argv: list[str]) -> str:
    """Podpowiedź dopasowana do odrzuconego polecenia."""
    joined = " ".join(argv).lower()
    if "md-to-docx" in ROLE_COMMANDS[role] and (argv[0] in DOCX_TOOLS or "docx" in joined or "pandoc" in joined):
        return " (zapis DOCX: md-to-docx <wejście.md> <wynik.docx> [--template szablon])"
    others = [r for r, prefixes in ROLE_COMMANDS.items() if r != role and any(matches(argv, p) for p in prefixes)]
    if others:
        return f" (polecenie należy do ról: {', '.join(others)} — przekaż krok właściwemu agentowi)"
    return ""


def check(role: str, raw_argv: list[str]) -> str | None:
    """Zwraca powód odrzucenia albo None, gdy polecenie jest dozwolone."""
    if role not in ROLE_COMMANDS:
        return f"nieznana rola: {role}"
    argv = normalized(raw_argv)
    if not argv:
        return "brak polecenia"
    if argv[0] in SHELLS_AND_RUNNERS:
        return f"uruchamianie przez {argv[0]} jest zabronione"
    if readonly() and any(matches(argv, prefix) for prefix in WRITE_COMMANDS):
        return (f"tryb tylko do odczytu ({READONLY_ENV}): {' '.join(argv[:2])} zmienia pliki lub repozytorium. "
                f"Pokaż zmianę jako diff do akceptacji")
    for token in argv[1:]:
        if token in FORBIDDEN_FLAGS or token.split("=", 1)[0] in FORBIDDEN_FLAGS:
            return f"zabroniona opcja: {token}"
        if SENSITIVE_PATH.search(token):
            return f"dostęp do pliku wrażliwego jest zabroniony: {token}"
    skill_script = role in ROLE_SKILL_SCRIPTS and is_skill_script(argv, ROLE_SKILL_SCRIPTS[role])
    problem = path_problem(argv, {1} if skill_script else set())
    if problem:
        return problem
    if skill_script:
        return None
    user_rule = None
    if not any(matches(argv, prefix) for prefix in ROLE_COMMANDS[role]):
        user_rule = next((p for p in user_allowed(role)[0] if matches(argv, p)), None)
        if user_rule is None:
            return (f"polecenie niedozwolone dla roli {role}: {' '.join(argv[:3])}{rejection_hint(role, argv)}."
                    f"{allow_hint(role, argv)}")
    if argv[0] == "kubectl":
        if any("secret" in token.lower() for token in argv[1:]):
            return "odczyt obiektów Secret jest zabroniony"
        if user_rule is None and len(argv) > 1 and argv[1] == "apply" and sum(t.startswith("--dry-run") for t in argv) != 1:
            return "kubectl apply wymaga dokładnie jednej opcji --dry-run=client"
    if argv[0] == "git" and any(t.startswith(("--output", "--ext-diff", "--exec")) for t in argv):
        return "opcja git zapisująca plik lub uruchamiająca program jest zabroniona"
    if argv[0] in ("git", "gh"):
        return delivery_problem(argv)
    if argv[0] == "semgrep":
        joined = " ".join(argv[1:]).lower()
        if any(bad in joined for bad in ("--config auto", "--config=auto", "http://", "https://", "r/", "p/")):
            return "semgrep dopuszcza wyłącznie lokalne reguły (bez --config auto i zdalnych URL)"
        if "--metrics=on" in joined or "--metrics on" in joined:
            return "semgrep wymaga wyłączonej telemetrii (bez --metrics=on)"
    if argv[0] == "md-to-docx":
        return md_to_docx_problem(argv[1:])
    return None


def md_to_docx_problem(args: list[str]) -> str | None:
    """Wynik musi być nowym plikiem .docx; źródła i szablony pozostają nietknięte."""
    positional = [a for i, a in enumerate(args) if not a.startswith("-")
                  and (i == 0 or args[i - 1] not in ("--reference-doc", "--template", "--engine", "--set"))]
    if len(positional) != 2:
        return "md-to-docx wymaga: <wejście.md> <wynik.docx>"
    if not positional[1].lower().endswith(".docx"):
        return "md-to-docx zapisuje wyłącznie plik .docx"
    if Path(positional[1]).resolve() == Path(positional[0]).resolve():
        return "md-to-docx nie może nadpisać pliku źródłowego"
    if any(part.lower() == ".git" for part in Path(positional[1]).resolve().parts):
        return "md-to-docx nie zapisuje w katalogu .git"
    return None


def with_limits(argv: list[str]) -> list[str]:
    """Ogranicza ilość logów, zanim trafią do kontekstu modelu."""
    name = normalized(argv)
    if name[:2] == ["kubectl", "logs"] and not any(t.startswith("--tail") for t in argv):
        return [*argv, "--tail=200"]
    if name[:2] == ["docker", "logs"] and not any(t.startswith("--tail") for t in argv):
        return [*argv, "--tail", "200"]
    if name[0] == "journalctl" and "-n" not in argv:
        return [*argv, "-n", "200", "--no-pager"]
    return argv


def redact(text: str) -> str:
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def limit_output(text: str, max_lines: int = MAX_LINES) -> str:
    lines = [line if len(line) <= MAX_LINE_CHARS else line[:MAX_LINE_CHARS] + " […]" for line in text.splitlines()]
    if len(lines) > max_lines:
        tail = max_lines - HEAD_LINES
        lines = lines[:HEAD_LINES] + [f"[… pominięto {len(lines) - max_lines} wierszy …]"] + lines[-tail:]
    return "\n".join(lines)


# --- Odczyt dokumentów ---------------------------------------------------------

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
TEXT_SUFFIXES = {".txt", ".md", ".vtt", ".csv", ".tsv", ".log", ".json", ".yaml", ".yml", ".xml"}


def safe_xml(archive: zipfile.ZipFile, name: str) -> ET.Element:
    data = archive.read(name)
    if b"<!DOCTYPE" in data[:4096].upper():
        raise ValueError("dokument zawiera niedozwoloną deklarację DOCTYPE")
    return ET.fromstring(data)


def open_archive(path: Path) -> zipfile.ZipFile:
    archive = zipfile.ZipFile(path)
    if sum(item.file_size for item in archive.infolist()) > MAX_UNZIPPED_BYTES:
        raise ValueError("dokument po rozpakowaniu jest zbyt duży")
    return archive


def word_lines(path: Path) -> list[str]:
    def text_of(element: ET.Element) -> str:
        return "".join(node.text or "" for node in element.iter(f"{W}t"))

    with open_archive(path) as archive:
        body = safe_xml(archive, "word/document.xml").find(f"{W}body")
    lines: list[str] = []
    for block in list(body) if body is not None else []:
        if block.tag == f"{W}p":
            text = text_of(block)
            style = block.find(f"{W}pPr/{W}pStyle")
            value = (style.get(f"{W}val", "") if style is not None else "").casefold()
            level = re.search(r"(?:heading|nag\w*)\D*(\d)", value)
            if text.strip():
                lines.append(f"{'#' * int(level.group(1))} {text}" if level else text)
        elif block.tag == f"{W}tbl":
            for row in block.iter(f"{W}tr"):
                lines.append("| " + " | ".join(text_of(cell).strip() for cell in row.findall(f"{W}tc")) + " |")
    return lines


def excel_lines(path: Path) -> list[str]:
    relation = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    with open_archive(path) as archive:
        names = set(archive.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            shared = ["".join(t.text or "" for t in item.iter(f"{S}t"))
                      for item in safe_xml(archive, "xl/sharedStrings.xml").findall(f"{S}si")]
        targets = {r.get("Id"): r.get("Target", "") for r in safe_xml(archive, "xl/_rels/workbook.xml.rels")}
        lines: list[str] = []
        for sheet in safe_xml(archive, "xl/workbook.xml").iter(f"{S}sheet"):
            target = targets.get(sheet.get(relation), "").lstrip("/")
            target = target if target.startswith("xl/") else f"xl/{target}"
            lines.append(f"# Arkusz: {sheet.get('name')}")
            for row in safe_xml(archive, target).iter(f"{S}row"):
                values = []
                for cell in row.findall(f"{S}c"):
                    value = cell.findtext(f"{S}v") or "".join(t.text or "" for t in cell.iter(f"{S}t"))
                    values.append(shared[int(value)] if cell.get("t") == "s" and value else value)
                lines.append("\t".join(values))
    return lines


def pdf_lines(path: Path) -> list[str]:
    if importlib.util.find_spec("pypdf") is None:
        raise ImportError("odczyt PDF wymaga lokalnego pakietu pypdf")
    from pypdf import PdfReader
    lines: list[str] = []
    for number, page in enumerate(PdfReader(str(path)).pages, 1):
        lines.append(f"# Strona {number}")
        lines.extend(line for line in (page.extract_text() or "").splitlines() if line.strip())
    return lines


def document_lines(path: Path) -> list[str]:
    if SENSITIVE_PATH.search(str(path)):
        raise ValueError("dostęp do pliku wrażliwego jest zabroniony")
    if path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("dokument jest zbyt duży")
    suffix = path.suffix.lower()
    if suffix in (".docx", ".dotx"):
        return word_lines(path)
    if suffix in (".xlsx", ".xlsm"):
        return excel_lines(path)
    if suffix == ".pdf":
        return pdf_lines(path)
    if suffix in TEXT_SUFFIXES or is_text_file(path):
        return read_text_lines(path)
    raise ValueError(f"nieobsługiwany format: {suffix or 'brak rozszerzenia'} (plik binarny; obsługiwane: "
                     ".docx, .dotx, .xlsx, .xlsm, .pdf i pliki tekstowe, w tym kod źródłowy)")


def is_text_file(path: Path) -> bool:
    """Kod źródłowy i inne pliki tekstowe rozpoznawane po treści: brak bajtów zerowych w początku pliku."""
    with path.open("rb") as handle:
        head = handle.read(8192)
    if head.startswith((b"\xff\xfe", b"\xfe\xff")):
        return True  # UTF-16 z BOM (np. pliki z Visual Studio)
    return b"\0" not in head


def read_text_lines(path: Path) -> list[str]:
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace").splitlines()
    try:
        return data.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return data.decode("cp1250", errors="replace").splitlines()  # starsze polskie pliki Windows


def read_document(args: list[str]) -> int:
    """read-document <plik> [--outline] [--lines OD-DO]: duże pliki czytane są partiami."""
    if not args:
        print("Użycie: read-document <plik> [--outline] [--lines OD-DO]")
        return 2
    try:
        lines = document_lines(Path(args[0]))
    except ImportError as error:
        print(f"BRAK BIBLIOTEKI: {error}")
        return 3
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        print(f"BŁĄD: {error}")
        return 2
    total = len(lines)
    if "--outline" in args:
        for number, line in enumerate(lines, 1):
            if line.startswith("#"):
                print(f"{number}: {redact(line)[:MAX_LINE_CHARS]}")
        print(f"[Wierszy: {total}]")
        return 0
    start, end = 1, DOCUMENT_PAGE_LINES
    if "--lines" in args:
        match = re.fullmatch(r"(\d+)-(\d+)", args[args.index("--lines") + 1] if args.index("--lines") + 1 < len(args) else "")
        if not match:
            print("BŁĄD: użyj --lines OD-DO")
            return 2
        start, end = int(match.group(1)), min(int(match.group(2)), int(match.group(1)) + DOCUMENT_PAGE_LINES - 1)
    for number, line in enumerate(lines[start - 1:end], start):
        print(f"{number}: {redact(line)[:MAX_LINE_CHARS]}")
    if end < total:
        print(f"[Pokazano {start}-{end} z {total}. Dalszą część odczytaj przez --lines {end + 1}-{end + DOCUMENT_PAGE_LINES}]")
    return 0


def detect_docx_libs() -> int:
    for label, module in (("python-docx", "docx"), ("mammoth", "mammoth"), ("docx2txt", "docx2txt"),
                          ("pypandoc", "pypandoc"), ("pypdf", "pypdf"), ("playwright", "playwright"),
                          ("cairosvg", "cairosvg")):
        print(f"{label}: {'AVAILABLE' if importlib.util.find_spec(module) else 'MISSING'}")
    for label, tool in (("pandoc", "pandoc"), ("mermaid-cli (mmdc)", "mmdc"), ("npx", "npx"), ("rsvg-convert", "rsvg-convert")):
        print(f"{label}: {'AVAILABLE' if shutil.which(tool) else 'MISSING'}")
    print("Zapis DOCX: md-to-docx (Pandoc, a bez niego python-docx). Odczyt: read-document.")
    return 0


def check_json(paths: list[str]) -> int:
    """check-json: składnia plików JSON, bez wykonywania ich treści."""
    import json

    if not paths:
        print("Użycie: check-json <plik.json> [...]")
        return 2
    failed = 0
    for name in paths:
        path = Path(name)
        try:
            if path.stat().st_size > MAX_DOCUMENT_BYTES:
                raise ValueError("plik jest zbyt duży")
            json.loads(path.read_text(encoding="utf-8-sig"))
            print(f"PASS {name}")
        except (OSError, ValueError, UnicodeDecodeError) as error:
            failed += 1
            print(f"FAIL {name}: {redact(str(error))[:MAX_LINE_CHARS]}")
    print(STATUS_FOOTER.format(code=1 if failed else 0))
    return 1 if failed else 0


def plain_check(args: list[str]) -> int:
    """plain-check: kontrola prostego języka (runtime/plain_language.py), bez zapisu plików."""
    import plain_language

    try:
        return plain_language.main(args)
    except SystemExit as error:  # argparse: błędne opcje lub --help
        return error.code if isinstance(error.code, int) else 2


def show_help(role: str) -> int:
    print(f"Rola: {role}. Uruchamiaj: flowkit_exec.py --role {role} -- <polecenie> [argumenty]")
    print("Polecenia wbudowane:")
    for prefix in ROLE_COMMANDS[role]:
        if prefix in BUILTINS:
            print(f"  {BUILTINS[prefix]}")
    print("Dozwolone polecenia (prefiksy):")
    print("  " + " · ".join(p for p in ROLE_COMMANDS[role] if p not in BUILTINS))
    if role in ROLE_SKILL_SCRIPTS:
        for skill, scripts in sorted(ROLE_SKILL_SCRIPTS[role].items()):
            print(f"  python <katalog skilla>/{skill}/scripts/<{'|'.join(sorted(scripts))}>")
    allowed, ignored = user_allowed(role)
    print(f"Zgody użytkownika ({allow_file()}):")
    print("  " + (" · ".join(allowed) if allowed else "brak") + " — te polecenia wykonuj sam, nie odsyłaj ich do czatu")
    for item in ignored:
        print(f"  pominięto: {item}")
    print("Bez powłoki, potoków, przekierowań i łączenia poleceń. Odrzucone polecenie zgłoś użytkownikowi.")
    return 0


def run_doctor(role: str) -> int:
    """Diagnoza środowiska FlowKit (runtime/flowkit_doctor.py) z zgodami liczonymi dla roli agenta."""
    import flowkit_doctor

    return flowkit_doctor.main(["--role", role])


def md_to_docx(args: list[str]) -> int:
    try:
        result = subprocess.run([sys.executable, str(RUNTIME_DIR / "md_to_docx.py"), *args], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=DOCUMENT_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        print(f"PRZEKROCZONO CZAS: {DOCUMENT_TIMEOUT} s")
        return 124
    print(limit_output(redact(result.stdout.decode("utf-8", "replace"))))
    return result.returncode


GLOB_CHARS = re.compile(r"[*?\[]")


def expand_globs(argv: list[str]) -> list[str]:
    """Rozwija wzorce (np. diagrams/D-*.yaml) jak powłoka, ale tylko w katalogu roboczym i FLOWKIT_EXTRA_PATHS.

    Executor działa bez powłoki, więc bez tego skrypty dostałyby wzorzec dosłownie. Wzorzec bez dopasowań
    zostaje bez zmian (jak w bash), a dopasowania spoza dozwolonych katalogów są pomijane.
    """
    import glob

    roots = allowed_roots()
    expanded = [argv[0]]
    for token in argv[1:]:
        if token.startswith("-") or "://" in token or not GLOB_CHARS.search(token):
            expanded.append(token)
            continue
        matches = sorted(m for m in glob.glob(token) if within_allowed(Path(m), roots))
        expanded.extend(matches or [token])
    return expanded


def run(argv: list[str], role: str = "orchestrator") -> int:
    argv = expand_globs(argv)
    name = normalized(argv)
    if name[0] == "help":
        return show_help(role)
    if name[0] == "doctor":
        return run_doctor(role)
    if name[0] == "md-to-docx":
        return md_to_docx(argv[1:])
    if name[0] == "read-document":
        return read_document(argv[1:])
    if name[0] == "detect-docx-libs":
        return detect_docx_libs()
    if name[0] == "check-json":
        return check_json(argv[1:])
    if name[0] == "plain-check":
        return plain_check(argv[1:])
    argv = with_limits(argv)
    executable = sys.executable if name[0] in PYTHON_NAMES else shutil.which(argv[0])
    if executable is None:
        print(f"BRAK NARZĘDZIA: {argv[0]} (status: NOT_RUN)")
        return 127
    long_running = TESTS + tuple(user_allowed(role)[0])  # testy i zgody użytkownika (np. budowanie)
    timeout = TEST_TIMEOUT if any(matches(name, prefix) for prefix in long_running) else DEFAULT_TIMEOUT
    try:
        # Wynik jest czytany jako UTF-8, więc skrypty Pythona też piszą w UTF-8 (polskie znaki w Windows).
        result = subprocess.run([executable, *argv[1:]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, timeout=timeout, check=False,
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    except subprocess.TimeoutExpired:
        print(f"PRZEKROCZONO CZAS: {timeout} s (status: UNKNOWN)")
        return 124
    print(limit_output(redact(result.stdout.decode("utf-8", "replace"))))
    print(STATUS_FOOTER.format(code=result.returncode))
    return result.returncode


# --- Dziennik audytu -----------------------------------------------------------------
# Każde polecenie agenta (wykonane i odrzucone) trafia jako wiersz JSON do pliku poza projektem
# (domyślnie ~/.flowkit/audit.log, inna ścieżka: FLOWKIT_AUDIT_FILE, wyłączenie: FLOWKIT_AUDIT_FILE=off).
# Argumenty są zapisywane po ukryciu sekretów, a skrót SHA-256 pozwala porównać wywołania bez ich treści.
# Hook blokuje agentom edycję dziennika, a błąd zapisu nie przerywa pracy.
AUDIT_FILE_ENV = "FLOWKIT_AUDIT_FILE"
AUDIT_MAX_CHARS = 1000


def audit_file() -> Path | None:
    configured = os.environ.get(AUDIT_FILE_ENV, "").strip()
    if configured.lower() == "off":
        return None
    return Path(configured).expanduser() if configured else Path.home() / ".flowkit" / "audit.log"


def audit(role: str, argv: list[str], decision: str, *, reason: str | None = None, exit_code: int | None = None,
          duration: float | None = None) -> None:
    import datetime
    import hashlib

    path = audit_file()
    if path is None:
        return
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "role": role,
        "cwd": str(Path.cwd()),
        "command": redact(" ".join(argv))[:AUDIT_MAX_CHARS],
        "args_sha256": hashlib.sha256("\0".join(argv).encode("utf-8", "replace")).hexdigest(),
        "decision": decision,
    }
    if reason is not None:
        entry["reason"] = redact(reason)[:AUDIT_MAX_CHARS]
    if exit_code is not None:
        entry["exit_code"] = exit_code
    if duration is not None:
        entry["duration_s"] = round(duration, 2)
    write_audit(entry, path)


def write_audit(entry: dict, path: Path | None = None) -> None:
    """Dopisuje wiersz JSON do dziennika audytu. Błąd zapisu tylko ostrzega na stderr."""
    import json

    path = path or audit_file()
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as error:
        print(f"FlowKit: nie zapisano dziennika audytu ({path}): {error}", file=sys.stderr)


def main(args: list[str]) -> int:
    import time

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if len(args) == 3 and args[0] == "--role" and args[2] == "--" and args[1] in ROLE_COMMANDS:
        return show_help(args[1])
    if len(args) < 4 or args[0] != "--role" or args[2] != "--":
        print("Użycie: flowkit_exec.py --role <rola> -- <polecenie> [argumenty]. "
              "Lista poleceń: flowkit_exec.py --role <rola> -- help")
        return 2
    role, argv = args[1], args[3:]
    if normalized(argv)[:1] in (["--help"], ["-h"]):
        argv = ["help"]
    problem = check(role, argv)
    if problem:
        audit(role, argv, "rejected", reason=problem, exit_code=2)
        print(f"ODRZUCONO: {problem}. Lista dozwolonych poleceń: flowkit_exec.py --role {role} -- help")
        return 2
    started = time.monotonic()
    code = run(argv, role)
    audit(role, argv, "allowed", exit_code=code, duration=time.monotonic() - started)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
