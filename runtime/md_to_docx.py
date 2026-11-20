"""Konwersja Markdown → DOCX dla FlowKit, lokalnie i bez sieci.

Użycie (przez executor):
  flowkit_exec.py --role <rola> -- md-to-docx <wejście.md> <wynik.docx> [opcje]

Opcje:
  --reference-doc PLIK   szablon .docx/.dotx; przejmowane są jego style (Pandoc i python-docx)
  --template PLIK        szablon .docx/.dotx z treścią (strona tytułowa, metryczka, stopki);
                         dokument trafia w miejsce akapitu [[FLOWKIT:TREŚĆ]] albo na koniec szablonu.
                         Wymusza silnik python-docx.
  --engine auto|pandoc|python-docx   domyślnie auto: Pandoc, a gdy go brak – python-docx
  --keep-images          zachowaj wyrenderowane diagramy obok wyniku (<wynik>_diagrams/)
  --set POLE=WARTOŚĆ     wypełnia pole szablonu (powtarzalne)
  --pdf                  podgląd PDF przez LibreOffice (soffice); bez niego status NOT_RUN

Po zapisie wynik jest ponownie otwierany i porównywany ze źródłem (nagłówki, tabele, obrazy,
nagłówki i stopki stron szablonu).

Bloki ```mermaid są renderowane do PNG lokalnym mermaid-cli (`mmdc` w PATH albo
`npx --no -p @mermaid-js/mermaid-cli`, bez pobierania pakietów). Obrazy SVG są zamieniane
na PNG: gotowy plik .png obok .svg → Playwright → CairoSVG → rsvg-convert. Obrazy z adresów
http(s) nie są pobierane – zostaje tekst alternatywny.

Kody wyjścia: 0 = sukces (ostrzeżenia na wyjściu), 1 = błąd danych, 3 = brak silnika DOCX,
4 = dokument zapisany, ale kontrola struktury nie przeszła.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flowkit_exec import EXTRA_PATHS_ENV, allowed_roots, within_allowed  # noqa: E402

CONTENT_MARKER = "[[FLOWKIT:TREŚĆ]]"
MERMAID_BLOCK = re.compile(r"^```+\s*mermaid[^\n]*\n(.*?)^```+[ \t]*$", re.DOTALL | re.MULTILINE)
IMAGE = re.compile(r'!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(\s+"[^"]*")?\s*\)')
TEMPLATE_TYPE = b"wordprocessingml.template.main+xml"
DOCUMENT_TYPE = b"wordprocessingml.document.main+xml"
PNG_SCALE = 2
RENDER_TIMEOUT = 180


class Report:
    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def warn(self, text: str) -> None:
        self.warnings.append(text)
        print(f"OSTRZEŻENIE: {text}")

    def note(self, text: str) -> None:
        self.notes.append(text)
        print(text)


# --- Szablony -------------------------------------------------------------------

def as_docx(template: Path, work_dir: Path) -> Path:
    """Zwraca ścieżkę .docx; szablon .dotx kopiuje z typem dokumentu. Plik źródłowy zostaje bez zmian."""
    if template.suffix.lower() != ".dotx":
        return template
    target = work_dir / (template.stem + "-szablon.docx")
    with zipfile.ZipFile(template) as source, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as copy:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(TEMPLATE_TYPE, DOCUMENT_TYPE)
            copy.writestr(item, data)
    return target


# --- Diagramy i obrazy ------------------------------------------------------------

def mermaid_commands() -> list[list[str]]:
    commands = []
    mmdc = shutil.which("mmdc")
    if mmdc:
        commands.append([mmdc])
    npx = shutil.which("npx")
    if npx:
        commands.append([npx, "--no", "-p", "@mermaid-js/mermaid-cli", "mmdc"])
    return commands


def render_mermaid(source: str, target: Path, report: Report) -> bool:
    source_file = target.with_suffix(".mmd")
    source_file.write_text(source, encoding="utf-8")
    for base in mermaid_commands():
        try:
            result = subprocess.run([*base, "-i", str(source_file), "-o", str(target), "-b", "white", "-s", str(PNG_SCALE)],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                    timeout=RENDER_TIMEOUT, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0 and target.exists():
            return True
    return False


def replace_mermaid(text: str, images_dir: Path, report: Report) -> str:
    counter = 0
    missing = 0

    def replace(match: re.Match) -> str:
        nonlocal counter, missing
        counter += 1
        target = images_dir / f"diagram-mermaid-{counter:02d}.png"
        if render_mermaid(match.group(1), target, report):
            return f"![Diagram {counter}]({target.as_posix()})"
        missing += 1
        return match.group(0)

    result = MERMAID_BLOCK.sub(replace, text)
    if counter:
        report.note(f"Diagramy mermaid: {counter - missing}/{counter} wyrenderowane do PNG.")
    if missing:
        report.warn(f"{missing} diagram(y) mermaid zostały jako blok kodu: brak lokalnego mermaid-cli. "
                    "Jednorazowo zainstaluj: npm install -g @mermaid-js/mermaid-cli")
    return result


def svg_to_png(svg: Path, png: Path) -> str | None:
    """Zwraca nazwę użytego renderera albo None."""
    if importlib.util.find_spec("playwright") is not None:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                for options in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
                    try:
                        browser = playwright.chromium.launch(**options)
                    except Exception:  # brak tej przeglądarki: próbujemy kolejnej
                        continue
                    try:
                        page = browser.new_page(device_scale_factor=PNG_SCALE)
                        page.set_content("<!doctype html><html><body style='margin:0;background:white'>"
                                         f"{svg.read_text(encoding='utf-8')}</body></html>")
                        page.locator("svg").first.screenshot(path=str(png))
                        return "playwright"
                    finally:
                        browser.close()
        except Exception:  # renderer niedostępny w tym środowisku: kolejny w kolejności
            pass
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg), write_to=str(png), scale=PNG_SCALE)
        return "cairosvg"
    except Exception:  # brak CairoSVG albo bibliotek Cairo
        pass
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        result = subprocess.run([rsvg, "-z", str(PNG_SCALE), "-o", str(png), str(svg)], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=RENDER_TIMEOUT, check=False)
        if result.returncode == 0 and png.exists():
            return "rsvg-convert"
    return None


def resolve_images(text: str, base_dir: Path, images_dir: Path, report: Report) -> str:
    converted: dict[Path, Path] = {}
    roots = [*allowed_roots(), images_dir.resolve()]  # katalog roboczy, FLOWKIT_EXTRA_PATHS i wyrenderowane diagramy

    def replace(match: re.Match) -> str:
        alt, target, title = match.group(1), match.group(2), match.group(3) or ""
        if re.match(r"^[a-z][a-z0-9+.-]*://", target, re.I) or target.startswith("//"):
            report.warn(f"obraz z sieci nie jest pobierany: {target}")
            return alt or "[obraz]"
        path = Path(target)
        path = path if path.is_absolute() else (base_dir / path)
        path = path.resolve()
        if not within_allowed(path, roots):
            report.warn(f"obraz poza katalogiem roboczym nie jest osadzany: {target} (zmienna {EXTRA_PATHS_ENV})")
            return alt or "[obraz]"
        if not path.exists():
            report.warn(f"brak pliku obrazu: {target}")
            return match.group(0)
        if path.suffix.lower() == ".svg":
            sibling = path.with_suffix(".png")
            if sibling.exists():
                path = sibling
            elif path in converted:
                path = converted[path]
            else:
                png = images_dir / f"{path.stem}.png"
                renderer = svg_to_png(path, png)
                if renderer is None:
                    report.warn(f"nie skonwertowano {target} do PNG (brak Playwright, CairoSVG i rsvg-convert); "
                                "uruchom export_diagram.py albo zainstaluj: pip install playwright && playwright install chromium")
                    return match.group(0)
                report.note(f"SVG → PNG ({renderer}): {target}")
                converted[path] = png
                path = png
        return f"![{alt}]({path.as_posix()}{title})"

    return IMAGE.sub(replace, text)


# --- Silnik Pandoc ------------------------------------------------------------------

def pandoc_path() -> str | None:
    found = shutil.which("pandoc")
    if found:
        return found
    if importlib.util.find_spec("pypandoc") is not None:
        try:
            import pypandoc
            path = pypandoc.get_pandoc_path()
            return path if path and Path(path).exists() else None
        except (OSError, RuntimeError):
            return None
    return None


def convert_pandoc(pandoc: str, source: Path, output: Path, reference: Path | None, resource_dirs: list[Path]) -> None:
    command = [pandoc, str(source), "-f", "markdown", "-t", "docx", "-o", str(output), "--standalone",
               f"--resource-path={os.pathsep.join(str(d) for d in resource_dirs)}"]
    if reference is not None:
        command.append(f"--reference-doc={reference}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            timeout=RENDER_TIMEOUT, check=False)
    text = result.stdout.decode("utf-8", "replace").strip()
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc zakończył się kodem {result.returncode}: {text}")
    for line in text.splitlines():
        print(f"pandoc: {line}")


# --- Silnik python-docx ---------------------------------------------------------------

INLINE = re.compile(r"(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`|\*[^*\s][^*]*\*|_[^_\s][^_]*_|\[[^\]]+\]\([^)\s]+\))")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
IMAGE_LINE = re.compile(r'^\s*!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)\s*$')


# Nazwy stylów w szablonach angielskich i polskich; pierwszy istniejący w szablonie wygrywa.
STYLE_ALIASES = {
    "Heading": ("Heading {n}", "Nagłówek {n}", "Naglowek {n}"),
    "List Bullet": ("List Bullet", "Lista punktowana", "Punktor"),
    "List Number": ("List Number", "Lista numerowana"),
    "Quote": ("Quote", "Cytat", "Block Text", "Tekst blokowy"),
    "Caption": ("Caption", "Legenda", "Podpis"),
    "Source Code": ("Source Code", "Kod", "Code", "HTML Preformatted", "HTML - wstępnie sformatowany"),
    "Table": ("Table Grid", "Tabela - Siatka", "Tabela – Siatka", "Table"),
}


def style_or_none(doc, name: str):
    """Styl szablonu po nazwie, identyfikatorze lub polskim odpowiedniku; None, gdy szablon go nie ma."""
    level = re.search(r"\s(\d)$", name)
    family = name[:level.start()] if level else name
    if family == "Heading" and level:
        candidates = [c.format(n=level.group(1)) for c in STYLE_ALIASES["Heading"]]
    elif level:
        candidates = [name]
    else:
        candidates = list(STYLE_ALIASES.get(name, (name,)))
    by_name = {str(st.name).casefold(): st for st in doc.styles}
    by_id = {str(st.style_id).casefold(): st for st in doc.styles}
    found = None
    for candidate in candidates:
        wanted = candidate.casefold()
        found = by_name.get(wanted) or by_id.get(wanted.replace(" ", ""))
        if found is not None:
            break
    return found


def template_table_style(doc):
    """Styl tabeli użyty już w szablonie klienta; potem Table Grid / Tabela - Siatka."""
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    for table in doc.element.body.iter(f"{namespace}tbl"):
        style = table.find(f"{namespace}tblPr/{namespace}tblStyle")
        if style is not None:
            wanted = style.get(f"{namespace}val", "").casefold()
            for st in doc.styles:
                if str(st.style_id).casefold() == wanted:
                    return st
    return style_or_none(doc, "Table")


def add_inline(paragraph, text: str) -> None:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith(("**", "__")) and len(part) > 4:
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
        elif part.startswith(("*", "_")) and len(part) > 2:
            paragraph.add_run(part[1:-1]).italic = True
        elif link := re.fullmatch(r"\[([^\]]+)\]\(([^)\s]+)\)", part):
            label, url = link.groups()
            paragraph.add_run(label if label == url or url.startswith("#") else f"{label} ({url})")
        else:
            paragraph.add_run(part.replace("\\*", "*").replace("\\_", "_"))


def add_paragraph(doc, text: str, style: str | None = None):
    paragraph = doc.add_paragraph()
    resolved = style_or_none(doc, style) if style else None
    if resolved is not None:
        paragraph.style = resolved
    add_inline(paragraph, text)
    return paragraph


def usable_width(doc):
    section = doc.sections[-1]
    return section.page_width - section.left_margin - section.right_margin


def add_image(doc, alt: str, path: Path, report: Report) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.image.image import Image

    if path.suffix.lower() == ".svg" or not path.exists():
        report.warn(f"obraz pominięty w DOCX: {path.name}")
        add_paragraph(doc, f"[{alt or path.name}]")
        return
    width = min(Image.from_file(str(path)).width, usable_width(doc))
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=width)
    if alt and not re.fullmatch(r"(diagram \d+|image|obraz)", alt, re.I):
        paragraph.paragraph_format.keep_with_next = True
        add_paragraph(doc, alt, "Caption").alignment = WD_ALIGN_PARAGRAPH.CENTER


def split_row(line: str) -> list[str]:
    line = line.strip()
    line = line[1:] if line.startswith("|") else line
    line = line[:-1] if line.endswith("|") and not line.endswith("\\|") else line
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", line)]


def add_table(doc, rows: list[list[str]], table_style=None) -> None:
    columns = max(len(row) for row in rows)
    table = doc.add_table(rows=len(rows), cols=columns)
    if table_style is not None:
        table.style = table_style
    for r, row in enumerate(rows):
        for c in range(columns):
            cell = table.cell(r, c)
            cell.paragraphs[0].text = ""
            add_inline(cell.paragraphs[0], row[c] if c < len(row) else "")
            if r == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True


def add_code(doc, lines: list[str]) -> None:
    from docx.shared import Pt

    style = style_or_none(doc, "Source Code")
    for line in lines or [""]:
        paragraph = doc.add_paragraph()
        if style is not None:
            paragraph.style = style
        run = paragraph.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        paragraph.paragraph_format.space_after = Pt(0)


def render_markdown(doc, text: str, report: Report, table_style=None) -> None:
    lines = text.replace("\r\n", "\n").split("\n")
    table_style = table_style if table_style is not None else template_table_style(doc)
    i = 0
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            add_paragraph(doc, " ".join(part.strip() for part in buffer))
            buffer.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            fence = re.match(r"`+", stripped).group(0)
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                code.append(lines[i])
                i += 1
            add_code(doc, code)
            i += 1
            continue
        if not stripped:
            flush()
            i += 1
            continue
        heading = HEADING.match(line)
        if heading:
            flush()
            level = len(heading.group(1))
            style = style_or_none(doc, f"Heading {level}")
            paragraph = doc.add_paragraph()
            if style is None:
                report.warn(f"szablon nie ma stylu nagłówka poziomu {level}; zapisano pogrubiony akapit")
                paragraph.add_run(heading.group(2)).bold = True
            else:
                paragraph.style = style
                add_inline(paragraph, heading.group(2))
            i += 1
            continue
        if "|" in stripped and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1]):
            flush()
            rows = [split_row(line)]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            add_table(doc, rows, table_style)
            continue
        image = IMAGE_LINE.match(line)
        if image:
            flush()
            add_image(doc, image.group(1), Path(image.group(2)), report)
            i += 1
            continue
        item = LIST_ITEM.match(line)
        if item:
            flush()
            numbered = item.group(2)[0].isdigit()
            level = min(len(item.group(1).expandtabs(4)) // 2, 2)
            name = ("List Number" if numbered else "List Bullet") + (f" {level + 1}" if level else "")
            if style_or_none(doc, name) is None:
                name = "List Number" if numbered else "List Bullet"
            if style_or_none(doc, name) is None:
                add_paragraph(doc, ("  " * level) + ("• " if not numbered else item.group(2) + " ") + item.group(3))
            else:
                add_paragraph(doc, item.group(3), name)
            i += 1
            continue
        if stripped.startswith(">"):
            flush()
            add_paragraph(doc, stripped.lstrip("> "), "Quote")
            i += 1
            continue
        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            flush()
            i += 1
            continue
        buffer.append(line)
        i += 1
    flush()


def fill_placeholders(doc, values: dict[str, str]) -> int:
    """Zastępuje pola szablonu w treści, tabelach, nagłówkach i stopkach, zachowując formatowanie fragmentów."""
    def paragraphs(container):
        yield from container.paragraphs
        for table in container.tables:
            for row in table.rows:
                for cell in row.cells:
                    yield from paragraphs(cell)

    def replace(paragraph, key, value) -> int:
        count, offset = 0, 0
        while True:
            runs = paragraph.runs
            start = "".join(run.text for run in runs).find(key, offset)
            if start < 0:
                return count
            end, position, first = start + len(key), 0, True
            for run in runs:
                run_start, run_end = position, position + len(run.text)
                position = run_end
                if run_end <= start or run_start >= end:
                    continue
                before = run.text[:max(start - run_start, 0)]
                after = run.text[end - run_start:] if run_end > end else ""
                run.text = before + (value if first else "") + after
                first = False
            count += 1
            offset = start + len(value)

    containers = [doc]
    for section in doc.sections:
        containers += [section.header, section.footer, section.first_page_header,
                       section.first_page_footer, section.even_page_header, section.even_page_footer]
    total = 0
    for container in containers:
        for paragraph in paragraphs(container):
            for key, value in values.items():
                total += replace(paragraph, key, value)
    return total


def clear_body(doc) -> None:
    body = doc.element.body
    for child in list(body):
        if not child.tag.endswith("}sectPr"):
            body.remove(child)


def convert_python_docx(source_text: str, output: Path, reference: Path | None, template: Path | None,
                        report: Report, values: dict[str, str] | None = None) -> None:
    from docx import Document

    def fill(doc) -> None:
        if values:
            report.note(f"Pola szablonu: wypełniono {fill_placeholders(doc, values)} wystąpień ({len(values)} pól).")

    if template is not None:
        doc = Document(str(template))
        fill(doc)  # przed dodaniem treści: pola wypełniane są tylko w szablonie
        body = doc.element.body
        before = list(body)  # trzymamy referencje, więc porównanie obiektów lxml jest stabilne
        render_markdown(doc, source_text, report)
        created = [child for child in body if child not in before and not child.tag.endswith("}sectPr")]
        marker = next((p for p in doc.paragraphs if p.text.strip() == CONTENT_MARKER), None)
        if marker is not None:
            for element in created:
                marker._p.addprevious(element)
            marker._p.getparent().remove(marker._p)
        else:
            report.note(f"Brak znacznika {CONTENT_MARKER} w szablonie: treść dodana na końcu szablonu.")
    else:
        # Kopia szablonu bez treści: zostają wszystkie style, numeracja, motyw, nagłówki, stopki i ustawienia stron.
        doc = Document(str(reference)) if reference is not None else Document()
        table_style = template_table_style(doc)
        if reference is not None:
            clear_body(doc)
        fill(doc)  # nagłówki i stopki szablonu
        render_markdown(doc, source_text, report, table_style)
    if template is not None or reference is not None:
        headings = [s.name for s in (style_or_none(doc, f"Heading {n}") for n in (1, 2, 3)) if s is not None]
        table = template_table_style(doc)
        report.note(f"Style szablonu: nagłówki {', '.join(headings) or 'brak'}; tabele {table.name if table else 'brak'}; "
                    f"stylów w dokumencie: {len(doc.styles)}.")
    doc.save(str(output))


# --- Główny przebieg ------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="md-to-docx", description="Markdown → DOCX (lokalnie).")
    parser.add_argument("input_md", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--reference-doc", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--engine", choices=("auto", "pandoc", "python-docx"), default="auto")
    parser.add_argument("--keep-images", action="store_true")
    parser.add_argument("--pdf", action="store_true", help="podgląd PDF przez LibreOffice, gdy jest dostępny")
    parser.add_argument("--set", action="append", default=[], metavar="POLE=WARTOŚĆ",
                        help="wypełnia pole szablonu, np. --set \"[TYTUŁ]=Analiza zmian\" (powtarzalne)")
    return parser.parse_args(argv)


def placeholder_values(items: list[str]) -> dict[str, str]:
    values = {}
    for item in items:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise ValueError(f"--set wymaga postaci POLE=WARTOŚĆ: {item}")
        values[key] = value
    return values


def validate(args: argparse.Namespace) -> str | None:
    if args.input_md.suffix.lower() not in (".md", ".markdown", ".txt"):
        return "plik wejściowy musi mieć rozszerzenie .md"
    if not args.input_md.is_file():
        return f"brak pliku: {args.input_md}"
    if args.output_docx.suffix.lower() != ".docx":
        return "plik wynikowy musi mieć rozszerzenie .docx"
    if args.output_docx.resolve() == args.input_md.resolve():
        return "plik wynikowy nie może nadpisać źródła"
    for option in ("reference_doc", "template"):
        path = getattr(args, option)
        if path is not None and (path.suffix.lower() not in (".docx", ".dotx") or not path.is_file()):
            return f"--{option.replace('_', '-')} wymaga istniejącego pliku .docx lub .dotx"
        if path is not None and path.resolve() == args.output_docx.resolve():
            return "plik wynikowy nie może nadpisać szablonu"
    if args.template is not None and args.reference_doc is not None:
        return "użyj --template albo --reference-doc, nie obu naraz"
    if (args.template is not None or args.set) and args.engine == "pandoc":
        return "--template i --set wymagają silnika python-docx"
    try:
        placeholder_values(args.set)
    except ValueError as error:
        return str(error)
    if not args.output_docx.parent.resolve().is_dir():
        return f"brak katalogu wynikowego: {args.output_docx.parent}"
    return None


def choose_engine(args: argparse.Namespace) -> tuple[str | None, str | None]:
    has_docx = importlib.util.find_spec("docx") is not None
    pandoc = pandoc_path()
    if args.template is not None or args.set or args.engine == "python-docx":
        return ("python-docx", None) if has_docx else (None, None)
    if args.engine == "pandoc":
        return ("pandoc", pandoc) if pandoc else (None, None)
    # Z szablonem dokument powstaje na kopii szablonu: komplet stylów, numeracja, nagłówki, stopki i motyw.
    # Pandoc przejmuje z --reference-doc tylko część stylów, więc jest wtedy drugim wyborem.
    order = ("python-docx", "pandoc") if args.reference_doc is not None else ("pandoc", "python-docx")
    for engine in order:
        if engine == "python-docx" and has_docx:
            return engine, None
        if engine == "pandoc" and pandoc:
            return engine, pandoc
    return None, None


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_STYLE = re.compile(r"(?:heading|nag\w*?)\s*(\d)", re.I)


def markdown_structure(text: str) -> dict[str, int]:
    """Liczba nagłówków, tabel i obrazów w Markdown (poza blokami kodu)."""
    counts = {"nagłówki": 0, "tabele": 0, "obrazy": 0}
    lines, fenced = text.replace("\r\n", "\n").split("\n"), False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if HEADING.match(line):
            counts["nagłówki"] += 1
        if "|" in line and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1]):
            counts["tabele"] += 1
        counts["obrazy"] += sum(1 for m in IMAGE.finditer(line) if not m.group(2).lower().endswith(".svg"))
    return counts


def docx_structure(path: Path) -> tuple[dict[str, int], int]:
    """Liczba nagłówków, tabel i obrazów w DOCX oraz liczba części nagłówków i stopek stron."""
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(path) as archive:
        body = ET.fromstring(archive.read("word/document.xml"))
        parts = sum(1 for n in archive.namelist() if re.match(r"word/(header|footer)\d*\.xml$", n))
    headings = 0
    for paragraph in body.iter(f"{W_NS}p"):
        style = paragraph.find(f"{W_NS}pPr/{W_NS}pStyle")
        if style is not None and HEADING_STYLE.search(style.get(f"{W_NS}val", "")):
            headings += 1
    counts = {"nagłówki": headings, "tabele": sum(1 for _ in body.iter(f"{W_NS}tbl")),
              "obrazy": sum(1 for _ in body.iter(f"{W_NS}drawing"))}
    return counts, parts


def verify_output(text: str, output: Path, template: Path | None, report: Report) -> bool:
    """Ponowne otwarcie wyniku i porównanie struktury z Markdown oraz z szablonem (nagłówki i stopki stron)."""
    try:
        found, parts = docx_structure(output)
    except Exception as error:  # uszkodzony plik wynikowy
        report.warn(f"kontrola DOCX: nie można ponownie otworzyć wyniku: {error}")
        return False
    expected = markdown_structure(text)
    base = {"nagłówki": 0, "tabele": 0, "obrazy": 0}
    template_parts = 0
    if template is not None:
        base, template_parts = docx_structure(template)
    ok = True
    details = []
    for key, value in expected.items():
        # W trybie --template wynik zawiera też elementy szablonu; przy --reference-doc treść szablonu jest usuwana.
        minimum = value + (base[key] if template is not None and key != "nagłówki" else 0)
        status = "PASS" if found[key] >= minimum else "FAIL"
        ok = ok and status == "PASS"
        details.append(f"{key} {found[key]}/{minimum} {status}")
    if template_parts and parts < template_parts:
        ok = False
        details.append(f"nagłówki/stopki stron {parts}/{template_parts} FAIL")
    report.note(f"Kontrola DOCX: {'; '.join(details)} — {'PASS' if ok else 'FAIL'}")
    return ok


def export_pdf(output: Path, report: Report) -> None:
    office = shutil.which("soffice") or shutil.which("libreoffice")
    if office is None:
        report.note("Podgląd PDF: NOT_RUN (brak LibreOffice: soffice). Sprawdź dokument wizualnie w Word.")
        return
    try:
        result = subprocess.run([office, "--headless", "--convert-to", "pdf", "--outdir", str(output.parent), str(output)],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                timeout=RENDER_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        report.warn("podgląd PDF: przekroczono czas (UNKNOWN)")
        return
    pdf = output.with_suffix(".pdf")
    if result.returncode == 0 and pdf.exists():
        report.note(f"Podgląd PDF: PASS — {pdf}")
    else:
        report.warn(f"podgląd PDF: FAIL — {result.stdout.decode('utf-8', 'replace').strip()[-300:]}")


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv)
    problem = validate(args)
    if problem:
        print(f"BŁĄD: {problem}")
        return 1
    engine, pandoc = choose_engine(args)
    if engine is None:
        print("BRAK SILNIKA DOCX: zainstaluj python-docx (pip install python-docx) albo Pandoc "
              "(winget install JohnMacFarlane.Pandoc). Dokument pozostaje w Markdown.")
        return 3
    report = Report()
    report.note(f"Silnik: {engine}")
    source_dir = args.input_md.resolve().parent
    work_dir = Path(tempfile.mkdtemp(prefix="flowkit_md2docx_"))
    images_dir = work_dir / "diagrams"
    images_dir.mkdir()
    try:
        text = args.input_md.read_text(encoding="utf-8-sig")
        text = replace_mermaid(text, images_dir, report)
        text = resolve_images(text, source_dir, images_dir, report)
        reference = as_docx(args.reference_doc, work_dir) if args.reference_doc else None
        template = as_docx(args.template, work_dir) if args.template else None
        output = args.output_docx.resolve()
        if engine == "pandoc":
            rendered = work_dir / "dokument.md"
            rendered.write_text(text, encoding="utf-8")
            convert_pandoc(pandoc, rendered, output, reference, [source_dir, images_dir])
        else:
            convert_python_docx(text, output, reference, template, report, placeholder_values(args.set))
        if args.keep_images and any(images_dir.iterdir()):
            keep = output.with_name(output.stem + "_diagrams")
            shutil.copytree(images_dir, keep, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.mmd"))
            report.note(f"Diagramy zachowane w: {keep}")
        verified = verify_output(text, output, template, report)
        if args.pdf:
            export_pdf(output, report)
    except Exception as error:  # każdy błąd konwersji kończy się czytelnym komunikatem, bez śladu stosu
        print(f"BŁĄD: {error}")
        return 1
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
    print(f"ZAPISANO: {output} (ostrzeżeń: {len(report.warnings)})")
    if not verified:
        print("KONTROLA: FAIL — dokument zapisany, ale jego struktura nie zgadza się ze źródłem; sprawdź go przed oddaniem.")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
