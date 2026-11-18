"""Model pośredni diagramu, motywy i pomiar tekstu (Documentation Diagrams Engine).

Moduł nie ma zależności poza PyYAML. Nie renderuje grafiki: patrz generate_diagram.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

MODEL_VERSION = "1.0"
UNKNOWN = "DO POTWIERDZENIA"

LAYERED_TYPES = {
    "architecture", "component", "flowchart", "state-machine", "er", "data-flow",
    "swimlane", "deployment", "dependency", "integration",
}
SEQUENCE_TYPES = {"sequence"}
TIMELINE_TYPES = {"timeline", "user-journey"}
MATRIX_TYPES = {"requirement-traceability", "security-matrix"}
DIAGRAM_TYPES = LAYERED_TYPES | SEQUENCE_TYPES | TIMELINE_TYPES | MATRIX_TYPES

TYPE_LABELS = {
    "architecture": "Architektura", "component": "Komponenty", "flowchart": "Proces",
    "state-machine": "Stany i przejścia", "er": "Model danych", "data-flow": "Przepływ danych",
    "swimlane": "Proces i role", "deployment": "Wdrożenie", "dependency": "Zależności",
    "integration": "Integracje", "sequence": "Sekwencja", "timeline": "Oś czasu",
    "user-journey": "Ścieżka użytkownika", "requirement-traceability": "Śledzenie wymagań",
    "security-matrix": "Macierz uprawnień",
}

NODE_TYPES = {
    "application", "service", "database", "external", "actor", "queue", "process",
    "decision", "state", "start", "end", "entity", "step", "item", "participant",
}
DIRECTIONS = {"forward", "both", "none", "unknown"}
THEMES = {"minimal-light", "minimal-dark", "full-editorial"}
SOURCE_RE = re.compile(r"^(SRC|ASSUMPTION|OPEN)-\d{3}$")
ID_RE = re.compile(r"^D-\d{2,3}$")
PLACEHOLDER_RE = re.compile(r"\b(TBD|TODO|N/A|lorem ipsum)\b", re.IGNORECASE)
# Etykiety nie mogą przemycać mechanizmów bez źródła tylko przez brak pola "source".
MARKER_RE = re.compile(r"(SRC|ASSUMPTION|OPEN|Q|REC)-\d{3}|DO POTWIERDZENIA|Nie analizowano|Brak danych")

FONT_STACK = "'Segoe UI', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif"
MONO_STACK = "'Cascadia Mono', Consolas, 'DejaVu Sans Mono', monospace"
SERIF_STACK = "Georgia, 'Times New Roman', serif"

THEME_TOKENS = {
    "minimal-light": {
        "paper": "#FFFFFF", "paper2": "#F5F4F1", "node": "#FFFFFF", "ink": "#262A31",
        "muted": "#59616D", "rule": "#BFC4CB", "line": "#59616D", "accent": "#B4492F",
        "warn": "#8A5A00", "warn_tint": "#FCF4E3", "external": "#F1F0ED",
    },
    "minimal-dark": {
        "paper": "#1D2128", "paper2": "#272C35", "node": "#242932", "ink": "#ECEEF1",
        "muted": "#B3BBC7", "rule": "#535C69", "line": "#A5AEBB", "accent": "#EE9379",
        "warn": "#E8C06A", "warn_tint": "#392F1E", "external": "#2B313B",
    },
    "full-editorial": {
        "paper": "#FBF9F5", "paper2": "#F2EEE6", "node": "#FFFFFF", "ink": "#23262C",
        "muted": "#59606B", "rule": "#BDB9AF", "line": "#59606B", "accent": "#A8412A",
        "warn": "#855500", "warn_tint": "#FBF1DC", "external": "#EFEBE3",
    },
}


class ModelError(ValueError):
    """Model diagramu jest niepoprawny; lista błędów w atrybucie ``errors``."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def sources_of(element: dict) -> list[str]:
    value = element.get("source")
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def certainty(element: dict) -> str:
    """confirmed / assumption / open: wynika wprost z oznaczeń pochodzenia."""
    refs = sources_of(element)
    if any(r.startswith("OPEN-") for r in refs):
        return "open"
    if any(r.startswith("ASSUMPTION-") for r in refs):
        return "assumption"
    return "confirmed"


def load_model(path: str | Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("diagram"), dict):
        raise ModelError([f"{path}: plik musi zawierać główny klucz 'diagram'"])
    return data["diagram"]


def _check_source(element: dict, where: str, errors: list[str]) -> None:
    refs = sources_of(element)
    if not refs:
        errors.append(f"{where}: brak pola 'source' (SRC-NNN, ASSUMPTION-NNN lub OPEN-NNN)")
    for ref in refs:
        if not SOURCE_RE.match(str(ref)):
            errors.append(f"{where}: niepoprawne oznaczenie źródła '{ref}'")


def _check_text(text: object, element: dict, where: str, errors: list[str]) -> None:
    value = str(text or "")
    if PLACEHOLDER_RE.search(value):
        errors.append(f"{where}: użyj '{UNKNOWN}' zamiast '{value}'")
    if UNKNOWN in value and certainty(element) != "open":
        errors.append(f"{where}: '{UNKNOWN}' wymaga źródła OPEN-NNN")


def validate_model(model: dict, mode: str = "working") -> list[str]:
    """Zwraca listę błędów merytorycznych modelu (pusta = model poprawny)."""
    errors: list[str] = []
    for key in ("id", "title", "type", "purpose", "caption", "explanation", "alt"):
        if not str(model.get(key) or "").strip():
            errors.append(f"brak wymaganego pola '{key}'")
    if str(model.get("model_version")) != MODEL_VERSION:
        errors.append(f"'model_version' musi mieć wartość \"{MODEL_VERSION}\"")
    if model.get("id") and not ID_RE.match(str(model["id"])):
        errors.append(f"'id' musi mieć format D-01, otrzymano '{model['id']}'")
    dtype = model.get("type")
    if dtype not in DIAGRAM_TYPES:
        errors.append(f"nieobsługiwany typ diagramu '{dtype}'")
    section = (model.get("source") or {}).get("section") if isinstance(model.get("source"), dict) else None
    if not section:
        errors.append("brak 'source.section' (sekcja dokumentu, której dotyczy diagram)")
    theme = (model.get("output") or {}).get("theme", "minimal-light")
    if theme not in THEMES:
        errors.append(f"nieobsługiwany motyw '{theme}'")

    nodes = model.get("nodes") or []
    conns = model.get("connections") or []
    if not nodes:
        errors.append("diagram nie ma żadnych elementów ('nodes')")
    seen: set[str] = set()
    for i, node in enumerate(nodes):
        nid = node.get("id")
        where = f"węzeł '{nid or i}'"
        if not nid:
            errors.append(f"{where}: brak 'id'")
        elif nid in seen:
            errors.append(f"{where}: powielony identyfikator")
        seen.add(nid)
        if not str(node.get("label") or "").strip():
            errors.append(f"{where}: brak 'label'")
        if node.get("type", "service") not in NODE_TYPES:
            errors.append(f"{where}: nieznany typ '{node.get('type')}'")
        _check_source(node, where, errors)
        for field in ("label", "sublabel", "date"):
            _check_text(node.get(field), node, where, errors)

    containers = {}
    for key in ("groups", "lanes"):
        for item in model.get(key) or []:
            containers[item.get("id")] = key
            _check_source(item, f"{key} '{item.get('id')}'", errors)
            _check_text(item.get("label"), item, f"{key} '{item.get('id')}'", errors)
    for node in nodes:
        for field, key in (("group", "groups"), ("lane", "lanes")):
            if node.get(field) and containers.get(node[field]) != key:
                errors.append(f"węzeł '{node.get('id')}': nieznane '{field}' = '{node[field]}'")
    if dtype == "swimlane":
        if not model.get("lanes"):
            errors.append("swimlane wymaga listy 'lanes'")
        for node in nodes:
            if not node.get("lane"):
                errors.append(f"węzeł '{node.get('id')}': swimlane wymaga pola 'lane'")
    if dtype in MATRIX_TYPES:
        for node in nodes:
            if node.get("axis") not in ("row", "column"):
                errors.append(f"węzeł '{node.get('id')}': macierz wymaga 'axis: row' lub 'axis: column'")

    for i, conn in enumerate(conns):
        where = f"połączenie {conn.get('from')}→{conn.get('to')}"
        for end in ("from", "to"):
            if conn.get(end) not in seen:
                errors.append(f"{where}: nieznany węzeł '{conn.get(end)}'")
        if conn.get("from") == conn.get("to") and dtype not in SEQUENCE_TYPES:
            errors.append(f"{where}: pętla własna jest obsługiwana tylko w diagramie sekwencji")
        direction = conn.get("direction", "forward")
        if direction not in DIRECTIONS:
            errors.append(f"{where}: nieznany kierunek '{direction}'")
        if direction == "none" and dtype != "er" and dtype not in MATRIX_TYPES:
            errors.append(f"{where}: brak kierunku dozwolony tylko w ER i macierzach; "
                          "dla nieznanego kierunku użyj 'direction: unknown' i OPEN-NNN")
        if direction == "unknown" and certainty(conn) != "open":
            errors.append(f"{where}: 'direction: unknown' wymaga źródła OPEN-NNN")
        _check_source(conn, where, errors)
        _check_text(conn.get("label"), conn, where, errors)
    for i, note in enumerate(model.get("annotations") or []):
        _check_source(note, f"adnotacja {i + 1}", errors)
        _check_text(note.get("text"), note, f"adnotacja {i + 1}", errors)

    if mode == "final":
        errors.extend(final_mode_errors(model))
    return errors


def visible_texts(model: dict) -> list[str]:
    """Wszystkie teksty, które trafią na grafikę."""
    texts: list[str] = []
    for node in model.get("nodes") or []:
        texts += [node.get("label"), node.get("sublabel"), node.get("date")]
        texts += [str(a) for a in node.get("attributes") or []]
    for conn in model.get("connections") or []:
        texts.append(conn.get("label"))
    for key in ("groups", "lanes"):
        texts += [item.get("label") for item in model.get(key) or []]
    texts += [note.get("text") for note in model.get("annotations") or []]
    return [str(t) for t in texts if t]


def final_mode_errors(model: dict) -> list[str]:
    errors = []
    elements = list(model.get("nodes") or []) + list(model.get("connections") or [])
    for key in ("groups", "lanes", "annotations"):
        elements += list(model.get(key) or [])
    for element in elements:
        if certainty(element) != "confirmed":
            name = element.get("id") or element.get("label") or element.get("text")
            errors.append(f"tryb końcowy: element '{name}' ma nierozstrzygnięte źródło "
                          f"{sources_of(element)}; potrzebna decyzja użytkownika")
    for text in visible_texts(model):
        if MARKER_RE.search(text):
            errors.append(f"tryb końcowy: oznaczenie robocze na grafice: '{text}'")
    return errors


# --- Kolory ---------------------------------------------------------------

def _rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in rgb))


def mix(color: str, other: str, amount: float) -> str:
    a, b = _rgb(color), _rgb(other)
    return _hex(tuple(a[i] * amount + b[i] * (1 - amount) for i in range(3)))


def contrast(color_a: str, color_b: str) -> float:
    def lum(color: str) -> float:
        parts = []
        for channel in _rgb(color):
            c = channel / 255
            parts.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2]
    hi, lo = sorted((lum(color_a), lum(color_b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def build_theme(model: dict, brand: dict | None = None) -> dict:
    output = model.get("output") or {}
    name = output.get("theme", "minimal-light")
    tokens = dict(THEME_TOKENS[name])
    tokens["name"] = name
    tokens["font"] = FONT_STACK
    tokens["mono"] = MONO_STACK
    tokens["heading"] = SERIF_STACK if name == "full-editorial" else FONT_STACK
    brand = {**(brand or {}), **{k: output[k] for k in ("accent", "font") if output.get(k)}}
    if brand.get("font"):
        tokens["font"] = f"'{brand['font']}', {FONT_STACK}"
        if name != "full-editorial":
            tokens["heading"] = tokens["font"]
    if brand.get("accent"):
        accent = str(brand["accent"])
        target = "#000000" if contrast(tokens["paper"], "#000000") > contrast(tokens["paper"], "#FFFFFF") else "#FFFFFF"
        step = 0
        while contrast(accent, tokens["paper"]) < 4.5 and step < 20:
            accent = mix(accent, target, 0.9)
            step += 1
        tokens["accent"] = accent
    tokens["accent_tint"] = mix(tokens["accent"], tokens["paper"], 0.10)
    return tokens


# --- Pomiar tekstu ---------------------------------------------------------

_NARROW = set("iljtfrI.,:;'|!()[] ")
_WIDE = set("mwMWŁ@%")


def text_width(text: str, size: float, bold: bool = False) -> float:
    total = 0.0
    for ch in text:
        if ch in _NARROW:
            total += 0.34
        elif ch in _WIDE:
            total += 0.90
        elif ch.isupper():
            total += 0.68
        else:
            total += 0.57
    return total * size * (1.07 if bold else 1.0)


def wrap(text: str, size: float, max_width: float, bold: bool = False) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in str(text).split():
        candidate = f"{current} {word}".strip()
        if current and text_width(candidate, size, bold) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def block_width(lines: list[str], size: float, bold: bool = False) -> float:
    return max((text_width(line, size, bold) for line in lines), default=0.0)


def snap(value: float, unit: int = 4) -> int:
    return int(round(value / unit) * unit)
