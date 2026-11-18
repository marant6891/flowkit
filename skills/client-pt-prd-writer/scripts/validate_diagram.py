"""Kontrola jakości diagramu: model, geometria, zgodność z dokumentem i render.

Użycie:
  python validate_diagram.py model.yaml [...] [--document dokument.md|.docx]
      [--mode working|final] [--svg-dir diagrams/] [--no-render]

Kody wyjścia: 0 = zaliczono, 1 = wykryto błędy.
Gdy brak przeglądarki, kontrola renderu jest zgłaszana jako POMINIĘTA, nie jako zaliczona.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_core import (  # noqa: E402
    ModelError, UNKNOWN, contrast, build_theme, load_model, sources_of, validate_model, visible_texts,
)
from docx_support import open_document  # noqa: E402
from export_diagram import open_browser  # noqa: E402
from generate_diagram import base_name, render  # noqa: E402

RENDER_CHECK = """
() => {
  const issues = [];
  const svg = document.querySelector('svg');
  const vb = svg.viewBox.baseVal;
  const items = [...svg.querySelectorAll('text')].map(el => ({el, b: el.getBBox(), t: el.textContent}));
  for (const {el, b, t} of items) {
    if (b.x < vb.x - 0.5 || b.y < vb.y - 0.5 || b.x + b.width > vb.x + vb.width + 0.5 || b.y + b.height > vb.y + vb.height + 0.5)
      issues.push('tekst obcięty przez kadr: ' + t);
    const box = el.getAttribute('data-box');
    if (box) {
      const [x, y, w, h] = box.split(' ').map(Number);
      if (b.x < x - 1 || b.x + b.width > x + w + 1 || b.y < y - 1 || b.y + b.height > y + h + 1)
        issues.push('tekst wychodzi poza element: ' + t);
    }
  }
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
    const a = items[i].b, b = items[j].b;
    if (a.x + 1 < b.x + b.width && b.x + 1 < a.x + a.width && a.y + 2 < b.y + b.height && b.y + 2 < a.y + a.height)
      issues.push('teksty nachodzą na siebie: ' + items[i].t + ' / ' + items[j].t);
  }
  return issues;
}
"""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def document_text(path: Path) -> str:
    if path.suffix.lower() in (".docx", ".dotx"):
        doc = open_document(path)
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts += [cell.text for cell in row.cells]
        return "\n".join(parts)
    return path.read_text(encoding="utf-8")


STOP_WORDS = {"oraz", "przez", "przy", "jest", "dla", "lub", "albo", "między", "miedzy", "pomiędzy", "pomiedzy"}


def fold(text: str) -> str:
    """Porównanie bez wielkości liter i polskich znaków."""
    text = text.replace("ł", "l").replace("Ł", "L")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


def words(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", fold(text))


def missing_words(text: str, document_words: set[str]) -> list[str]:
    """Słowa bez odpowiednika w dokumencie; rdzeń dopuszcza polską odmianę."""
    missing = []
    for word in words(text.replace(UNKNOWN, " ")):
        if len(word) < 4 or word.isdigit() or word in STOP_WORDS:
            continue
        stem = word[:max(4, len(word) - 3)]
        if not any(candidate.startswith(stem) for candidate in document_words):
            missing.append(word)
    return missing


def check_against_document(model: dict, text: str, mode: str) -> list[str]:
    """Treść grafiki musi wynikać z dokumentu, a oznaczenia źródeł być w dokumencie roboczym."""
    errors = []
    haystack = normalize(text)
    folded = " ".join(words(text))
    document_words = set(folded.split())
    for node in model.get("nodes") or []:
        label = str(node.get("label", ""))
        pattern = r"(?<![^\W_])" + r"\s+".join(re.escape(w) for w in words(label)) + r"(?![^\W_])"
        if UNKNOWN not in label and not re.search(pattern, folded):
            errors.append(f"węzeł '{label}' nie występuje w tekście dokumentu")
    details = [("połączenie", c.get("label")) for c in model.get("connections") or []]
    details += [("grupa", g.get("label")) for g in model.get("groups") or []]
    details += [("rola", l.get("label")) for l in model.get("lanes") or []]
    details += [("adnotacja", a.get("text")) for a in model.get("annotations") or []]
    for node in model.get("nodes") or []:
        details += [("opis węzła", node.get("sublabel")), ("data", node.get("date"))]
        details += [("atrybut", a) for a in node.get("attributes") or []]
    for kind, value in details:
        for word in missing_words(str(value or ""), document_words):
            errors.append(f"{kind} '{value}': słowo '{word}' nie występuje w dokumencie")
    section = str((model.get("source") or {}).get("section", ""))
    if section and normalize(re.sub(r"^\d+(\.\d+)*\.?\s*", "", section)) not in haystack:
        errors.append(f"sekcja źródłowa '{section}' nie istnieje w dokumencie")
    if mode == "working":
        elements = list(model.get("nodes") or []) + list(model.get("connections") or []) + list(model.get("remarks") or [])
        for ref in sorted({r for e in elements for r in sources_of(e)}):
            if ref not in text:
                errors.append(f"oznaczenie {ref} nie występuje w dokumencie")
    return errors


def check_theme(model: dict) -> list[str]:
    t = build_theme(model)
    errors = []
    for name, fg, bg, minimum in (("tekst", t["ink"], t["paper"], 4.5), ("opis", t["muted"], t["paper"], 4.5),
                                  ("linie", t["line"], t["paper"], 3.0), ("akcent", t["accent"], t["paper"], 3.0)):
        if contrast(fg, bg) < minimum:
            errors.append(f"za niski kontrast ({name}): {contrast(fg, bg):.2f}:1, wymagane {minimum}:1")
    return errors


def validate_one(path: Path, text: str | None, mode: str) -> tuple[dict | None, list[str], list[str]]:
    warnings: list[str] = []
    try:
        model = load_model(path)
    except ModelError as error:
        return None, error.errors, warnings
    errors = validate_model(model, mode)
    if errors:
        return model, errors, warnings
    _canvas, issues = render(model)
    errors += issues + check_theme(model)
    if text is not None:
        errors += check_against_document(model, text, mode)
    nodes, conns = len(model.get("nodes") or []), len(model.get("connections") or [])
    if nodes > 12 or conns > 16:
        warnings.append(f"duża gęstość ({nodes} elementów, {conns} połączeń): rozważ podział na przegląd i szczegóły")
    if sum(1 for n in model.get("nodes") or [] if n.get("focus")) > 2:
        errors.append("więcej niż 2 elementy wyróżnione akcentem: diagram traci punkt skupienia")
    if not visible_texts(model):
        errors.append("diagram nie zawiera żadnego tekstu")
    return model, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("models", nargs="+", type=Path)
    parser.add_argument("--document", type=Path)
    parser.add_argument("--mode", choices=("working", "final"), default="working")
    parser.add_argument("--svg-dir", type=Path, help="katalog z SVG do kontroli po wyrenderowaniu")
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()

    text = document_text(args.document) if args.document else None
    failed = 0
    results = []
    ids: dict[str, Path] = {}
    for path in args.models:
        model, errors, warnings = validate_one(path, text, args.mode)
        if model and model.get("id") in ids:
            errors.append(f"powielony identyfikator diagramu {model['id']} (także w {ids[model['id']].name})")
        if model:
            ids[str(model.get("id"))] = path
        results.append((path, model, errors, warnings))

    playwright, browser = (None, None)
    if args.svg_dir and not args.no_render:
        playwright, browser = open_browser()
    try:
        for path, model, errors, warnings in results:
            if args.svg_dir and model and not errors:
                svg = args.svg_dir / f"{base_name(model)}.svg"
                if not svg.exists():
                    errors.append(f"brak pliku {svg.name}")
                elif browser:
                    page = browser.new_page()
                    page.set_content(f"<!doctype html><html><body>{svg.read_text(encoding='utf-8')}</body></html>")
                    errors.extend(sorted(set(page.evaluate(RENDER_CHECK))))
                    page.close()
                elif not args.no_render:
                    warnings.append("kontrola po wyrenderowaniu POMINIĘTA: brak przeglądarki")
            failed += bool(errors)
            print(f"{'BŁĄD' if errors else 'OK'} {path.name}")
            for error in errors:
                print(f"  - {error}")
            for warning in warnings:
                print(f"  ! {warning}")
    finally:
        if browser:
            browser.close()
            playwright.stop()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
