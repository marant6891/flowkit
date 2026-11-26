"""Diagnoza środowiska FlowKit i przygotowanie pliku zgód.

Użycie:
  python flowkit_doctor.py                 # przegląd instalacji, bezpieczeństwa, konfiguracji i narzędzi
  python flowkit_doctor.py --role analyst  # zgody liczone dla wskazanej roli (domyślnie wszystkie)
  python flowkit_doctor.py --json          # wynik w JSON
  python flowkit_doctor.py init            # tworzy ~/.flowkit i pusty allow.json (uruchamia tylko użytkownik)

Przegląd tylko czyta pliki. `init` tworzy plik zgód wyłącznie, gdy go nie ma, i nigdy nie dopisuje zgód:
polecenia dopisuje sam użytkownik. Kody wyjścia: 0 = bez błędów (mogą być uwagi), 1 = są błędy, 2 = złe użycie.
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flowkit_exec as fx  # noqa: E402

RUNTIME_DIR = Path(__file__).resolve().parent
MIN_PYTHON = (3, 10)
SCHEMA_URL = "https://raw.githubusercontent.com/marant6891/flowkit/main/docs/allow.schema.json"
RUNTIME_FILES = ("flowkit_exec.py", "plain_language.py", "guard_bash.py", "log_tool_event.py", "md_to_docx.py",
                 "checkpoint_report.py", "flowkit_doctor.py", "procedures")
AGENT_MARKER = re.compile(r"<!-- FlowKit (\d+\.\d+\.\d+)")
ROLE_KEYS = ("*", *fx.ROLE_COMMANDS)

OK, INFO, WARN, ERROR = "OK", "INFO", "UWAGA", "BŁĄD"


@dataclass
class Check:
    section: str
    status: str
    name: str
    detail: str
    fix: str = ""


def doctor_command() -> str:
    return f'python "{RUNTIME_DIR / "flowkit_doctor.py"}"'


# --- Plik zgód -------------------------------------------------------------------------

def inspect_allow_file(path: Path) -> list[Check]:
    """Ocena pliku zgód: istnienie, składnia, nazwy ról, wpisy aktywne i pominięte, uprawnienia."""
    section = "Bezpieczeństwo"
    if not path.exists():
        return [Check(section, INFO, "Plik zgód", f"{path}: brak (opcjonalny). Bez niego agenci wykonują tylko "
                      "polecenia ze swojej roli.", f"utwórz pusty plik: {doctor_command()} init")]
    if not path.is_file():
        return [Check(section, ERROR, "Plik zgód", f"{path} nie jest plikiem", "usuń lub zmień nazwę tej ścieżki")]
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        return [Check(section, ERROR, "Plik zgód", f"{path}: niepoprawny JSON w linii {error.lineno}, kolumna "
                      f"{error.colno}: {error.msg}. Do czasu poprawy żadna zgoda nie działa.",
                      "popraw składnię (wzór: docs/allow.example.json w repozytorium FlowKit)")]
    except (OSError, UnicodeDecodeError) as error:
        return [Check(section, ERROR, "Plik zgód", f"{path}: nie można odczytać ({error})", "sprawdź uprawnienia")]
    commands = data.get("commands") if isinstance(data, dict) else None
    if not isinstance(commands, dict):
        return [Check(section, ERROR, "Plik zgód", f"{path}: brak obiektu \"commands\"; żadna zgoda nie działa.",
                      'użyj układu {"commands": {"*": [], "orchestrator": []}}')]

    checks: list[Check] = []
    active: dict[str, list[str]] = {}
    for key, entries in commands.items():
        if key not in ROLE_KEYS:
            close = difflib.get_close_matches(key, ROLE_KEYS, n=1)
            hint = f" — chodziło o \"{close[0]}\"?" if close else ""
            checks.append(Check(section, WARN, "Plik zgód", f"nieznana rola \"{key}\": wpisy są ignorowane{hint}",
                                f"dozwolone klucze: {', '.join(ROLE_KEYS)}"))
            continue
        if not isinstance(entries, list):
            checks.append(Check(section, ERROR, "Plik zgód", f"\"{key}\" musi być listą poleceń",
                                f'np. "{key}": ["make lint"]'))
            continue
        for entry in entries:
            problem = fx.allow_entry_problem(str(entry))
            if problem:
                checks.append(Check(section, WARN, "Plik zgód", f"pominięto wpis \"{entry}\" ({key}): {problem}",
                                    "podaj konkretne polecenie, np. \"dotnet build\" albo \"python scripts/build.py\""))
            else:
                active.setdefault(key, []).append(str(entry))
    summary = "; ".join(f"{key}: {', '.join(values)}" for key, values in active.items()) or "brak aktywnych zgód"
    checks.insert(0, Check(section, OK, "Plik zgód", f"{path} — {summary}"))
    checks.extend(allow_file_permissions(path))
    return checks


def allow_file_permissions(path: Path) -> list[Check]:
    """Na Linux/macOS plik zgód może zmieniać tylko jego właściciel."""
    if os.name == "nt":
        return []
    stat = path.stat()
    checks = []
    if stat.st_mode & 0o022:
        checks.append(Check("Bezpieczeństwo", ERROR, "Uprawnienia pliku zgód",
                            f"{path}: inni użytkownicy mogą go zmienić (tryb {oct(stat.st_mode & 0o777)})",
                            f'chmod 600 "{path}"'))
    if hasattr(os, "getuid") and stat.st_uid != os.getuid():
        checks.append(Check("Bezpieczeństwo", WARN, "Uprawnienia pliku zgód",
                            f"{path}: właścicielem jest inny użytkownik (uid {stat.st_uid})",
                            "plik zgód powinien należeć do Ciebie"))
    return checks


def init_allow_file(path: Path) -> int:
    """Tworzy pusty plik zgód. Nie nadpisuje istniejącego pliku."""
    if path.exists():
        print(f"Plik zgód już istnieje: {path}. Nic nie zmieniono.")
        print(f"Sprawdź go poleceniem: {doctor_command()}")
        return 0
    content = {"$schema": SCHEMA_URL, "commands": {key: [] for key in ROLE_KEYS}}
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    except OSError as error:
        print(f"BŁĄD: nie utworzono pliku zgód {path}: {error}")
        return 1
    print(f"Utworzono pusty plik zgód: {path}")
    print("Dopisz początki poleceń, które agenci mają wykonywać sami, np.:")
    print('  "orchestrator": ["dotnet build"], "*": ["make lint"]')
    print("Agenci nie mogą zmieniać tego pliku. Sprawdzenie: " + doctor_command())
    return 0


# --- Instalacja ------------------------------------------------------------------------

def install_kind(runtime: Path = RUNTIME_DIR) -> str:
    parts = [part.lower() for part in runtime.parts]
    if (runtime.parent / ".claude-plugin" / "plugin.json").exists() and "plugins" in parts:
        return "wtyczka Claude Code"
    if (runtime.parent / ".git").exists():
        return "repozytorium FlowKit (tryb deweloperski)"
    if parts[-3:] == [".github", "flowkit", "runtime"]:
        return "VS Code (instalator, katalog projektu)"
    if parts[-3:] == [".claude", "flowkit", "runtime"]:
        return "Claude Code (instalator)"
    return "instalacja ręczna"


def plugin_version(runtime: Path = RUNTIME_DIR) -> str | None:
    manifest = runtime.parent / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("version")
    except (OSError, ValueError):
        return None


def hook_python() -> tuple[str | None, str | None]:
    """Interpreter `python`, którego używają hooki Claude Code, i jego wersja."""
    path = shutil.which("python")
    if path is None:
        return None, None
    try:
        result = subprocess.run([path, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
                                capture_output=True, text=True, timeout=10, check=False)
        return path, result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return path, None


def agent_dirs() -> list[Path]:
    return [Path.home() / ".claude" / "agents", Path.cwd() / ".claude" / "agents", Path.cwd() / ".github" / "agents"]


def check_installation() -> list[Check]:
    section = "Instalacja"
    checks = [Check(section, OK, "Runtime", f"FlowKit {fx.VERSION}, {RUNTIME_DIR} ({install_kind()})")]
    manifest = plugin_version()
    if manifest and manifest != fx.VERSION:
        checks.append(Check(section, ERROR, "Wersja", f"wtyczka {manifest}, runtime {fx.VERSION}",
                            "zaktualizuj wtyczkę: claude plugin update flowkit@flowkit"))
    missing = [name for name in RUNTIME_FILES if not (RUNTIME_DIR / name).exists()]
    if missing:
        checks.append(Check(section, ERROR, "Pliki runtime", f"brak: {', '.join(missing)}",
                            "zainstaluj ponownie agentów i runtime (instalator z opcją agent all)"))
    if sys.version_info < MIN_PYTHON:
        checks.append(Check(section, ERROR, "Python", f"{sys.version.split()[0]}, wymagany 3.10+",
                            "zainstaluj Python 3.10 lub nowszy"))
    path, version = hook_python()
    if path is None:
        checks.append(Check(section, ERROR, "Python dla hooków", "polecenie `python` nie jest dostępne w PATH; "
                            "hooki Claude Code nie zadziałają", "dodaj Pythona do PATH (w Windows zaznacz "
                            "„Add python.exe to PATH” w instalatorze)"))
    elif "windowsapps" in path.lower() and version is None:
        checks.append(Check(section, ERROR, "Python dla hooków", f"{path} to skrót Microsoft Store, nie Python",
                            "zainstaluj Pythona z python.org i wyłącz alias w Ustawienia → Aplikacje → "
                            "Aliasy wykonywania aplikacji"))
    elif version is None or tuple(int(x) for x in version.split(".")) < MIN_PYTHON:
        checks.append(Check(section, ERROR, "Python dla hooków", f"{path}: wersja {version or 'nieznana'}, "
                            "wymagana 3.10+", "ustaw w PATH Pythona 3.10 lub nowszego"))
    else:
        checks.append(Check(section, OK, "Python dla hooków", f"{path} ({version})"))

    return checks + check_agents() + check_manual_runtime()


def reinstall_hint(directory: Path) -> str:
    """Polecenie ponownej instalacji agentów i runtime dla katalogu, w którym leżą agenci."""
    vscode = directory.parent.name == ".github"
    script = r"<repozytorium FlowKit>\scripts\install.ps1" if os.name == "nt" else "<repozytorium FlowKit>/scripts/install.sh"
    if os.name == "nt":
        command = f"{script} -AgentName all -Platform {'vscode' if vscode else 'claude'} -Force"
    else:
        command = f"{script} agent all --platform {'vscode' if vscode else 'claude'} --force"
    return command + (f" (uruchom w katalogu projektu {directory.parent.parent})" if vscode else "")


def agent_tools(text: str) -> list[str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return []
    tools = re.search(r"^tools:\s*\n((?:\s*-\s*.+\n?)+)", match.group(1), re.MULTILINE)
    return re.findall(r"-\s*([^\s#]+)", tools.group(1)) if tools else []


def plugin_installed() -> bool:
    registry = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    try:
        return "flowkit@" in registry.read_text(encoding="utf-8")
    except OSError:
        return False


def check_agents() -> list[Check]:
    """Wersja zainstalowanych agentów, narzędzie okna pytań orkiestratora i podwójna instalacja."""
    section = "Instalacja"
    checks: list[Check] = []
    found = 0
    for directory in agent_dirs():
        if not directory.is_dir():
            continue
        stale = []
        for agent in sorted(directory.glob("flowkit-*.md")):
            found += 1
            text = agent.read_text(encoding="utf-8", errors="replace")
            marker = AGENT_MARKER.search(text[:2000])
            version = marker.group(1) if marker else "starsza niż 1.8.0"
            if version != fx.VERSION:
                stale.append(f"{agent.name} ({version})")
            if agent.name.startswith("flowkit-orchestrator"):
                tool = "vscode/askQuestions" if agent.name.endswith(".agent.md") else "AskUserQuestion"
                if tool not in agent_tools(text):
                    checks.append(Check(section, ERROR, "Okno pytań", f"{agent}: orkiestrator nie ma narzędzia {tool}, "
                                        "więc pyta zwykłym tekstem (`Ask: text`)", reinstall_hint(directory)))
        if stale:
            checks.append(Check(section, WARN, "Agenci", f"{directory}: inna wersja niż runtime {fx.VERSION}: "
                                + ", ".join(stale[:4]) + (" …" if len(stale) > 4 else ""), reinstall_hint(directory)))
        for legacy in sorted(directory.glob("agent-3x3*.md")):
            checks.append(Check(section, WARN, "Starzy agenci", f"{legacy} (wersja 1.7)", "usuń ten plik"))
    home_agents = Path.home() / ".claude" / "agents"
    if plugin_installed() and any(home_agents.glob("flowkit-*.md")):
        checks.append(Check(section, WARN, "Podwójna instalacja", "jest wtyczka FlowKit i agenci z instalatora w "
                            f"{home_agents}; `claude --agent flowkit-orchestrator` uruchamia agenta z instalatora, a "
                            "`flowkit:flowkit-orchestrator` — z wtyczki", "zostaw jedną instalację: usuń pliki "
                            f"flowkit-*.md z {home_agents} albo odinstaluj wtyczkę"))
    if not found:
        checks.append(Check(section, INFO, "Agenci", "brak plików agentów w ~/.claude/agents, .claude/agents i "
                            ".github/agents (przy instalacji jako wtyczka to prawidłowe)"))
    elif not any(c.name in ("Agenci", "Okno pytań") for c in checks):
        checks.append(Check(section, OK, "Agenci", f"{found} plików agentów w wersji {fx.VERSION}"))
    return checks


def check_manual_runtime() -> list[Check]:
    """Agenci z instalatora używają runtime z ~/.claude/flowkit/runtime — może być starszy niż ten."""
    manual = Path.home() / ".claude" / "flowkit" / "runtime"
    if manual.resolve() == RUNTIME_DIR or not (manual / "flowkit_exec.py").exists():
        return []
    match = re.search(r'^VERSION = "([^"]+)"', (manual / "flowkit_exec.py").read_text(encoding="utf-8", errors="replace"),
                      re.MULTILINE)
    version = match.group(1) if match else "starsza niż 1.8.0"
    if version == fx.VERSION:
        return [Check("Instalacja", OK, "Runtime instalatora", f"{manual} ({version})")]
    return [Check("Instalacja", WARN, "Runtime instalatora", f"{manual}: wersja {version}, a ten runtime {fx.VERSION}; "
                  "agenci z instalatora używają starszych zasad (np. listy poleceń ról)", reinstall_hint(manual.parent.parent / "agents"))]


# --- Bezpieczeństwo i konfiguracja ----------------------------------------------------

def check_security() -> list[Check]:
    section = "Bezpieczeństwo"
    checks = inspect_allow_file(fx.allow_file())
    audit = fx.audit_file()
    if audit is None:
        checks.append(Check(section, INFO, "Dziennik audytu", f"wyłączony ({fx.AUDIT_FILE_ENV}=off)"))
    else:
        directory = audit.parent
        existing = next((p for p in (directory, *directory.parents) if p.exists()), None)
        if audit.exists() and not os.access(audit, os.W_OK):
            checks.append(Check(section, ERROR, "Dziennik audytu", f"{audit}: brak prawa zapisu",
                                "przywróć prawo zapisu albo ustaw inną ścieżkę w " + fx.AUDIT_FILE_ENV))
        elif existing is None or not os.access(existing, os.W_OK):
            checks.append(Check(section, ERROR, "Dziennik audytu", f"{directory}: nie można utworzyć katalogu",
                                "ustaw zapisywalną ścieżkę w " + fx.AUDIT_FILE_ENV))
        else:
            state = "istnieje" if audit.exists() else "powstanie przy pierwszym poleceniu agenta"
            checks.append(Check(section, OK, "Dziennik audytu", f"{audit} ({state})"))
    mode = "włączony: bez zmian plików, DOCX, commit i push" if fx.readonly() else "wyłączony"
    checks.append(Check(section, INFO, fx.READONLY_ENV, mode))
    return checks


def check_configuration() -> list[Check]:
    section = "Konfiguracja"
    project = Path.cwd() / "flowkit-project.md"
    checks = [Check(section, OK if project.is_file() else INFO, "flowkit-project.md",
                    str(project) if project.is_file() else "brak (opcjonalny; wzór: docs/flowkit-project.template.md)")]
    extra = [item.strip() for item in os.environ.get(fx.EXTRA_PATHS_ENV, "").split(os.pathsep) if item.strip()]
    if not extra:
        checks.append(Check(section, INFO, fx.EXTRA_PATHS_ENV, "nie ustawiono (agenci czytają tylko katalog projektu)"))
    for item in extra:
        path = Path(item).expanduser()
        if path.is_dir():
            checks.append(Check(section, OK, fx.EXTRA_PATHS_ENV, str(path)))
        else:
            checks.append(Check(section, WARN, fx.EXTRA_PATHS_ENV, f"{path}: katalog nie istnieje",
                                f"popraw ścieżkę (separator: '{os.pathsep}')"))
    return checks


def check_tools() -> list[Check]:
    section = "Narzędzia"
    has = {name: importlib.util.find_spec(module) is not None
           for name, module in (("python-docx", "docx"), ("pyyaml", "yaml"), ("pypdf", "pypdf"))}
    pandoc = shutil.which("pandoc") is not None
    checks = [Check(section, OK if has["python-docx"] or pandoc else WARN, "Zapis DOCX",
                    "python-docx" if has["python-docx"] else "Pandoc" if pandoc else "brak silnika DOCX",
                    "" if has["python-docx"] or pandoc else "pip install python-docx")]
    for name, purpose, fix in (("pyyaml", "diagramy skilla PT/PRD", "pip install pyyaml"),
                               ("pypdf", "odczyt PDF", "pip install pypdf")):
        checks.append(Check(section, OK if has[name] else WARN, name, purpose if has[name] else f"brak — {purpose}",
                            "" if has[name] else fix))
    optional = [tool for tool in ("mmdc", "rsvg-convert", "terraform", "helm", "kubectl", "docker") if shutil.which(tool)]
    checks.append(Check(section, INFO, "Narzędzia opcjonalne", ", ".join(optional) or "brak (sprawdzenia dostaną NOT_RUN)"))
    return checks


def collect() -> list[Check]:
    return check_installation() + check_security() + check_configuration() + check_tools()


# --- Wynik -----------------------------------------------------------------------------

def print_report(checks: list[Check], role: str | None) -> None:
    print(f"FlowKit doctor {fx.VERSION}" + (f" (rola: {role})" if role else ""))
    section = None
    for check in checks:
        if check.section != section:
            section = check.section
            print(f"\n== {section} ==")
        print(f"  {check.status:<6} {check.name}: {check.detail}")
        if check.fix:
            print(f"         → {check.fix}")
    errors = sum(c.status == ERROR for c in checks)
    warnings = sum(c.status == WARN for c in checks)
    print(f"\nPodsumowanie: błędy {errors}, uwagi {warnings}.")


def role_view(role: str) -> list[Check]:
    allowed, _ = fx.user_allowed(role)
    return [Check("Bezpieczeństwo", INFO, f"Zgody dla roli {role}", ", ".join(allowed) or "brak")]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", nargs="?", choices=("check", "init"), default="check")
    parser.add_argument("--role", choices=sorted(fx.ROLE_COMMANDS), help="pokaż zgody aktywne dla tej roli")
    parser.add_argument("--json", action="store_true", help="wynik w JSON")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 2
    if args.action == "init":
        return init_allow_file(fx.allow_file())
    checks = collect()
    if args.role:
        checks += role_view(args.role)
    checks.sort(key=lambda c: ["Instalacja", "Bezpieczeństwo", "Konfiguracja", "Narzędzia"].index(c.section))
    if args.json:
        print(json.dumps({"version": fx.VERSION, "checks": [asdict(c) for c in checks]}, ensure_ascii=False, indent=2))
    else:
        print_report(checks, args.role)
    return 1 if any(c.status == ERROR for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
