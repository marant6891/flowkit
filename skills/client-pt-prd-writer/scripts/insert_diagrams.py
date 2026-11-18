"""Osadza diagramy we właściwych sekcjach dokumentu DOCX lub Markdown.

Użycie:
  python insert_diagrams.py dokument.docx --diagrams diagrams/ --output wynik.docx

Skrypt jest idempotentny: usuwa wcześniej osadzone diagramy, wstawia aktualne i numeruje
je według kolejności w dokumencie. Dzięki temu pojedynczy diagram można wygenerować
ponownie bez przebudowy całego dokumentu. Miejsce wskazuje znacznik [[DIAGRAM:D-01]]
albo pole placement.section w modelu. Brak sekcji jest błędem: diagram nigdy nie trafia
na koniec dokumentu.

Kody wyjścia: 0 = sukces, 1 = błąd danych, 3 = brak python-docx lub pliku PNG.
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_core import load_model  # noqa: E402
from export_diagram import PNG_SCALE  # noqa: E402
from generate_diagram import base_name  # noqa: E402

FIGURE = "Rysunek"
BOOKMARK_PREFIX = "_fk"
MAX_PAGE_HEIGHT_SHARE = 0.72
EMU_PER_PX = 9525


def norm_heading(text: str) -> str:
    text = re.sub(r"^\s*\d+(\.\d+)*\.?\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).casefold()


def load_models(directory: Path) -> list[dict]:
    models = [load_model(p) for p in sorted(directory.glob("D-*.yaml"))]
    ids = [m["id"] for m in models]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise ValueError(f"powielone identyfikatory diagramów: {', '.join(sorted(duplicates))}")
    return models


def target_section(model: dict) -> str:
    placement = model.get("placement") or {}
    return str(placement.get("section") or model["source"]["section"])


def intro_text(model: dict, number: int) -> str:
    return f"{FIGURE} {number} przedstawia {str(model['explanation']).rstrip('.')}."


def caption_text(model: dict, number: int) -> str:
    return f"{FIGURE} {number}. {str(model['caption']).rstrip('.')}."


# --- Markdown -----------------------------------------------------------------

MD_BLOCK = re.compile(
    rf"(?:^{FIGURE} \d+ przedstawia [^\n]*\n\n)?^!\[[^\]]*\]\([^)\n]*D-\d{{2,3}}-[^)\n]*\.svg\)\n\n"
    rf"^\*{FIGURE} \d+\. [^\n]*\*\n\n?",
    re.MULTILINE,
)


def md_anchor(lines: list[str], model: dict) -> tuple[int, bool]:
    """Zwraca (indeks linii, czy linia jest znacznikiem do zastąpienia)."""
    marker = f"[[DIAGRAM:{model['id']}]]"
    fenced = False
    wanted = norm_heading(target_section(model))
    heading = None
    for i, line in enumerate(lines):
        if line.strip() == marker:
            return i, True
        if line.lstrip().startswith("```"):
            fenced = not fenced
        match = re.match(r"^#{1,6}\s+(.*?)\s*#*$", line)
        if not fenced and heading is None and match and norm_heading(match.group(1)) == wanted:
            heading = i
    if heading is None:
        raise ValueError(f"{model['id']}: nie znaleziono sekcji '{target_section(model)}'")
    i = heading + 1
    if (model.get("placement") or {}).get("position") == "after-heading":
        return i, False
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and re.match(r"^#{1,6}\s", lines[i]):
        return heading + 1, False
    while i < len(lines) and lines[i].strip():
        i += 1
    return i, False


def insert_markdown(document: Path, directory: Path, output: Path, models: list[dict]) -> list[str]:
    raw = document.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = MD_BLOCK.sub("", raw.replace("\r\n", "\n"))
    lines = text.split("\n")
    placed = sorted(((*md_anchor(lines, m), m["id"], m) for m in models), key=lambda item: (item[0], item[2]))
    blocks = []
    for number, (index, is_marker, _id, model) in enumerate(placed, 1):
        svg = directory / f"{base_name(model)}.svg"
        if not svg.exists():
            raise ValueError(f"{model['id']}: brak pliku {svg.name}")
        rel = Path(os.path.relpath(svg, output.parent)).as_posix()
        alt = str(model["alt"]).replace("[", "(").replace("]", ")")
        block = ["", intro_text(model, number), "", f"![{alt}]({rel})", "", f"*{caption_text(model, number)}*", ""]
        blocks.append((index, is_marker, block))
    for index, is_marker, block in reversed(blocks):
        lines[index:index + (1 if is_marker else 0)] = block
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    output.write_bytes(result.replace("\n", eol).encode("utf-8"))
    return [m["id"] for *_, m in placed]


# --- DOCX ----------------------------------------------------------------------

def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} nie jest plikiem PNG")
    return struct.unpack(">II", header[16:24])


def insert_docx(document: Path, directory: Path, output: Path, models: list[dict]) -> list[str]:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.section import Section
    from docx.shared import Emu
    from docx.text.paragraph import Paragraph

    doc = Document(str(document))
    body = doc.element.body

    for paragraph in list(body.iterchildren(qn("w:p"))):
        names = [b.get(qn("w:name"), "") for b in paragraph.iter(qn("w:bookmarkStart"))]
        if any(n.startswith(BOOKMARK_PREFIX) for n in names):
            body.remove(paragraph)

    blocks = [el for el in body.iterchildren() if el.tag in (qn("w:p"), qn("w:tbl"))]

    def is_heading(element) -> bool:
        if element.tag != qn("w:p"):
            return False
        style = Paragraph(element, doc._body).style
        name = (style.name or "").casefold() if style is not None else ""
        return name.startswith(("heading", "nagłówek", "title", "tytuł"))

    def anchor_for(model: dict):
        marker = f"[[DIAGRAM:{model['id']}]]"
        wanted = norm_heading(target_section(model))
        heading = None
        for i, element in enumerate(blocks):
            if element.tag != qn("w:p"):
                continue
            text = Paragraph(element, doc._body).text
            if text.strip() == marker:
                return i, element, True
            if heading is None and is_heading(element) and norm_heading(text) == wanted:
                heading = i
        if heading is None:
            raise ValueError(f"{model['id']}: nie znaleziono sekcji '{target_section(model)}'")
        following = blocks[heading + 1] if heading + 1 < len(blocks) else None
        after_heading = (model.get("placement") or {}).get("position") == "after-heading"
        if after_heading or following is None or is_heading(following):
            return heading, blocks[heading], False
        return heading + 1, following, False

    def section_of(element) -> Section:
        for sibling in element.itersiblings():
            if sibling.tag == qn("w:p"):
                found = sibling.find(f"{qn('w:pPr')}/{qn('w:sectPr')}")
                if found is not None:
                    return Section(found, doc.part)
        return Section(body.find(qn("w:sectPr")), doc.part)

    caption_style = next((s for s in doc.styles if s.type == 1 and (s.name or "").casefold() in ("caption", "legenda")), None)
    next_id = max([int(b.get(qn("w:id"), 0)) for b in body.iter(qn("w:bookmarkStart"))] + [9000]) + 1

    def bookmark(paragraph, name: str) -> None:
        nonlocal next_id
        start = OxmlElement("w:bookmarkStart")
        start.set(qn("w:id"), str(next_id))
        start.set(qn("w:name"), name)
        end = OxmlElement("w:bookmarkEnd")
        end.set(qn("w:id"), str(next_id))
        paragraph._p.append(start)
        paragraph._p.append(end)
        next_id += 1

    placed = sorted(((*anchor_for(m), m) for m in models), key=lambda item: (item[0], item[3]["id"]))
    tail: dict[int, object] = {}
    for number, (position, element, is_marker, model) in enumerate(placed, 1):
        png = directory / f"{base_name(model)}.png"
        if not png.exists():
            raise FileNotFoundError(f"{model['id']}: brak pliku {png.name}; uruchom export_diagram.py")
        anchor = tail.get(id(element), element)
        key = re.sub(r"\W", "", model["id"])

        def new_paragraph(after):
            created = OxmlElement("w:p")
            after.addnext(created)
            return Paragraph(created, doc._body)

        intro = new_paragraph(anchor)
        intro.add_run(intro_text(model, number))
        bookmark(intro, f"{BOOKMARK_PREFIX}{key}i")
        intro.paragraph_format.keep_with_next = True

        figure = new_paragraph(intro._p)
        figure.alignment = WD_ALIGN_PARAGRAPH.CENTER
        figure.paragraph_format.keep_with_next = True
        section = section_of(figure._p)
        max_w = section.page_width - section.left_margin - section.right_margin
        max_h = int((section.page_height - section.top_margin - section.bottom_margin) * MAX_PAGE_HEIGHT_SHARE)
        px_w, px_h = png_size(png)
        native_w, native_h = px_w / PNG_SCALE * EMU_PER_PX, px_h / PNG_SCALE * EMU_PER_PX
        scale = min(1.0, max_w / native_w, max_h / native_h)
        shape = figure.add_run().add_picture(str(png), width=Emu(int(native_w * scale)), height=Emu(int(native_h * scale)))
        properties = shape._inline.docPr
        properties.set("name", f"{FIGURE} {number}")
        properties.set("title", str(model["title"]))
        properties.set("descr", str(model["alt"]))
        bookmark(figure, f"{BOOKMARK_PREFIX}{key}f")

        caption = new_paragraph(figure._p)
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption_style is not None:
            caption.style = caption_style
        runs = [caption.add_run(f"{FIGURE} ")]
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), f" SEQ {FIGURE} \\* ARABIC ")
        field_run = OxmlElement("w:r")
        field_text = OxmlElement("w:t")
        field_text.text = str(number)
        field_run.append(field_text)
        field.append(field_run)
        caption._p.append(field)
        runs.append(caption.add_run(f". {str(model['caption']).rstrip('.')}."))
        if caption_style is None:
            for run in runs:
                run.italic = True
            properties_run = OxmlElement("w:rPr")
            properties_run.append(OxmlElement("w:i"))
            field_run.insert(0, deepcopy(properties_run))
        bookmark(caption, f"{BOOKMARK_PREFIX}{key}c")

        tail[id(element)] = caption._p
        if is_marker:
            body.remove(element)
            tail[id(caption._p)] = caption._p
    doc.save(str(output))
    return [item[3]["id"] for item in placed]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--diagrams", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    suffix = args.document.suffix.lower()
    try:
        models = load_models(args.diagrams)
        if suffix == ".md":
            placed = insert_markdown(args.document, args.diagrams, args.output, models)
        elif suffix == ".docx":
            placed = insert_docx(args.document, args.diagrams, args.output, models)
        else:
            print(f"BŁĄD: nieobsługiwany format {suffix}")
            return 1
    except ImportError:
        print("BRAK python-docx: zainstaluj pakiet albo oddaj dokument w formacie Markdown.")
        return 3
    except FileNotFoundError as error:
        print(f"BRAK PLIKU: {error}")
        return 3
    except ValueError as error:
        print(f"BŁĄD: {error}")
        return 1
    print(f"OK osadzono {len(placed)}: {', '.join(placed) if placed else 'brak diagramów'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
