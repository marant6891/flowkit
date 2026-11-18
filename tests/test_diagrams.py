"""Testy Documentation Diagrams Engine i słownika statusów skilla client-pt-prd-writer.
Uruchom: python -m unittest tests/test_diagrams.py
"""
import importlib.util
import re
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "client-pt-prd-writer"
FIXTURES = ROOT / "tests" / "fixtures" / "diagrams"
sys.path.insert(0, str(SKILL / "scripts"))

import check_status_labels as labels  # noqa: E402
import diagram_core as core  # noqa: E402
import generate_diagram as gen  # noqa: E402
import insert_diagrams as ins  # noqa: E402
import validate_diagram as val  # noqa: E402

HAS_DOCX = importlib.util.find_spec("docx") is not None


def fixture(name):
    return core.load_model(next(FIXTURES.glob(f"{name}-*.yaml")))


def tiny_png(path, width=2400, height=1200):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    raw = zlib.compress(b"".join(b"\x00" + b"\xff" * 3 for _ in range(1)))
    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")
    # Deklarowany rozmiar jest podmieniany, bo testy sprawdzają tylko skalowanie w dokumencie.
    png = png[:16] + struct.pack(">II", width, height) + png[24:]
    path.write_bytes(png)


class TestModel(unittest.TestCase):

    def test_all_fixture_models_render_without_issues(self):
        for path in sorted(FIXTURES.glob("D-*.yaml")):
            model = core.load_model(path)
            self.assertEqual(core.validate_model(model), [], path.name)
            canvas, issues = gen.render(model)
            self.assertEqual(issues, [], path.name)
            svg = canvas.to_svg(model)
            self.assertIn('role="img"', svg)
            self.assertIn("<title", svg)
            self.assertIn("<desc", svg)

    def test_skill_template_model_is_valid(self):
        model = core.load_model(SKILL / "templates" / "diagram-model.yaml")
        self.assertEqual(core.validate_model(model), [])
        self.assertEqual(gen.render(model)[1], [])

    def test_every_declared_type_has_a_layout(self):
        declared = {t for types, _ in gen.LAYOUTS for t in types}
        self.assertEqual(declared, core.DIAGRAM_TYPES)

    def test_element_without_source_is_rejected(self):
        model = fixture("D-01")
        del model["nodes"][0]["source"]
        self.assertTrue(any("source" in e for e in core.validate_model(model)))

    def test_unknown_direction_requires_open_item(self):
        model = fixture("D-01")
        model["connections"][0]["direction"] = "unknown"
        self.assertTrue(any("OPEN-NNN" in e for e in core.validate_model(model)))
        model["connections"][0]["source"] = "OPEN-009"
        self.assertEqual(core.validate_model(model), [])

    def test_missing_direction_cannot_hide_as_none(self):
        model = fixture("D-01")
        model["connections"][0]["direction"] = "none"
        self.assertTrue(any("direction: unknown" in e for e in core.validate_model(model)))

    def test_tbd_label_is_rejected(self):
        model = fixture("D-01")
        model["nodes"][0]["label"] = "TBD"
        self.assertTrue(any(core.UNKNOWN in e for e in core.validate_model(model)))

    def test_incomplete_sources_are_marked_and_blocked_in_final_mode(self):
        model = fixture("D-07")
        canvas, issues = gen.render(model)
        self.assertEqual(issues, [])
        self.assertIn('stroke-dasharray="5 4"', canvas.to_svg(model))
        self.assertIn("do potwierdzenia", canvas.to_svg(model))
        self.assertTrue(core.validate_model(model, "final"))

    def test_confirmed_model_is_clean_in_final_mode(self):
        model = fixture("D-01")
        self.assertEqual(core.validate_model(model, "final"), [])
        self.assertNotRegex(gen.render(model)[0].to_svg(model), r"(SRC|OPEN|ASSUMPTION)-\d{3}")

    def test_node_missing_from_document_is_reported(self):
        model = fixture("D-01")
        model["nodes"].append({"id": "x", "label": "Serwer OAuth2", "type": "service", "source": "SRC-001"})
        text = (FIXTURES / "document.md").read_text(encoding="utf-8")
        self.assertTrue(any("Serwer OAuth2" in e for e in val.check_against_document(model, text, "working")))

    def test_oversized_diagram_is_refused_not_degraded(self):
        model = fixture("D-01")
        model["groups"] = []
        model["nodes"] = [{"id": f"n{i}", "label": f"Komponent numer {i}", "type": "service", "source": "SRC-001"}
                          for i in range(12)]
        model["connections"] = []
        _canvas, issues = gen.render(model)
        self.assertTrue(any("podziel" in i for i in issues))

    def test_dense_diagram_with_cycle_and_long_edges_stays_valid(self):
        model = fixture("D-02")
        model["connections"] += [
            {"from": "o", "to": "v", "label": "Ponowna weryfikacja", "source": "SRC-001"},
            {"from": "s", "to": "k", "label": "Wycofanie", "source": "SRC-001"},
        ]
        self.assertEqual(gen.render(model)[1], [])

    def test_themes_and_brand_keep_contrast(self):
        for theme in sorted(core.THEMES):
            model = deepcopy(fixture("D-01"))
            model["output"] = {"theme": theme, "accent": "#FFD9D0"}
            self.assertEqual(val.check_theme(model), [], theme)
            self.assertEqual(gen.render(model)[1], [], theme)


class TestMarkdownIntegration(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.dir = self.tmp / "diagrams"
        for name in ("D-01", "D-02"):
            path = next(FIXTURES.glob(f"{name}-*.yaml"))
            self.assertEqual(gen.generate(path, self.dir, "working", None), [])
        self.doc = self.tmp / "doc.md"
        shutil.copyfile(FIXTURES / "document.md", self.doc)

    def run_insert(self):
        return ins.insert_markdown(self.doc, self.dir, self.doc, ins.load_models(self.dir))

    def test_diagram_follows_first_discussion_with_relative_path(self):
        self.run_insert()
        text = self.doc.read_text(encoding="utf-8")
        self.assertLess(text.index("Portal klienta wywołuje"), text.index("Rysunek 1 przedstawia"))
        self.assertLess(text.index("*Rysunek 1."), text.index("### Odpowiedzialności"))
        self.assertIn("](diagrams/D-01-architecture.svg)", text)
        self.assertNotIn("<svg", text)

    def test_reinsertion_is_idempotent(self):
        self.run_insert()
        first = self.doc.read_bytes()
        self.run_insert()
        self.assertEqual(first, self.doc.read_bytes())

    def test_removing_a_diagram_renumbers_the_rest(self):
        self.run_insert()
        for path in self.dir.glob("D-01-*"):
            path.unlink()
        self.run_insert()
        text = self.doc.read_text(encoding="utf-8")
        self.assertNotIn("D-01-architecture", text)
        self.assertIn("*Rysunek 1. Przebieg obsługi reklamacji", text)

    def test_document_without_diagrams_is_unchanged(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        before = self.doc.read_bytes()
        ins.insert_markdown(self.doc, empty, self.doc, ins.load_models(empty))
        self.assertEqual(before, self.doc.read_bytes())

    def test_missing_section_is_an_error_not_an_append(self):
        model = fixture("D-01")
        model["placement"] = {"section": "Sekcja nieistniejąca"}
        with self.assertRaises(ValueError):
            ins.md_anchor(self.doc.read_text(encoding="utf-8").split("\n"), model)


@unittest.skipUnless(HAS_DOCX, "python-docx niedostępny")
class TestDocxIntegration(unittest.TestCase):

    def setUp(self):
        from docx import Document
        from docx.shared import Cm
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.dir = self.tmp / "diagrams"
        self.dir.mkdir()
        for name in ("D-01", "D-02"):
            path = next(FIXTURES.glob(f"{name}-*.yaml"))
            model = core.load_model(path)
            shutil.copyfile(path, self.dir / f"{gen.base_name(model)}.yaml")
            tiny_png(self.dir / f"{gen.base_name(model)}.png")
        doc = Document()
        section = doc.sections[0]
        section.left_margin = section.right_margin = Cm(4)
        section.header.paragraphs[0].text = "Nagłówek klienta"
        doc.add_heading("2. Architektura rozwiązania", 1)
        doc.add_paragraph("Opis architektury.")
        doc.add_paragraph("Dalszy opis architektury.")
        doc.add_heading("3. Proces reklamacji", 1)
        table = doc.add_table(rows=1, cols=1)
        table.cell(0, 0).text = "Tabela procesu"
        doc.add_heading("4. Integracje", 1)
        self.source = self.tmp / "template.docx"
        doc.save(self.source)
        self.output = self.tmp / "result.docx"

    def insert(self, source=None):
        ins.insert_docx(source or self.source, self.dir, self.output, ins.load_models(self.dir))
        from docx import Document
        return Document(self.output)

    def test_caption_alt_text_and_page_fit(self):
        doc = self.insert()
        from docx.oxml.ns import qn
        texts = ["".join(t.text or "" for t in p._p.iter(qn("w:t"))) for p in doc.paragraphs]
        self.assertLess(texts.index("Opis architektury."), texts.index(next(t for t in texts if t.startswith("Rysunek 1 przedstawia"))))
        self.assertTrue(any(t.startswith("Rysunek 1. Architektura logiczna") for t in texts))
        self.assertEqual(len(doc.inline_shapes), 2)
        section = doc.sections[0]
        usable = section.page_width - section.left_margin - section.right_margin
        for shape in doc.inline_shapes:
            self.assertLessEqual(shape.width, usable)
            self.assertAlmostEqual(shape.width / shape.height, 2.0, places=2)
            self.assertTrue(shape._inline.docPr.get("descr"))

    def test_diagram_is_placed_after_table_in_section(self):
        doc = self.insert()
        tags = [el.tag.split("}")[1] for el in doc.element.body.iterchildren()]
        self.assertEqual(tags[tags.index("tbl") + 1], "p")
        following = doc.element.body[tags.index("tbl") + 1]
        self.assertIn("Rysunek 2 przedstawia", "".join(following.itertext()))

    def test_template_styles_header_and_section_are_preserved(self):
        import zipfile
        doc = self.insert()
        self.assertEqual(doc.sections[0].header.paragraphs[0].text, "Nagłówek klienta")
        with zipfile.ZipFile(self.source) as a, zipfile.ZipFile(self.output) as b:
            self.assertEqual(a.read("word/styles.xml"), b.read("word/styles.xml"))

    def test_brand_uses_font_of_normal_style(self):
        from docx import Document
        doc = Document(self.source)
        doc.styles["Normal"].font.name = "Calibri"
        doc.save(self.source)
        self.assertEqual(gen.brand_from_template(self.source)["font"], "Calibri")

    def test_regeneration_replaces_instead_of_duplicating(self):
        self.insert()
        doc = self.insert(self.output)
        self.assertEqual(len(doc.inline_shapes), 2)
        self.assertEqual(sum(p.text.startswith("Rysunek 1 przedstawia") for p in doc.paragraphs), 1)


class TestStatusVocabulary(unittest.TestCase):

    def test_moscow_is_translated(self):
        self.assertEqual(labels.lookup("Must"), "Wymagane")
        self.assertEqual(labels.lookup(" **Should have** "), "Zalecane")
        self.assertEqual(labels.lookup("Could"), "Opcjonalne")
        self.assertEqual(labels.lookup("Won't"), "Wyłączone z zakresu")

    def test_only_whole_cells_are_flagged(self):
        self.assertIsNone(labels.lookup("System must be open"))
        self.assertIsNone(labels.lookup("Wymagane"))

    def test_markdown_tables_are_checked_but_code_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "d.md"
            path.write_text("| ID | Priority | Status |\n|---|---|---|\n| FR-001 | Must | In Progress |\n\n"
                            "```\n| x | Must |\n```\n\nThe word Must w zdaniu.\n", encoding="utf-8")
            issues = labels.find_issues(path)
        self.assertEqual(len(issues), 3)

    def test_reference_lists_every_polish_term(self):
        reference = (SKILL / "references" / "status-vocabulary.md").read_text(encoding="utf-8")
        for polish in set(labels.TERMS.values()):
            self.assertIn(polish, reference, polish)

    def test_skill_links_new_references(self):
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in ("status-vocabulary.md", "diagram-engine.md", "diagram-selection.md", "diagram-design-system.md"):
            self.assertIn(name, content)
        self.assertTrue(re.search(r"diagram-quality-checklist\.md", content))


if __name__ == "__main__":
    unittest.main()
