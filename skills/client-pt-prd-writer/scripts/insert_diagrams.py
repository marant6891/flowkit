"""Osadza diagramy we właściwych sekcjach dokumentu DOCX, DOTX lub Markdown.

Użycie:
  python insert_diagrams.py dokument.docx --diagrams diagrams/ --output wynik.docx

Skrypt jest idempotentny: usuwa wcześniej osadzone diagramy, wstawia aktualne i numeruje
je według kolejności w dokumencie. Miejsce wskazuje znacznik [[DIAGRAM:D-01]] albo pole
placement.section w modelu. Diagram wstawiony znacznikiem poza sekcją z modelu zostaje
w tym miejscu przy kolejnych uruchomieniach. Aby go przenieść, wstaw nowy znacznik.
Brak sekcji jest błędem: diagram nigdy nie trafia na koniec dokumentu.

Kody wyjścia: 0 = sukces, 1 = błąd danych, 3 = brak python-docx lub pliku PNG.
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_core import load_model  # noqa: E402
from docx_support import open_document  # noqa: E402
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


def remarks_text(model: dict, number: int, mode: str) -> str | None:
    """Uwagi są zwykłym tekstem pod rysunkiem. Wersja końcowa nie zawiera oznaczeń źródeł."""
    items = []
    for remark in model.get("remarks") or []:
        text = str(remark["text"]).rstrip(".")
        refs = remark.get("source")
        refs = [refs] if isinstance(refs, str) else list(refs or [])
        items.append(f"{text} ({', '.join(refs)})" if mode == "working" and refs else text)
    return f"Uwagi do rysunku {number}: {'; '.join(items)}." if items else None


# --- Markdown -----------------------------------------------------------------

MD_BLOCK = re.compile(
    rf"(?:^{FIGURE} \d+ przedstawia [^\n]*\n\n)?^!\[[^\]]*\]\([^)\n]*(D-\d{{2,3}})-[^)\n]*\.svg\)\n\n"
    rf"^\*{FIGURE} \d+\. [^\n]*\*\n\n?(?:^Uwagi do rysunku \d+: [^\n]*\n\n?)?",
    re.MULTILINE,
)
MD_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*$")


def last_heading(lines: list[str]) -> str:
    for line in reversed(lines):
        match = MD_HEADING.match(line)
        if match:
            return match.group(1)
    return ""


def strip_markdown_blocks(text: str) -> tuple[str, dict[str, tuple[int, str]]]:
    """Usuwa osadzone diagramy i zapamiętuje ich dotychczasowe miejsca."""
    kept, cursor, existing = "", 0, {}
    for match in MD_BLOCK.finditer(text):
        kept += text[cursor:match.start()]
        cursor = match.end()
        lines = kept.rstrip("\n").split("\n")
        existing[match.group(1)] = (len(lines), last_heading(lines))
    return kept + text[cursor:], existing


def md_anchor(lines: list[str], model: dict, existing: dict | None = None) -> tuple[int, bool]:
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
        match = MD_HEADING.match(line)
        if not fenced and heading is None and match and norm_heading(match.group(1)) == wanted:
            heading = i
    previous = (existing or {}).get(model["id"])
    if previous and norm_heading(previous[1]) != wanted:
        return previous[0], False
    if heading is None:
        raise ValueError(f"{model['id']}: nie znaleziono sekcji '{target_section(model)}'")
    i = heading + 1
    if (model.get("placement") or {}).get("position") == "after-heading":
        return i, False
    while True:
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines) or MD_HEADING.match(lines[i]):
            return (heading + 1, False) if i == heading + 1 or not any(x.strip() for x in lines[heading + 1:i]) else (last_text(lines, i), False)
        while i < len(lines) and lines[i].strip():
            i += 1
        # Zapowiedź tabeli lub listy pozostaje razem z zapowiadaną treścią.
        if not lines[last_text(lines, i) - 1].rstrip().endswith(":"):
            return i, False


def last_text(lines: list[str], end: int) -> int:
    index = end
    while index > 0 and not lines[index - 1].strip():
        index -= 1
    return index


def insert_markdown(document: Path, directory: Path, output: Path, models: list[dict], mode: str = "working") -> list[str]:
    raw = document.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    text, existing = strip_markdown_blocks(raw.replace("\r\n", "\n"))
    lines = text.split("\n")
    client_numbers = [int(m.group(1)) for line in lines if (m := re.match(rf"^\*?{FIGURE}\s+(\d+)\s*[.:]", line))]
    offset = max(client_numbers, default=0)
    placed = sorted(((*md_anchor(lines, m, existing), m["id"], m) for m in models), key=lambda item: (item[0], item[2]))
    blocks = []
    for own, (index, is_marker, _id, model) in enumerate(placed, 1):
        number = offset + own
        svg = directory / f"{base_name(model)}.svg"
        if not svg.exists():
            raise ValueError(f"{model['id']}: brak pliku {svg.name}")
        rel = Path(os.path.relpath(svg, output.parent)).as_posix()
        alt = str(model["alt"]).replace("[", "(").replace("]", ")")
        block = ["", intro_text(model, number), "", f"![{alt}]({rel})", "", f"*{caption_text(model, number)}*", ""]
        remarks = remarks_text(model, number, mode)
        if remarks:
            block += [remarks, ""]
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


def insert_docx(document: Path, directory: Path, output: Path, models: list[dict], mode: str = "working") -> list[str]:
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.section import Section
    from docx.shared import Emu
    from docx.text.paragraph import Paragraph

    if output.suffix.lower() != ".docx":
        raise ValueError("wynik musi być plikiem .docx")
    doc = open_document(document)
    body = doc.element.body

    def paragraph(element) -> Paragraph:
        return Paragraph(element, doc._body)

    def full_text(element) -> str:
        return "".join(node.text or "" for node in element.iter(qn("w:t")))

    def outline_level(properties) -> bool:
        level = properties.find(qn("w:outlineLvl")) if properties is not None else None
        return level is not None and int(level.get(qn("w:val"), "9")) < 9

    def is_heading(element) -> bool:
        if element.tag != qn("w:p"):
            return False
        if outline_level(element.find(qn("w:pPr"))):
            return True
        style = paragraph(element).style
        for _ in range(10):
            if style is None:
                return False
            if (style.name or "").casefold().startswith(("heading", "nagłówek", "title", "tytuł")):
                return True
            if outline_level(style.element.find(qn("w:pPr"))):
                return True
            style = style.base_style
        return False

    def is_list_item(element) -> bool:
        if element.tag != qn("w:p"):
            return False
        properties = element.find(qn("w:pPr"))
        if properties is not None and properties.find(qn("w:numPr")) is not None:
            return True
        style = paragraph(element).style
        return bool(style is not None and (style.name or "").casefold().startswith(("list", "lista", "akapit z listą")))

    existing: dict[str, tuple[object, str]] = {}
    kept, section_title = None, ""
    for element in list(body.iterchildren()):
        if element.tag not in (qn("w:p"), qn("w:tbl")):
            continue
        names = [b.get(qn("w:name"), "") for b in element.iter(qn("w:bookmarkStart"))]
        own = [n for n in names if n.startswith(BOOKMARK_PREFIX)]
        if own:
            key = re.sub(r"[ifcr]$", "", own[0][len(BOOKMARK_PREFIX):])
            existing.setdefault(key, (kept, section_title))
            body.remove(element)
            continue
        kept = element
        if is_heading(element):
            section_title = full_text(element)

    blocks = [el for el in body.iterchildren() if el.tag in (qn("w:p"), qn("w:tbl"))]
    positions = {id(el): index for index, el in enumerate(blocks)}

    def after_first_block(heading: int) -> int:
        index = heading + 1
        if index >= len(blocks) or is_heading(blocks[index]):
            return heading
        while index + 1 < len(blocks) and not is_heading(blocks[index + 1]):
            current, following = blocks[index], blocks[index + 1]
            announces = current.tag == qn("w:p") and full_text(current).rstrip().endswith(":")
            if announces or (is_list_item(current) and is_list_item(following)):
                index += 1
                continue
            break
        return index

    def anchor_for(model: dict):
        marker = f"[[DIAGRAM:{model['id']}]]"
        wanted = norm_heading(target_section(model))
        heading, fallback = None, None
        for index, element in enumerate(blocks):
            if element.tag != qn("w:p"):
                continue
            text = full_text(element)
            if text.strip() == marker:
                return index, element, True
            if norm_heading(text) == wanted:
                if heading is None and is_heading(element):
                    heading = index
                fallback = index if fallback is None else fallback
        key = re.sub(r"\W", "", model["id"])
        previous = existing.get(key)
        if previous and previous[0] is not None and norm_heading(previous[1]) != wanted and id(previous[0]) in positions:
            return positions[id(previous[0])], previous[0], False
        heading = heading if heading is not None else fallback
        if heading is None:
            raise ValueError(f"{model['id']}: nie znaleziono sekcji '{target_section(model)}'")
        if (model.get("placement") or {}).get("position") == "after-heading":
            return heading, blocks[heading], False
        index = after_first_block(heading)
        return index, blocks[index], False

    def section_of(element) -> Section:
        for sibling in element.itersiblings():
            if sibling.tag == qn("w:p"):
                found = sibling.find(f"{qn('w:pPr')}/{qn('w:sectPr')}")
                if found is not None:
                    return Section(found, doc.part)
        return Section(body.find(qn("w:sectPr")), doc.part)

    def body_style(position: int):
        order = list(range(position, len(blocks))) + list(range(position - 1, -1, -1))
        for index in order:
            element = blocks[index]
            if element.tag == qn("w:p") and full_text(element).strip() and not is_heading(element) and not is_list_item(element):
                return paragraph(element).style
        return None

    def has_sequence(element) -> bool:
        simple = any(f"SEQ {FIGURE}" in (f.get(qn("w:instr")) or "") for f in element.iter(qn("w:fldSimple")))
        return simple or any(f"SEQ {FIGURE}" in (i.text or "") for i in element.iter(qn("w:instrText")))

    def set_sequence_value(element, value: int) -> None:
        for field in element.iter(qn("w:fldSimple")):
            if f"SEQ {FIGURE}" in (field.get(qn("w:instr")) or ""):
                node = next(field.iter(qn("w:t")), None)
                if node is not None:
                    node.text = str(value)
                return
        active, result = False, False
        for run in element.iter(qn("w:r")):
            for child in run:
                if child.tag == qn("w:instrText") and f"SEQ {FIGURE}" in (child.text or ""):
                    active = True
                elif child.tag == qn("w:fldChar") and active:
                    kind = child.get(qn("w:fldCharType"))
                    result = kind == "separate"
                    if kind == "end":
                        return
                elif child.tag == qn("w:t") and result:
                    child.text = str(value)
                    return

    client_sequence = [i for i, el in enumerate(blocks) if el.tag == qn("w:p") and has_sequence(el)]
    client_plain = [int(m.group(1)) for el in blocks if el.tag == qn("w:p") and not has_sequence(el)
                    and (m := re.match(rf"^\s*{FIGURE}\s+(\d+)\s*[.:]", full_text(el)))]
    use_sequence = not client_plain
    offset = max(client_plain, default=0)

    caption_style = next((s for s in doc.styles if s.type == 1 and (s.name or "").casefold() in ("caption", "legenda")), None)
    next_id = max([int(b.get(qn("w:id"), 0)) for b in body.iter(qn("w:bookmarkStart"))] + [9000]) + 1

    def bookmark(target, name: str) -> None:
        nonlocal next_id
        start = OxmlElement("w:bookmarkStart")
        start.set(qn("w:id"), str(next_id))
        start.set(qn("w:name"), name)
        end = OxmlElement("w:bookmarkEnd")
        end.set(qn("w:id"), str(next_id))
        target._p.append(start)
        target._p.append(end)
        next_id += 1

    def new_paragraph(after) -> Paragraph:
        created = OxmlElement("w:p")
        after.addnext(created)
        return paragraph(created)

    placed = sorted(((*anchor_for(m), m) for m in models), key=lambda item: (item[0], item[3]["id"]))
    numbers = {}
    if use_sequence:
        merged = sorted([(i, 0, None) for i in client_sequence] + [(item[0], 1, item[3]["id"]) for item in placed],
                        key=lambda entry: (entry[0], entry[1], entry[2] or ""))
        for value, (index, kind, model_id) in enumerate(merged, 1):
            if kind:
                numbers[model_id] = value
            else:
                set_sequence_value(blocks[index], value)
    else:
        numbers = {item[3]["id"]: offset + own for own, item in enumerate(placed, 1)}

    tail: dict[int, object] = {}
    for position, element, is_marker, model in placed:
        number = numbers[model["id"]]
        png = directory / f"{base_name(model)}.png"
        if not png.exists():
            raise FileNotFoundError(f"{model['id']}: brak pliku {png.name}; uruchom export_diagram.py")
        anchor = tail.get(id(element), element)
        key = re.sub(r"\W", "", model["id"])

        intro = new_paragraph(anchor)
        text_style = body_style(position)
        if text_style is not None:
            intro.style = text_style
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
        if use_sequence:
            field = OxmlElement("w:fldSimple")
            field.set(qn("w:instr"), f" SEQ {FIGURE} \\* ARABIC ")
            field_run = OxmlElement("w:r")
            if caption_style is None:
                run_properties = OxmlElement("w:rPr")
                run_properties.append(OxmlElement("w:i"))
                field_run.append(run_properties)
            field_text = OxmlElement("w:t")
            field_text.text = str(number)
            field_run.append(field_text)
            field.append(field_run)
            caption._p.append(field)
        else:
            runs.append(caption.add_run(str(number)))
        runs.append(caption.add_run(f". {str(model['caption']).rstrip('.')}."))
        if caption_style is None:
            for run in runs:
                run.italic = True
        bookmark(caption, f"{BOOKMARK_PREFIX}{key}c")

        last = caption
        remarks = remarks_text(model, number, mode)
        if remarks:
            caption.paragraph_format.keep_with_next = True
            last = new_paragraph(caption._p)
            if text_style is not None:
                last.style = text_style
            last.add_run(remarks)
            bookmark(last, f"{BOOKMARK_PREFIX}{key}r")

        tail[id(element)] = last._p
        if is_marker:
            body.remove(element)
    doc.save(str(output))
    return [item[3]["id"] for item in placed]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--diagrams", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("working", "final"), default="working")
    args = parser.parse_args()
    suffix = args.document.suffix.lower()
    try:
        models = load_models(args.diagrams)
        if suffix == ".md":
            placed = insert_markdown(args.document, args.diagrams, args.output, models, args.mode)
        elif suffix in (".docx", ".dotx"):
            placed = insert_docx(args.document, args.diagrams, args.output, models, args.mode)
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
